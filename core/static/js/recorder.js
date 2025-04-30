var context, analyser, src, array, logo, mediaRecorder, voice, loopID, audioBlob, fd;

voice = [];
loopID = undefined;

var btnStart = document.querySelector('button[name="record"]');
var btnStop = document.querySelector('button[name="stop"]');
var audio = document.querySelector('#audio');

logo = document.getElementById("logo").style;

function startRecording(){
    event.preventDefault();

    btnStart.disabled = true;

    context = new AudioContext();
    analyser = context.createAnalyser();

    navigator.mediaDevices.getUserMedia({
        audio: true
    }).then(stream => {
        src = context.createMediaStreamSource(stream);
        src.connect(analyser);
        loop();

        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        mediaRecorder.addEventListener('dataavailable', (e) => {
            voice.push(e.data);
        })

        mediaRecorder.addEventListener("stop", function() {
            audioBlob = new Blob(voice, {
                type: 'audio/mp3'
            });

            audioFile = new File([audioBlob], 'audio.mp3', {
                type: 'audio/mp3'
            });
            
            var dt = new DataTransfer();
            dt.items.add(audioFile);
            var file_list = dt.files;
            audio.files = file_list;

            fd = new FormData($('form')[0]);
            fd.append('audio', audioFile);

            voice = [];
        });
    });
    console.log("ok");
}

function stopRecording(){
    event.preventDefault();
    mediaRecorder.stop();
    if(loopID){
        window.cancelAnimationFrame(loopID);
        loopID = undefined;
    }
    logo.minHeight = "30px";
    logo.width = "30px";

    btnStart.disabled = false;
}

btnStart.addEventListener('click', startRecording);
btnStop.addEventListener('click', stopRecording);

function loop() {
    loopID = window.requestAnimationFrame(loop);
    array = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(array);

    logo.minHeight = (array[40] / 3)+"px";
    logo.width = (array[40] / 3)+"px";
}
