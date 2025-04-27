from mcprotocol import SecureServer
from apscheduler.schedulers.background import BackgroundScheduler

class SchedulerMCP(SecureServer):
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
    @endpoint('/v1/schedule/add')
    def add_job(self, params):
        self.scheduler.add_job(params['func'], **params['kwargs'])
        return {"job_id": "generated-job-id"}