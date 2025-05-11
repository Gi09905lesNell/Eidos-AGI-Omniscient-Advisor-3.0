from mcprotocol import SecureServer
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
import uuid
import logging
class SchedulerMCP(SecureServer):
    """
    Advanced scheduler service that manages job scheduling and execution
    Provides REST API endpoints for job management
    """
    
    def __init__(self, max_threads=20, max_processes=5):
        """
        Initialize the scheduler with configurable thread and process pools
        """
        # Configure job stores
        jobstores = {
            'default': MemoryJobStore()
        }
        
        # Configure executor pools
        executors = {
            'default': ThreadPoolExecutor(max_threads),
            'processpool': ProcessPoolExecutor(max_processes)
        }
        
        # Scheduler configuration
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 30
        }
        
        # Initialize scheduler with configuration
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )
        
        # Start scheduler
        self.scheduler.start()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    @endpoint('/v1/schedule/add')
    def add_job(self, params):
        """
        Add a new job to the scheduler
        params: Dictionary containing job configuration
        returns: Job ID and status
        """
        try:
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Extract job parameters
            func = params.get('func')
            trigger_type = params.get('trigger_type', 'date')
            trigger_args = params.get('trigger_args', {})
            job_kwargs = params.get('kwargs', {})
            
            # Validate parameters
            if not func:
                raise ValueError("Function parameter is required")
                
            # Add job to scheduler
            job = self.scheduler.add_job(
                func=func,
                trigger=trigger_type,
                id=job_id,
                **trigger_args,
                **job_kwargs
            )
            
            self.logger.info(f"Added new job with ID: {job_id}")
            
            return {
                "job_id": job_id,
                "status": "scheduled",
                "next_run_time": str(job.next_run_time)
            }
            
        except Exception as e:
            self.logger.error(f"Error adding job: {str(e)}")
            raise
            
    @endpoint('/v1/schedule/remove')
    def remove_job(self, params):
        """
        Remove a job from the scheduler
        """
        job_id = params.get('job_id')
        try:
            self.scheduler.remove_job(job_id)
            return {"status": "removed", "job_id": job_id}
        except Exception as e:
            self.logger.error(f"Error removing job {job_id}: {str(e)}")
            raise
            
    @endpoint('/v1/schedule/pause')
    def pause_job(self, params):
        """
        Pause a scheduled job
        """
        job_id = params.get('job_id')
        try:
            self.scheduler.pause_job(job_id)
            return {"status": "paused", "job_id": job_id}
        except Exception as e:
            self.logger.error(f"Error pausing job {job_id}: {str(e)}")
            raise
            
    @endpoint('/v1/schedule/resume')
    def resume_job(self, params):
        """
        Resume a paused job
        """
        job_id = params.get('job_id')
        try:
            self.scheduler.resume_job(job_id)
            return {"status": "resumed", "job_id": job_id}
        except Exception as e:
            self.logger.error(f"Error resuming job {job_id}: {str(e)}")
            raise
            
    @endpoint('/v1/schedule/list')
    def list_jobs(self, params=None):
        """
        List all scheduled jobs
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger),
                "status": "paused" if job.next_run_time is None else "active"
            })
        return {"jobs": jobs}
        
    def shutdown(self):
        """
        Gracefully shutdown the scheduler
        """
        try:
            self.scheduler.shutdown(wait=True)
            self.logger.info("Scheduler shutdown successfully")
        except Exception as e:
            self.logger.error(f"Error during scheduler shutdown: {str(e)}")
            raise
