import pytest
import asyncio
from unittest.mock import Mock, patch
from services.runway_service import RunwayService
from services.ffmpeg_service import FFmpegService
from services.whisper_service import WhisperService
from services.gpt4_service import GPT4Service

class TestRunwayService:
    """RunwayService testleri"""
    
    @pytest.fixture
    def runway_service(self):
        return RunwayService()
    
    @pytest.mark.asyncio
    async def test_process_video_success(self, runway_service):
        """Başarılı video işleme testi"""
        with patch.object(runway_service.client, 'text_to_image') as mock_client:
            mock_task = Mock()
            mock_task.output = ["https://example.com/output.mp4"]
            mock_client.create.return_value.wait_for_task_output.return_value = mock_task
            
            result = await runway_service.process_video(
                video_url="https://example.com/input.mp4",
                prompt="Transform to sci-fi",
                pipeline_id="test-pipeline"
            )
            
            assert result is not None
            assert result["status"] == "success"
            assert "video_url" in result
    
    @pytest.mark.asyncio
    async def test_process_video_failure(self, runway_service):
        """Başarısız video işleme testi"""
        with patch.object(runway_service.client, 'text_to_image') as mock_client:
            mock_client.create.side_effect = Exception("API Error")
            
            result = await runway_service.process_video(
                video_url="https://example.com/input.mp4",
                prompt="Transform to sci-fi",
                pipeline_id="test-pipeline"
            )
            
            assert result is not None
            assert result["status"] == "failed"
            assert "error" in result

class TestFFmpegService:
    """FFmpegService testleri"""
    
    @pytest.fixture
    def ffmpeg_service(self):
        return FFmpegService()
    
    @pytest.mark.asyncio
    async def test_process_video_success(self, ffmpeg_service):
        """Başarılı video işleme testi"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"", b"")
            mock_subprocess.return_value = mock_process
            
            result = await ffmpeg_service.process_video(
                input_url="https://example.com/input.mp4",
                pipeline_id="test-pipeline"
            )
            
            assert result is not None
            assert result["status"] == "success"
            assert "processed_video" in result
    
    @pytest.mark.asyncio
    async def test_extract_audio_success(self, ffmpeg_service):
        """Başarılı ses çıkarma testi"""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"", b"")
            mock_subprocess.return_value = mock_process
            
            result = await ffmpeg_service.extract_audio(
                video_url="https://example.com/video.mp4",
                pipeline_id="test-pipeline"
            )
            
            assert result is not None
            assert result["status"] == "success"
            assert "audio_file" in result

class TestWhisperService:
    """WhisperService testleri"""
    
    @pytest.fixture
    def whisper_service(self):
        return WhisperService()
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, whisper_service):
        """Başarılı ses transkripsiyonu testi"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"text": "This is a test transcript"}
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await whisper_service.transcribe_audio(
                audio_url="https://example.com/audio.mp3",
                pipeline_id="test-pipeline"
            )
            
            assert result is not None
            assert result["status"] == "success"
            assert "transcript" in result

class TestGPT4Service:
    """GPT4Service testleri"""
    
    @pytest.fixture
    def gpt4_service(self):
        return GPT4Service()
    
    @pytest.mark.asyncio
    async def test_analyze_content_success(self, gpt4_service):
        """Başarılı içerik analizi testi"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Analysis result"}}]
            }
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await gpt4_service.analyze_content(
                content="Test content",
                pipeline_id="test-pipeline"
            )
            
            assert result is not None
            assert result["status"] == "success"
            assert "analysis" in result 