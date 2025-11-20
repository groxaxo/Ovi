"""
API Server for Ovi Video Generation
Provides REST API and WebSocket support for queue management
"""

import os
import sys
import logging
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from queue import Queue as ThreadQueue
from threading import Thread, Lock

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import socketio
import uvicorn

from ovi.ovi_fusion_engine import OviFusionEngine, DEFAULT_CONFIG
from ovi.utils.io_utils import save_video
import tempfile

# Initialize FastAPI
app = FastAPI(title="Ovi API Server", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Models
class GenerationOptions(BaseModel):
    seed: int = 100
    steps: int = 50
    videoGuidance: float = 4.0
    audioGuidance: float = 3.0
    resolution: str = "960x960"
    duration: str = "10s"
    solver: str = "unipc"
    slgLayer: int = 11


class GenerationJob(BaseModel):
    id: str
    mode: str  # 't2v' or 'i2v'
    prompt: str
    image: Optional[str] = None
    options: GenerationOptions
    status: str = "queued"
    progress: Optional[float] = None
    videoUrl: Optional[str] = None
    error: Optional[str] = None
    createdAt: str


# Global state
class JobQueue:
    def __init__(self):
        self.jobs: Dict[str, GenerationJob] = {}
        self.queue: ThreadQueue = ThreadQueue()
        self.lock = Lock()
        self.processing = False
        
    def add_job(self, job: GenerationJob):
        with self.lock:
            self.jobs[job.id] = job
            self.queue.put(job)
            
    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        with self.lock:
            return self.jobs.get(job_id)
            
    def update_job(self, job_id: str, **kwargs):
        with self.lock:
            if job_id in self.jobs:
                for key, value in kwargs.items():
                    setattr(self.jobs[job_id], key, value)
                    
    def remove_job(self, job_id: str):
        with self.lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                
    def get_all_jobs(self) -> List[GenerationJob]:
        with self.lock:
            return list(self.jobs.values())


job_queue = JobQueue()
ovi_engine: Optional[OviFusionEngine] = None


# Initialize Ovi Engine
def init_ovi_engine():
    global ovi_engine
    if ovi_engine is None:
        logger.info("Initializing Ovi Fusion Engine...")
        try:
            ovi_engine = OviFusionEngine(config=DEFAULT_CONFIG)
            logger.info("Ovi Fusion Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ovi Engine: {e}")
            raise


# Process queue
async def process_queue():
    """Background task to process generation queue"""
    while True:
        try:
            if not job_queue.queue.empty():
                job = job_queue.queue.get()
                logger.info(f"Processing job {job.id}")
                
                # Update status
                job_queue.update_job(job.id, status="processing", progress=0)
                await sio.emit('job_update', {
                    'id': job.id,
                    'status': 'processing',
                    'progress': 0
                })
                
                try:
                    # Parse resolution
                    height, width = map(int, job.options.resolution.split('x'))
                    
                    # Generate video
                    image_path = None
                    if job.mode == 'i2v' and job.image:
                        # Handle image (would need to be saved from upload)
                        pass
                    
                    # Simulate progress updates (in real implementation, hook into generation)
                    for progress in [25, 50, 75]:
                        await asyncio.sleep(1)
                        job_queue.update_job(job.id, progress=progress)
                        await sio.emit('job_update', {
                            'id': job.id,
                            'status': 'processing',
                            'progress': progress
                        })
                    
                    generated_video, generated_audio, _ = ovi_engine.generate(
                        text_prompt=job.prompt,
                        image_path=image_path,
                        video_frame_height_width=[height, width],
                        seed=job.options.seed,
                        solver_name=job.options.solver,
                        sample_steps=job.options.steps,
                        shift=5.0,
                        video_guidance_scale=job.options.videoGuidance,
                        audio_guidance_scale=job.options.audioGuidance,
                        slg_layer=job.options.slgLayer,
                        video_negative_prompt="jitter, bad hands, blur, distortion",
                        audio_negative_prompt="robotic, muffled, echo, distorted"
                    )
                    
                    # Save video
                    output_dir = Path("./outputs")
                    output_dir.mkdir(exist_ok=True)
                    video_path = output_dir / f"{job.id}.mp4"
                    save_video(str(video_path), generated_video, generated_audio, fps=24, sample_rate=16000)
                    
                    # Update job
                    job_queue.update_job(
                        job.id,
                        status="completed",
                        progress=100,
                        videoUrl=f"/api/videos/{job.id}.mp4"
                    )
                    
                    await sio.emit('job_update', {
                        'id': job.id,
                        'status': 'completed',
                        'progress': 100,
                        'videoUrl': f"/api/videos/{job.id}.mp4"
                    })
                    
                    logger.info(f"Job {job.id} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Error processing job {job.id}: {e}")
                    job_queue.update_job(
                        job.id,
                        status="failed",
                        error=str(e)
                    )
                    await sio.emit('job_update', {
                        'id': job.id,
                        'status': 'failed',
                        'error': str(e)
                    })
            else:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in queue processor: {e}")
            await asyncio.sleep(1)


# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize engine and start queue processor"""
    init_ovi_engine()
    asyncio.create_task(process_queue())


@app.get("/")
async def root():
    return {"message": "Ovi API Server", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "engine_loaded": ovi_engine is not None,
        "queue_size": job_queue.queue.qsize(),
        "total_jobs": len(job_queue.get_all_jobs())
    }


@app.post("/api/generate")
async def generate_video(job: GenerationJob):
    """Submit a new video generation job"""
    try:
        logger.info(f"Received generation request: {job.id}")
        job_queue.add_job(job)
        return {"status": "success", "job_id": job.id, "message": "Job added to queue"}
    except Exception as e:
        logger.error(f"Error submitting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs")
async def get_jobs():
    """Get all jobs"""
    return job_queue.get_all_jobs()


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get specific job"""
    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a job"""
    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == "queued":
        job_queue.remove_job(job_id)
        return {"status": "success", "message": "Job cancelled"}
    else:
        return {"status": "error", "message": "Cannot cancel job in current state"}


@app.get("/api/videos/{filename}")
async def get_video(filename: str):
    """Serve generated video"""
    video_path = Path("./outputs") / filename
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(video_path)


# Socket.IO Events
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")


@sio.event
async def submit_job(sid, data):
    """Handle job submission via WebSocket"""
    try:
        job = GenerationJob(**data)
        job_queue.add_job(job)
        await sio.emit('job_submitted', {'id': job.id, 'status': 'queued'}, room=sid)
    except Exception as e:
        logger.error(f"Error handling submit_job: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)


@sio.event
async def cancel_job(sid, data):
    """Handle job cancellation via WebSocket"""
    try:
        job_id = data.get('id')
        job = job_queue.get_job(job_id)
        if job and job.status == "queued":
            job_queue.remove_job(job_id)
            await sio.emit('job_cancelled', {'id': job_id}, room=sid)
    except Exception as e:
        logger.error(f"Error handling cancel_job: {e}")


if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, log_level="info")
