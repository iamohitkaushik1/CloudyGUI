import random
import uuid
from datetime import datetime, timedelta
from ..core.models import Job, Task, Instance

def generate_workload(num_jobs=10, tasks_per_job=5, instances_per_task=3):
    """
    Generate a workload with specified number of jobs, tasks per job, and instances per task.
    
    Args:
        num_jobs (int): Number of jobs to generate
        tasks_per_job (int): Number of tasks per job
        instances_per_task (int): Number of instances per task
    
    Returns:
        list: List of Job objects
    """
    job_types = ['batch_processing', 'machine_learning', 'data_analytics', 'web_service']
    jobs = []
    
    # Create jobs with staggered start times
    base_time = datetime.now()
    
    # Create jobs
    for i in range(num_jobs):
        job = Job(f"job_{uuid.uuid4().hex[:8]}", random.choice(job_types), priority=random.randint(1, 5))
        job.start_time = base_time + timedelta(minutes=random.randint(0, 60))
        job.end_time = job.start_time + timedelta(minutes=random.randint(30, 180))
        
        # Generate tasks for each job
        for j in range(tasks_per_job):
            # Generate resource requirements based on job type
            if job.job_type == 'machine_learning':
                base_resources = {
                    'cpu': random.uniform(20, 40),
                    'memory': random.uniform(4000, 8000),
                    'gpu': random.uniform(1, 2),
                    'disk': random.uniform(50, 200)
                }
            else:
                base_resources = {
                    'cpu': random.uniform(10, 30),
                    'memory': random.uniform(2000, 6000),
                    'gpu': 0,
                    'disk': random.uniform(20, 100)
                }
            
            task = Task(f"{job.job_id}_task_{j}", job.job_id)
            task.start_time = job.start_time + timedelta(minutes=random.randint(0, 30))
            task.end_time = task.start_time + timedelta(minutes=random.randint(15, 90))
            
            # Generate instances for each task
            for k in range(instances_per_task):
                # Add some variation to resource requirements for each instance
                instance_resources = {
                    'cpu': base_resources['cpu'] * random.uniform(0.8, 1.2),
                    'memory': base_resources['memory'] * random.uniform(0.8, 1.2),
                    'gpu': base_resources['gpu'] * random.uniform(0.9, 1.1) if base_resources['gpu'] > 0 else 0,
                    'disk': base_resources['disk'] * random.uniform(0.9, 1.1)
                }
                
                instance = Instance(
                    f"{task.task_id}_instance_{k}",
                    task.task_id,
                    instance_resources['cpu'],
                    instance_resources['memory'],
                    instance_resources['gpu'],
                    instance_resources['disk']
                )
                instance.start_time = task.start_time + timedelta(minutes=random.randint(0, 15))
                instance.end_time = instance.start_time + timedelta(minutes=random.randint(5, 45))
                
                # Set status based on time
                if instance.end_time < datetime.now():
                    instance.status = "completed"
                elif instance.start_time < datetime.now():
                    instance.status = "running"
                
                task.instances.append(instance)
            
            # Update task status based on instance statuses
            if all(i.status == "completed" for i in task.instances):
                task.status = "completed"
            elif any(i.status == "running" for i in task.instances):
                task.status = "running"
            
            job.tasks.append(task)
        
        # Update job status based on task statuses
        if all(t.status == "completed" for t in job.tasks):
            job.status = "completed"
        elif any(t.status == "running" for t in job.tasks):
            job.status = "running"
        
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
