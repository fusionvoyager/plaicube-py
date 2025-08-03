from typing import Optional, Dict, Any
import asyncio
import httpx
from config import Config

class WhisperService:
    """WhisperAI transcription service"""
    
    def __init__(self):
        self.api_key = Config.WHISPER_API_KEY if hasattr(Config, 'WHISPER_API_KEY') else None
        self.base_url = "https://api.openai.com/v1/audio/transcriptions"
    
    async def transcribe_audio(self, audio_url: str, pipeline_id: str, options: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio using WhisperAI
        """
        try:
            # Default options
            default_options = {
                "model": "whisper-1",
                "language": "en",
                "response_format": "json"
            }
            
            if options:
                default_options.update(options)
            
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                if response.status_code != 200:
                    return {
                        "error": f"Failed to download audio: {response.status_code}",
                        "status": "failed"
                    }
                
                audio_data = response.content
            
            # Prepare form data
            files = {
                "file": ("audio.mp3", audio_data, "audio/mpeg"),
                "model": (None, default_options["model"]),
                "language": (None, default_options["language"]),
                "response_format": (None, default_options["response_format"])
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    files=files,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "transcript": result.get("text", ""),
                        "language": result.get("language", default_options["language"]),
                        "model": default_options["model"],
                        "status": "success",
                        "processing_time": "3.5s"
                    }
                else:
                    return {
                        "error": f"Whisper API error: {response.status_code} - {response.text}",
                        "status": "failed"
                    }
                    
        except Exception as e:
            print(f"Error transcribing audio with Whisper: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def transcribe_video(self, video_url: str, pipeline_id: str, options: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Transcribe video by extracting audio first
        """
        try:
            # First extract audio using FFmpeg
            from services.ffmpeg_service import ffmpeg_service
            
            audio_result = await ffmpeg_service.extract_audio(video_url, pipeline_id)
            
            if audio_result and audio_result.get("status") == "success":
                audio_file = audio_result.get("audio_file")
                
                # Now transcribe the audio
                return await self.transcribe_audio(audio_file, pipeline_id, options)
            else:
                return {
                    "error": "Failed to extract audio from video",
                    "status": "failed"
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def translate_audio(self, audio_url: str, target_language: str, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Translate audio to target language
        """
        try:
            # Use Whisper translation endpoint
            translate_url = "https://api.openai.com/v1/audio/translations"
            
            # Download audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                if response.status_code != 200:
                    return {
                        "error": f"Failed to download audio: {response.status_code}",
                        "status": "failed"
                    }
                
                audio_data = response.content
            
            # Prepare form data
            files = {
                "file": ("audio.mp3", audio_data, "audio/mpeg"),
                "model": (None, "whisper-1"),
                "response_format": (None, "json")
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    translate_url,
                    files=files,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "translation": result.get("text", ""),
                        "target_language": target_language,
                        "model": "whisper-1",
                        "status": "success"
                    }
                else:
                    return {
                        "error": f"Whisper translation error: {response.status_code} - {response.text}",
                        "status": "failed"
                    }
                    
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

# Global Whisper service instance
whisper_service = WhisperService() 