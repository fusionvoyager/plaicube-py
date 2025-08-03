from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import uuid
from models import (
    Pipeline, PipelineStep, StepType, StepStatus, PipelineStatus,
    PipelineConfig
)
from config import Config
from services.runway_service import runway_service
# from services.ffmpeg_service import ffmpeg_service
# from services.whisper_service import whisper_service
# from services.gpt4_service import gpt4_service
from utils.logger import logger
from exceptions import PipelineException, ServiceException

class PipelineManager:
    """Pipeline yönetimi için manager sınıfı"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.running_pipelines: Dict[str, asyncio.Task] = {}
    
    def create_pipeline(self, video_id: str, video_url: str, prompt: str, 
                       config: Optional[PipelineConfig] = None) -> Pipeline:
        """Yeni pipeline oluştur"""
        
        if config is None:
            config = PipelineConfig()
        
        # Şimdilik sadece Runway aktif, diğerleri devre dışı
        config.enableFfmpeg = False
        config.enableWhisper = False
        config.enableGpt4 = False
        
        pipeline_id = str(uuid.uuid4())
        steps = self._create_steps(config)
        
        pipeline = Pipeline(
            pipelineId=pipeline_id,
            videoId=video_id,
            videoUrl=video_url,
            prompt=prompt,
            status=PipelineStatus.PENDING,
            steps=steps,
            createdAt=datetime.now(),
            totalSteps=len(steps),
            completedSteps=0
        )
        
        self.pipelines[pipeline_id] = pipeline
        logger.info(f"Pipeline created", pipeline_id=pipeline_id, video_id=video_id, total_steps=len(steps))
        return pipeline
    
    def _create_steps(self, config: PipelineConfig) -> List[PipelineStep]:
        """Pipeline adımlarını oluştur"""
        steps = []
        order = 0
        
        # Runway Video Step
        if config.enableRunwayVideo:
            steps.append(PipelineStep(
                stepId=str(uuid.uuid4()),
                stepType=StepType.RUNWAY_VIDEO,
                status=StepStatus.PENDING,
                order=order,
                input={},
                progress=0
            ))
            order += 1
        
        # FFmpeg Step (devre dışı)
        if config.enableFfmpeg:
            steps.append(PipelineStep(
                stepId=str(uuid.uuid4()),
                stepType=StepType.FFMPEG_PROCESS,
                status=StepStatus.PENDING,
                order=order,
                input={},
                progress=0
            ))
            order += 1
        
        # Whisper Step (devre dışı)
        if config.enableWhisper:
            steps.append(PipelineStep(
                stepId=str(uuid.uuid4()),
                stepType=StepType.WHISPER_TRANSCRIBE,
                status=StepStatus.PENDING,
                order=order,
                input={},
                progress=0
            ))
            order += 1
        
        # GPT4 Step (devre dışı)
        if config.enableGpt4:
            steps.append(PipelineStep(
                stepId=str(uuid.uuid4()),
                stepType=StepType.GPT4_ANALYSIS,
                status=StepStatus.PENDING,
                order=order,
                input={},
                progress=0
            ))
            order += 1
        
        # Custom Steps
        for custom_step in config.customSteps:
            steps.append(PipelineStep(
                stepId=str(uuid.uuid4()),
                stepType=StepType.CUSTOM_PROCESS,
                status=StepStatus.PENDING,
                order=order,
                input=custom_step,
                progress=0
            ))
            order += 1
        
        return steps
    
    async def start_pipeline(self, pipeline_id: str) -> None:
        """Pipeline'ı başlat"""
        if pipeline_id not in self.pipelines:
            raise PipelineException(f"Pipeline {pipeline_id} not found")
        
        pipeline = self.pipelines[pipeline_id]
        pipeline.status = PipelineStatus.PROCESSING
        pipeline.updatedAt = datetime.now()
        
        logger.pipeline_start(pipeline_id, pipeline.videoId)
        
        # Background task oluştur
        task = asyncio.create_task(self._execute_pipeline(pipeline_id))
        self.running_pipelines[pipeline_id] = task
    
    async def _execute_pipeline(self, pipeline_id: str) -> None:
        """Pipeline'ı çalıştır"""
        pipeline = self.pipelines[pipeline_id]
        
        try:
            for step in pipeline.steps:
                if pipeline.status == PipelineStatus.CANCELLED:
                    logger.info(f"Pipeline cancelled, stopping execution", pipeline_id=pipeline_id)
                    break
                
                await self._execute_step(pipeline_id, step)
                
                if step.status == StepStatus.FAILED:
                    pipeline.status = PipelineStatus.FAILED
                    logger.error(f"Pipeline failed due to step failure", pipeline_id=pipeline_id, step_id=step.stepId)
                    break
                elif step.status == StepStatus.COMPLETED:
                    pipeline.completedSteps += 1
            
            # Pipeline tamamlandı
            if pipeline.status != PipelineStatus.FAILED:
                pipeline.status = PipelineStatus.COMPLETED
                pipeline.completedAt = datetime.now()
                logger.pipeline_complete(pipeline_id, "completed")
            
            pipeline.updatedAt = datetime.now()
            
        except Exception as e:
            pipeline.status = PipelineStatus.FAILED
            pipeline.updatedAt = datetime.now()
            logger.error(f"Pipeline execution failed", pipeline_id=pipeline_id, error=str(e))
            raise PipelineException(f"Pipeline {pipeline_id} failed: {str(e)}")
        
        finally:
            # Cleanup
            if pipeline_id in self.running_pipelines:
                del self.running_pipelines[pipeline_id]
    
    async def _execute_step(self, pipeline_id: str, step: PipelineStep) -> None:
        """Tek bir adımı çalıştır"""
        step.status = StepStatus.PROCESSING
        step.startedAt = datetime.now()
        step.progress = 10
        
        logger.step_start(step.stepId, step.stepType, pipeline_id)
        
        try:
            if step.stepType == StepType.RUNWAY_VIDEO:
                await self._execute_runway_step(pipeline_id, step)
            elif step.stepType == StepType.FFMPEG_PROCESS:
                # FFmpeg devre dışı - placeholder
                await self._execute_ffmpeg_step_placeholder(pipeline_id, step)
            elif step.stepType == StepType.WHISPER_TRANSCRIBE:
                # Whisper devre dışı - placeholder
                await self._execute_whisper_step_placeholder(pipeline_id, step)
            elif step.stepType == StepType.GPT4_ANALYSIS:
                # GPT4 devre dışı - placeholder
                await self._execute_gpt4_step_placeholder(pipeline_id, step)
            elif step.stepType == StepType.CUSTOM_PROCESS:
                await self._execute_custom_step(pipeline_id, step)
            else:
                step.status = StepStatus.SKIPPED
                step.progress = 100
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.progress = 0
            logger.service_error(step.stepType, str(e), pipeline_id)
            raise ServiceException(f"Step {step.stepId} failed: {str(e)}")
        
        finally:
            step.completedAt = datetime.now()
            if step.status == StepStatus.PROCESSING:
                step.status = StepStatus.COMPLETED
                step.progress = 100
            
            logger.step_complete(step.stepId, step.status, pipeline_id)
    
    async def _execute_runway_step(self, pipeline_id: str, step: PipelineStep) -> None:
        """Runway video adımını çalıştır"""
        pipeline = self.pipelines[pipeline_id]
        
        # Runway service kullan
        result = await runway_service.process_video(
            video_url=pipeline.videoUrl,
            prompt=pipeline.prompt,
            pipeline_id=pipeline_id
        )
        
        if result and result.get("status") == "success":
            step.output = result
        else:
            step.status = StepStatus.FAILED
            step.error = result.get("error", "Unknown error") if result else "No result"
            raise ServiceException(f"Runway service failed: {step.error}")
    
    async def _execute_ffmpeg_step_placeholder(self, pipeline_id: str, step: PipelineStep) -> None:
        """FFmpeg adımı placeholder (devre dışı)"""
        step.status = StepStatus.SKIPPED
        step.error = "FFmpeg service is currently disabled"
        logger.warning(f"FFmpeg step skipped - service disabled", pipeline_id=pipeline_id)
    
    async def _execute_whisper_step_placeholder(self, pipeline_id: str, step: PipelineStep) -> None:
        """Whisper adımı placeholder (devre dışı)"""
        step.status = StepStatus.SKIPPED
        step.error = "Whisper service is currently disabled"
        logger.warning(f"Whisper step skipped - service disabled", pipeline_id=pipeline_id)
    
    async def _execute_gpt4_step_placeholder(self, pipeline_id: str, step: PipelineStep) -> None:
        """GPT4 adımı placeholder (devre dışı)"""
        step.status = StepStatus.SKIPPED
        step.error = "GPT4 service is currently disabled"
        logger.warning(f"GPT4 step skipped - service disabled", pipeline_id=pipeline_id)
    
    async def _execute_custom_step(self, pipeline_id: str, step: PipelineStep) -> None:
        """Custom adımını çalıştır"""
        # Custom işlem burada yapılacak
        await asyncio.sleep(1)
        
        step.output = {
            "custom_result": "Custom processing result...",
            "step_data": step.input,
            "status": "success"
        }
    
    def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        """Pipeline'ı getir"""
        return self.pipelines.get(pipeline_id)
    
    def get_all_pipelines(self) -> List[Pipeline]:
        """Tüm pipeline'ları getir"""
        return list(self.pipelines.values())
    
    def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Pipeline'ı iptal et"""
        if pipeline_id not in self.pipelines:
            return False
        
        pipeline = self.pipelines[pipeline_id]
        pipeline.status = PipelineStatus.CANCELLED
        pipeline.updatedAt = datetime.now()
        
        logger.info(f"Pipeline cancelled", pipeline_id=pipeline_id)
        
        # Running task'ı iptal et
        if pipeline_id in self.running_pipelines:
            self.running_pipelines[pipeline_id].cancel()
            del self.running_pipelines[pipeline_id]
        
        return True
    
    def delete_pipeline(self, pipeline_id: str) -> bool:
        """Pipeline'ı sil"""
        if pipeline_id not in self.pipelines:
            return False
        
        # Running task'ı iptal et
        if pipeline_id in self.running_pipelines:
            self.running_pipelines[pipeline_id].cancel()
            del self.running_pipelines[pipeline_id]
        
        del self.pipelines[pipeline_id]
        logger.info(f"Pipeline deleted", pipeline_id=pipeline_id)
        return True

# Global pipeline manager instance
pipeline_manager = PipelineManager() 