#!/usr/bin/env python3
"""
Dialect detector training & inference script

Usage examples:
  # Train and save model
  python dialect_detector.py --mode train --dataset_dir dataset/ --out_model model.joblib

  # Predict a single file
  python dialect_detector.py --mode predict --in_file some_audio.wav --in_model model.joblib

What it does:
  - loads audio files from dataset_dir with structure: dataset/<label>/*.wav
  - extracts audio features (MFCCs + deltas + chroma + spectral contrast + tonnetz)
  - optional simple augmentations (time-stretch + pitch-shift)
  - trains a RandomForest classifier with cross-validation and GridSearch
  - saves the trained pipeline (scaler + classifier) and label map

Notes to improve accuracy:
  - Increase dataset size and class balance
  - Use spectrogram/CNN or pretrained audio embeddings (wav2vec2) for much better results
  - Experiment with more augmentations

Dependencies:
  pip install numpy scipy scikit-learn librosa joblib soundfile tqdm

"""

import os
import glob
import argparse
import warnings
from pathlib import Path

import numpy as np
import librosa
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm

warnings.filterwarnings("ignore")


def extract_features(path, sr=22050, n_mfcc=13, duration=None, offset=0.0):
    """Load an audio file and extract a feature vector.

    Returns a 1D numpy array of aggregated features.
    """
    y, sr = librosa.load(path, sr=sr, duration=duration, offset=offset)
    if y.size == 0:
        return None

    # Ensure mono
    if y.ndim > 1:
        y = librosa.to_mono(y)

    # Trim silence
    y, _ = librosa.effects.trim(y)

    # MFCCs (mean + std)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = mfcc.mean(axis=1)
    mfcc_std = mfcc.std(axis=1)

    # Delta MFCCs
    delta = librosa.feature.delta(mfcc)
    delta_mean = delta.mean(axis=1)
    delta_std = delta.std(axis=1)

    # Chroma
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    chroma_std = chroma.std(axis=1)

    # Spectral contrast
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    contrast_mean = contrast.mean(axis=1)
    contrast_std = contrast.std(axis=1)

    # Tonnetz (requires harmonic)
    try:
        y_harmonic = librosa.effects.harmonic(y)
        tonnetz = librosa.feature.tonnetz(y=y_harmonic, sr=sr)
        tonnetz_mean = tonnetz.mean(axis=1)
        tonnetz_std = tonnetz.std(axis=1)
    except Exception:
        tonnetz_mean = np.zeros(6)
        tonnetz_std = np.zeros(6)

    features = np.concatenate([
        mfcc_mean, mfcc_std,
        delta_mean, delta_std,
        chroma_mean, chroma_std,
        contrast_mean, contrast_std,
        tonnetz_mean, tonnetz_std
    ])

    return features


def augment_time_stretch(y, rate=1.1):
    try:
        return librosa.effects.time_stretch(y, rate)
    except Exception:
        return y


def augment_pitch_shift(y, sr, n_steps=2):
    try:
        return librosa.effects.pitch_shift(y, sr, n_steps)
    except Exception:
        return y


def build_dataset(dataset_dir, sr=22050, augment=False, augment_times=2, n_mfcc=13):
    """Walk dataset_dir and extract features and labels.

    dataset_dir/
      american/
        file1.wav
        file2.wav
      british/
        file1.wav
    """
    X = []
    y = []
    p = Path(dataset_dir)
    classes = [d.name for d in p.iterdir() if d.is_dir()]
    classes.sort()

    for label in classes:
        files = list((p / label).glob("*.wav")) + list((p / label).glob("*.mp3"))
        for fpath in tqdm(files, desc=f"Processing {label}"):
            feats = extract_features(str(fpath), sr=sr, n_mfcc=n_mfcc)
            if feats is None:
                continue
            X.append(feats)
            y.append(label)

            if augment:
                # load full waveform for augmentation
                y_orig, _ = librosa.load(str(fpath), sr=sr)
                for i in range(augment_times):
                    # alternate augmentations
                    if i % 2 == 0:
                        y_aug = augment_time_stretch(y_orig, rate=np.random.uniform(0.85, 1.15))
                    else:
                        y_aug = augment_pitch_shift(y_orig, sr, n_steps=np.random.randint(-3, 4))

                    # temporarily save to buffer by computing features from the array
                    try:
                        # compute mfcc etc from y_aug directly (use feature functions that accept y)
                        mfcc = librosa.feature.mfcc(y=y_aug, sr=sr, n_mfcc=n_mfcc)
                        mfcc_mean = mfcc.mean(axis=1)
                        mfcc_std = mfcc.std(axis=1)
                        delta = librosa.feature.delta(mfcc)
                        delta_mean = delta.mean(axis=1)
                        delta_std = delta.std(axis=1)
                        chroma = librosa.feature.chroma_stft(y=y_aug, sr=sr)
                        chroma_mean = chroma.mean(axis=1)
                        chroma_std = chroma.std(axis=1)
                        contrast = librosa.feature.spectral_contrast(y=y_aug, sr=sr)
                        contrast_mean = contrast.mean(axis=1)
                        contrast_std = contrast.std(axis=1)
                        try:
                            y_harmonic = librosa.effects.harmonic(y_aug)
                            tonnetz = librosa.feature.tonnetz(y=y_harmonic, sr=sr)
                            tonnetz_mean = tonnetz.mean(axis=1)
                            tonnetz_std = tonnetz.std(axis=1)
                        except Exception:
                            tonnetz_mean = np.zeros(6)
                            tonnetz_std = np.zeros(6)

                        feats_aug = np.concatenate([
                            mfcc_mean, mfcc_std,
                            delta_mean, delta_std,
                            chroma_mean, chroma_std,
                            contrast_mean, contrast_std,
                            tonnetz_mean, tonnetz_std
                        ])
                        X.append(feats_aug)
                        y.append(label)
                    except Exception:
                        # skip augmentation failure
                        continue

    X = np.array(X)
    y = np.array(y)
    return X, y, classes


def train_and_save(X, y, classes, out_model_path, cv_folds=5, random_state=42):
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # Split hold-out test set
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.15, random_state=random_state, stratify=y_enc
    )

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(random_state=random_state, n_jobs=-1))
    ])

    param_grid = {
        'clf__n_estimators': [100, 300],
        'clf__max_depth': [None, 20, 50]
    }

    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    grid = GridSearchCV(pipe, param_grid, cv=cv, n_jobs=-1, verbose=2)

    print("Starting training with GridSearchCV...")
    grid.fit(X_train, y_train)
    print(f"Best params: {grid.best_params_}")

    best = grid.best_estimator_

    # Evaluate on test set
    y_pred = best.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=le.classes_)
    cm = confusion_matrix(y_test, y_pred)

    print("Test classification report:\n", report)
    print("Confusion matrix:\n", cm)

    # Save pipeline + label encoder
    out = {
        'pipeline': best,
        'label_encoder': le,
        'classes': classes
    }
    joblib.dump(out, out_model_path)
    print(f"Saved trained model to {out_model_path}")

    return out, (X_test, y_test, y_pred)


def predict_file(model_path, file_path):
    obj = joblib.load(model_path)
    pipeline = obj['pipeline']
    le = obj['label_encoder']

    feats = extract_features(file_path)
    if feats is None:
        raise RuntimeError("Could not extract features from input file")

    probs = pipeline.predict_proba([feats])[0]
    pred_idx = np.argmax(probs)
    pred_label = le.inverse_transform([pred_idx])[0]

    # Return sorted probabilities
    prob_map = {le.inverse_transform([i])[0]: float(probs[i]) for i in range(len(probs))}
    return pred_label, prob_map


def parse_args():
    parser = argparse.ArgumentParser(description="Train or run dialect detector")
    parser.add_argument('--mode', type=str, choices=['train', 'predict'], required=True)
    parser.add_argument('--dataset_dir', type=str, help='Path to dataset root')
    parser.add_argument('--out_model', type=str, default='dialect_model.joblib')
    parser.add_argument('--in_model', type=str, help='Path to trained model (for predict)')
    parser.add_argument('--in_file', type=str, help='Input audio file (for predict)')
    parser.add_argument('--augment', action='store_true', help='Use simple augmentation during training')
    parser.add_argument('--augment_times', type=int, default=2, help='Augmentations per file')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode == 'train':
        if not args.dataset_dir:
            raise ValueError('dataset_dir required for training')
        X, y, classes = build_dataset(args.dataset_dir, augment=args.augment, augment_times=args.augment_times)
        print(f"Built dataset: X={X.shape}, y={y.shape}, classes={classes}")
        train_and_save(X, y, classes, args.out_model)

    elif args.mode == 'predict':
        if not args.in_model or not args.in_file:
            raise ValueError('in_model and in_file are required for predict mode')
        pred_label, prob_map = predict_file(args.in_model, args.in_file)
        print(f"Predicted dialect: {pred_label}")
        print("Probabilities:")
        for k, v in sorted(prob_map.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v:.4f}")


if __name__ == '__main__':
    main()

