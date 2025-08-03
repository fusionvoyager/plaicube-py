from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict
import httpx
import asyncio
import os
from dotenv import load_dotenv
import uuid
import json
from datetime import datetime
from config import Config
from models import VideoRequest, VideoResponse, PipelineStatusResponse, PipelineConfig
from pipeline_manager import pipeline_manager
from middleware.logging_middleware import LoggingMiddleware
from middleware.error_middleware import ErrorHandlingMiddleware
from utils.validators import validate_uuid, validate_video_url, validate_prompt, validate_pipeline_config
from utils.logger import logger
from exceptions import ValidationException, PipelineException

# Load environment variables
load_dotenv()

# Validate configuration and print current config
Config.validate()
Config.print_config()

app = FastAPI(
    title="Plaicube Video Pipeline API",
    description="Multi-step video processing pipeline with Runway ML, FFmpeg, WhisperAI, and GPT-4",
    version="1.0.0"
)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Plaicube Video Pipeline API - Multi-step processing"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/api/video/transform", response_model=VideoResponse)
async def transform_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Video transformation pipeline başlat
    """
    try:
        # Validate input
        validate_uuid(request.videoId, "videoId")
        validate_video_url(str(request.videoUrl))
        validate_prompt(request.prompt)
        
        if request.pipelineConfig:
            validate_pipeline_config(request.pipelineConfig)
        
        # Check if pipeline already exists for this video
        existing_pipelines = [p for p in pipeline_manager.get_all_pipelines() 
                            if p.videoId == request.videoId]
        if existing_pipelines:
            existing_pipeline = existing_pipelines[0]
            logger.info(f"Pipeline already exists", pipeline_id=existing_pipeline.pipelineId, video_id=request.videoId)
            return VideoResponse(
                videoId=request.videoId,
                pipelineId=existing_pipeline.pipelineId,
                status=existing_pipeline.status,
                message=f"Pipeline already exists with status: {existing_pipeline.status}",
                totalSteps=existing_pipeline.totalSteps,
                completedSteps=existing_pipeline.completedSteps,
                createdAt=existing_pipeline.createdAt,
                updatedAt=existing_pipeline.updatedAt
            )
        
        # Parse pipeline configuration
        config = None
        if request.pipelineConfig:
            config = PipelineConfig(**request.pipelineConfig)
        
        # Create new pipeline
        pipeline = pipeline_manager.create_pipeline(
            video_id=request.videoId,
            video_url=str(request.videoUrl),
            prompt=request.prompt,
            config=config
        )
        
        logger.pipeline_start(pipeline.pipelineId, request.videoId)
        
        # Start pipeline in background
        background_tasks.add_task(pipeline_manager.start_pipeline, pipeline.pipelineId)
        
        return VideoResponse(
            videoId=request.videoId,
            pipelineId=pipeline.pipelineId,
            status=pipeline.status,
            message="Pipeline created and started",
            totalSteps=pipeline.totalSteps,
            completedSteps=pipeline.completedSteps,
            createdAt=pipeline.createdAt
        )
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PipelineException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in transform_video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/pipeline/{pipeline_id}/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(pipeline_id: str):
    """
    Pipeline durumunu kontrol et
    """
    try:
        # Validate pipelineId format
        validate_uuid(pipeline_id, "pipelineId")
        
        # Get pipeline
        pipeline = pipeline_manager.get_pipeline(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        return PipelineStatusResponse(
            pipelineId=pipeline.pipelineId,
            videoId=pipeline.videoId,
            status=pipeline.status,
            message=f"Pipeline status: {pipeline.status}",
            steps=pipeline.steps,
            totalSteps=pipeline.totalSteps,
            completedSteps=pipeline.completedSteps,
            createdAt=pipeline.createdAt,
            updatedAt=pipeline.updatedAt,
            completedAt=pipeline.completedAt
        )
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_pipeline_status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/pipelines")
async def get_all_pipelines():
    """
    Tüm pipeline'ları listele
    """
    try:
        pipelines = pipeline_manager.get_all_pipelines()
        logger.info(f"Retrieved all pipelines", count=len(pipelines))
        
        return {
            "pipelines": [
                {
                    "pipelineId": p.pipelineId,
                    "videoId": p.videoId,
                    "status": p.status,
                    "totalSteps": p.totalSteps,
                    "completedSteps": p.completedSteps,
                    "createdAt": p.createdAt,
                    "updatedAt": p.updatedAt,
                    "completedAt": p.completedAt
                }
                for p in pipelines
            ],
            "total": len(pipelines)
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in get_all_pipelines: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/pipeline/{pipeline_id}/cancel")
async def cancel_pipeline(pipeline_id: str):
    """
    Pipeline'ı iptal et
    """
    try:
        # Validate pipelineId format
        validate_uuid(pipeline_id, "pipelineId")
        
        # Cancel pipeline
        success = pipeline_manager.cancel_pipeline(pipeline_id)
        if not success:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        logger.info(f"Pipeline cancelled", pipeline_id=pipeline_id)
        return {"message": "Pipeline cancelled successfully"}
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in cancel_pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/api/pipeline/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    """
    Pipeline'ı sil
    """
    try:
        # Validate pipelineId format
        validate_uuid(pipeline_id, "pipelineId")
        
        # Delete pipeline
        success = pipeline_manager.delete_pipeline(pipeline_id)
        if not success:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        logger.info(f"Pipeline deleted", pipeline_id=pipeline_id)
        return {"message": "Pipeline deleted successfully"}
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/pipeline/{pipeline_id}/steps")
async def get_pipeline_steps(pipeline_id: str):
    """
    Pipeline adımlarını getir
    """
    try:
        # Validate pipelineId format
        validate_uuid(pipeline_id, "pipelineId")
        
        # Get pipeline
        pipeline = pipeline_manager.get_pipeline(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        return {
            "pipelineId": pipeline.pipelineId,
            "steps": [
                {
                    "stepId": step.stepId,
                    "stepType": step.stepType,
                    "status": step.status,
                    "order": step.order,
                    "progress": step.progress,
                    "startedAt": step.startedAt,
                    "completedAt": step.completedAt,
                    "error": step.error,
                    "output": step.output
                }
                for step in pipeline.steps
            ]
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_pipeline_steps: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Legacy endpoints for backward compatibility
@app.get("/api/video/{video_id}/status")
async def get_video_status_legacy(video_id: str):
    """
    Legacy video status endpoint (redirects to pipeline)
    """
    try:
        # Validate videoId format
        validate_uuid(video_id, "videoId")
        
        # Find pipeline for this video
        pipelines = [p for p in pipeline_manager.get_all_pipelines() 
                    if p.videoId == video_id]
        
        if not pipelines:
            raise HTTPException(status_code=404, detail="Video not found")
        
        pipeline = pipelines[0]
        
        return {
            "videoId": pipeline.videoId,
            "pipelineId": pipeline.pipelineId,
            "status": pipeline.status,
            "message": f"Pipeline status: {pipeline.status}",
            "totalSteps": pipeline.totalSteps,
            "completedSteps": pipeline.completedSteps,
            "createdAt": pipeline.createdAt,
            "updatedAt": pipeline.updatedAt
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_video_status_legacy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Plaicube Video Pipeline API...")
    uvicorn.run(app, host=Config.HOST, port=Config.PORT) 