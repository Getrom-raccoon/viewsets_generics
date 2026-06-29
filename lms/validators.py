import re
from rest_framework import serializers


def validate_youtube_url(value):
    """
    Валидатор: ссылка должна вести на youtube.com или youtu.be.
    Если поле пустое, пропускаем (разрешено).
    """
    if not value:
        return value
    # Регулярное выражение для youtube
    pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'
    if not re.match(pattern, value):
        raise serializers.ValidationError('Ссылка должна вести на youtube.com или youtu.be')
    return value