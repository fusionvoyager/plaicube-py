#!/usr/bin/env python3
"""
Plaicube Video Pipeline API - Main entry point
"""

import uvicorn
from main import app
from config import Config
from utils.logger import logger

if __name__ == "__main__":
    logger.info("🚀 Starting Plaicube Video Pipeline API...")
    logger.info(f"Server will run on http://{Config.HOST}:{Config.PORT}")
    
    uvicorn.run(
        app, 
        host=Config.HOST, 
        port=Config.PORT,
        log_level=Config.LOG_LEVEL.lower()
    ) 