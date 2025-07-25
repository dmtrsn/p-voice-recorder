import os
from django.core.exceptions import ValidationError
from django.conf import settings

def load_regions():
    path = os.path.join(settings.BASE_DIR, 'regions.txt')
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []
    
def validate_region(value):
    whitelist = load_regions()
    if value not in whitelist:
        raise ValidationError(f'"{value}" Ваш регион не найден.')