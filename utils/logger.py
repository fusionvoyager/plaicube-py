import logging
import sys
from datetime import datetime
from typing import Optional
from config import Config

class PlaicubeLogger:
    """Custom logger for Plaicube API"""
    
    def __init__(self, name: str = "plaicube"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(f"{message} {kwargs if kwargs else ''}")
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(f"{message} {kwargs if kwargs else ''}")
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(f"{message} {kwargs if kwargs else ''}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(f"{message} {kwargs if kwargs else ''}")
    
    def pipeline_start(self, pipeline_id: str, video_id: str):
        """Log pipeline start"""
        self.info(f"Pipeline started", pipeline_id=pipeline_id, video_id=video_id)
    
    def pipeline_complete(self, pipeline_id: str, status: str):
        """Log pipeline completion"""
        self.info(f"Pipeline completed", pipeline_id=pipeline_id, status=status)
    
    def step_start(self, step_id: str, step_type: str, pipeline_id: str):
        """Log step start"""
        self.info(f"Step started", step_id=step_id, step_type=step_type, pipeline_id=pipeline_id)
    
    def step_complete(self, step_id: str, status: str, pipeline_id: str):
        """Log step completion"""
        self.info(f"Step completed", step_id=step_id, status=status, pipeline_id=pipeline_id)
    
    def service_error(self, service_name: str, error: str, pipeline_id: Optional[str] = None):
        """Log service error"""
        self.error(f"Service error", service=service_name, error=error, pipeline_id=pipeline_id)

# Global logger instance
logger = PlaicubeLogger() 