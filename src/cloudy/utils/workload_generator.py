import random
import uuid
from ..core.models import Job, Task

def generate_workload(num_jobs=10):
    job_types = ['batch_processing', 'machine_learning', 'data_analytics', 'web_service']
    jobs = []
    
    # Create jobs
    for i in range(num_jobs):
        job = Job(f"job_{uuid.uuid4().hex[:8]}", random.choice(job_types), priority=random.randint(1, 5))
        
        # Generate 1-5 tasks per job
        num_tasks = random.randint(1, 5)
        for j in range(num_tasks):
            # Generate resource requirements based on job type
            if job.job_type == 'machine_learning':
                required_resources = {
                    'cpu': random.uniform(20, 40),
                    'memory': random.uniform(4000, 8000),
                    'gpu': random.uniform(1, 2)
                }
            else:
                required_resources = {
                    'cpu': random.uniform(10, 30),
                    'memory': random.uniform(2000, 6000),
                    'gpu': 0
                }
            
            task = Task(f"{job.job_id}_task_{j}", job.job_id, 
                       random.randint(1, 3), required_resources)
            job.tasks.append(task)
        
        jobs.append(job)
    
    # Add some random dependencies (ensuring no cycles)
    for i, job in enumerate(jobs):
        # Can only depend on jobs that come before this one to avoid cycles
        if i > 0:
            # 30% chance to add a dependency
            if random.random() < 0.3:
                dependency_job = random.choice(jobs[:i])
                job.add_dependency(dependency_job.job_id)
    
    return jobs
