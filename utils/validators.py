import uuid
from typing import Optional
from exceptions import ValidationException

def validate_uuid(uuid_string: str, field_name: str = "ID") -> bool:
    """Validate UUID format"""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        raise ValidationException(f"Invalid {field_name} format: {uuid_string}")

def validate_video_url(url: str) -> bool:
    """Validate video URL format"""
    if not url:
        raise ValidationException("Video URL cannot be empty")
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValidationException("Video URL must be a valid HTTP/HTTPS URL")
    
    # Check for common video extensions
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    if not any(ext in url.lower() for ext in video_extensions):
        # Allow URLs without extensions (like CDN URLs)
        pass
    
    return True

def validate_prompt(prompt: str) -> bool:
    """Validate prompt text"""
    if not prompt or not prompt.strip():
        raise ValidationException("Prompt cannot be empty")
    
    if len(prompt) > 1000:
        raise ValidationException("Prompt too long (max 1000 characters)")
    
    return True

def validate_pipeline_config(config: dict) -> bool:
    """Validate pipeline configuration"""
    if not isinstance(config, dict):
        raise ValidationException("Pipeline config must be a dictionary")
    
    allowed_keys = ['enableRunwayVideo', 'enableFfmpeg', 'enableWhisper', 'enableGpt4', 'customSteps']
    
    for key in config.keys():
        if key not in allowed_keys:
            raise ValidationException(f"Invalid pipeline config key: {key}")
    
    return True 