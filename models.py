from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Pipeline Step Types
class StepType(str, Enum):
    RUNWAY_VIDEO = "runway_video"
    FFMPEG_PROCESS = "ffmpeg_process"
    WHISPER_TRANSCRIBE = "whisper_transcribe"
    GPT4_ANALYSIS = "gpt4_analysis"
    CUSTOM_PROCESS = "custom_process"

# Step Status
class StepStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# Pipeline Status
class PipelineStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Base Models
class PipelineStep(BaseModel):
    stepId: str
    stepType: StepType
    status: StepStatus
    order: int
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    progress: int = 0

class Pipeline(BaseModel):
    pipelineId: str
    videoId: str
    videoUrl: HttpUrl
    prompt: str
    status: PipelineStatus
    steps: List[PipelineStep]
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    totalSteps: int
    completedSteps: int = 0

# Request/Response Models
class VideoRequest(BaseModel):
    videoId: str
    videoUrl: HttpUrl
    prompt: str
    pipelineConfig: Optional[Dict[str, Any]] = None

class VideoResponse(BaseModel):
    videoId: str
    pipelineId: str
    status: PipelineStatus
    message: str
    totalSteps: int
    completedSteps: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None

class PipelineStatusResponse(BaseModel):
    pipelineId: str
    videoId: str
    status: PipelineStatus
    message: str
    steps: List[PipelineStep]
    totalSteps: int
    completedSteps: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None

# Pipeline Configuration
class PipelineConfig(BaseModel):
    enableRunwayVideo: bool = True
    enableFfmpeg: bool = False
    enableWhisper: bool = False
    enableGpt4: bool = False
    customSteps: List[Dict[str, Any]] = [] 