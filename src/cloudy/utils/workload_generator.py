import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict
from ..core.models import Job, Task, Instance
from ..scheduler.scheduler import Scheduler
from ..scheduler.resource_manager import ResourceManager

# Job type configurations with realistic characteristics
JOB_TYPES = {
    'data_processing': {
        'weight': 0.3,  # 30% of jobs
        'duration_range': (30, 180),  # 30 mins to 3 hours
        'failure_rate': 0.05,  # 5% chance of failure
        'resource_ranges': {
            'cpu': (4, 32),
            'memory': (8 * 1024, 128 * 1024),  # 8GB to 128GB
            'gpu': (0, 2),
            'disk': (100, 500)
        },
        'task_types': ['data_preparation', 'processing', 'aggregation']
    },
    'machine_learning': {
        'weight': 0.25,  # 25% of jobs
        'duration_range': (120, 720),  # 2-12 hours
        'failure_rate': 0.1,  # 10% chance of failure
        'resource_ranges': {
            'cpu': (8, 64),
            'memory': (16 * 1024, 256 * 1024),  # 16GB to 256GB
            'gpu': (1, 4),
            'disk': (200, 1000)
        },
        'task_types': ['data_preprocessing', 'training', 'evaluation']
    },
    'web_service': {
        'weight': 0.2,  # 20% of jobs
        'duration_range': (15, 120),  # 15 mins to 2 hours
        'failure_rate': 0.03,  # 3% chance of failure
        'resource_ranges': {
            'cpu': (2, 16),
            'memory': (4 * 1024, 32 * 1024),  # 4GB to 32GB
            'gpu': (0, 0),
            'disk': (50, 200)
        },
        'task_types': ['frontend', 'backend', 'database']
    },
    'batch_processing': {
        'weight': 0.15,  # 15% of jobs
        'duration_range': (60, 360),  # 1-6 hours
        'failure_rate': 0.07,  # 7% chance of failure
        'resource_ranges': {
            'cpu': (16, 128),
            'memory': (32 * 1024, 512 * 1024),  # 32GB to 512GB
            'gpu': (0, 8),
            'disk': (500, 2000)
        },
        'task_types': ['data_collection', 'analysis', 'visualization']
    },
    'analytics': {
        'weight': 0.1,  # 10% of jobs
        'duration_range': (30, 180),  # 30 mins to 3 hours
        'failure_rate': 0.05,  # 5% chance of failure
        'resource_ranges': {
            'cpu': (4, 32),
            'memory': (16 * 1024, 128 * 1024),  # 16GB to 128GB
            'gpu': (0, 2),
            'disk': (200, 800)
        },
        'task_types': ['data_collection', 'analysis', 'visualization']
    }
}

# System resources (increased for larger workloads)
TOTAL_RESOURCES = {
    'cpu': 512,  # 512 CPU cores
    'memory': 2048 * 1024,  # 2TB RAM in MB
    'gpu': 32,  # 32 GPUs
    'disk': 10240  # 10TB disk in GB
}

def generate_workload(num_jobs=1000, tasks_per_job=5, instances_per_task=3):
    """
    Generate a realistic workload with jobs, tasks, and instances.
    
    Args:
        num_jobs (int): Number of jobs to generate (default: 1000)
        tasks_per_job (int): Maximum number of tasks per job (default: 5)
        instances_per_task (int): Maximum number of instances per task (default: 3)
    
    Returns:
        list: List of Job objects representing the workload
    """
    # Input validation
    num_jobs = min(max(1, num_jobs), 50000)  # Limit to 50,000 jobs for memory management
    tasks_per_job = min(max(1, tasks_per_job), 20)  # Limit to 20 tasks per job
    instances_per_task = min(max(1, instances_per_task), 10)  # Limit to 10 instances per task
    
    workload = []
    scheduler = Scheduler(ResourceManager(TOTAL_RESOURCES))
    
    # Calculate time ranges for job distribution
    current_time = datetime.now()
    time_window = timedelta(days=7)  # Use a 7-day window for job distribution
    
    # Calculate job distribution
    total_weight = sum(job_type['weight'] for job_type in JOB_TYPES.values())
    job_distribution = {
        'waiting': int(0.2 * num_jobs),    # 20% waiting
        'running': int(0.3 * num_jobs),    # 30% running
        'terminated': int(0.35 * num_jobs), # 35% terminated
        'failed': int(0.1 * num_jobs),     # 10% failed
        'interrupted': int(0.05 * num_jobs) # 5% interrupted
    }
    
    # Ensure we account for all jobs due to rounding
    total_distributed = sum(job_distribution.values())
    if total_distributed < num_jobs:
        job_distribution['running'] += num_jobs - total_distributed
    
    # Generate jobs based on distribution
    job_id = 1
    for status, count in job_distribution.items():
        for _ in range(count):
            # Select job type based on weights
            rand_val = random.random() * total_weight
            cumulative_weight = 0
            selected_type = None
            
            for job_type, config in JOB_TYPES.items():
                cumulative_weight += config['weight']
                if rand_val <= cumulative_weight:
                    selected_type = job_type
                    break
            
            job_config = JOB_TYPES[selected_type]
            
            # Calculate submit time within the last week
            submit_offset = random.uniform(0, time_window.total_seconds())
            submit_time = current_time - timedelta(seconds=submit_offset)
            
            # Create job with random priority
            job = Job(f"job_{job_id}", selected_type, random.randint(1, 5))
            job.submit_time = submit_time
            
            # Generate random number of tasks
            num_tasks = random.randint(1, tasks_per_job)
            task_types = job_config['task_types']
            
            # Set job timing based on status
            if status == 'terminated':
                # For terminated jobs, set both start and end times
                start_offset = random.uniform(0, submit_offset)
                job.start_time = submit_time + timedelta(seconds=start_offset)
                duration = random.uniform(job_config['duration_range'][0] * 60, 
                                       job_config['duration_range'][1] * 60)
                job.end_time = job.start_time + timedelta(seconds=duration)
            
            elif status == 'running':
                # For running jobs, only set start time
                start_offset = random.uniform(0, submit_offset)
                job.start_time = submit_time + timedelta(seconds=start_offset)
                job.end_time = None
            
            elif status == 'failed':
                # For failed jobs, set shorter duration
                start_offset = random.uniform(0, submit_offset)
                job.start_time = submit_time + timedelta(seconds=start_offset)
                max_duration = job_config['duration_range'][1] * 30  # 50% of max duration
                duration = random.uniform(0, max_duration)
                job.end_time = job.start_time + timedelta(seconds=duration)
            
            elif status == 'interrupted':
                # For interrupted jobs, random duration up to max
                start_offset = random.uniform(0, submit_offset)
                job.start_time = submit_time + timedelta(seconds=start_offset)
                max_duration = job_config['duration_range'][1] * 60
                duration = random.uniform(0, max_duration)
                job.end_time = job.start_time + timedelta(seconds=duration)
            
            else:  # waiting
                job.start_time = None
                job.end_time = None
            
            # Set job status
            job.status = status
            
            # Create tasks
            for j in range(num_tasks):
                task_type = random.choice(task_types)
                task = Task(f"task_{job_id}_{j}", job.job_id, task_type)
                
                # Create instances for each task
                num_instances = random.randint(1, instances_per_task)
                for k in range(num_instances):
                    # Scale resource requirements based on total resources
                    cpu_range = job_config['resource_ranges']['cpu']
                    memory_range = job_config['resource_ranges']['memory']
                    gpu_range = job_config['resource_ranges']['gpu']
                    disk_range = job_config['resource_ranges']['disk']
                    
                    # Ensure resources don't exceed system limits
                    max_cpu = min(cpu_range[1], TOTAL_RESOURCES['cpu'] // 4)
                    max_memory = min(memory_range[1], TOTAL_RESOURCES['memory'] // 4)
                    max_gpu = min(gpu_range[1], TOTAL_RESOURCES['gpu'])
                    max_disk = min(disk_range[1], TOTAL_RESOURCES['disk'] // 2)
                    
                    # Set actual resource requirements
                    cpu_required = random.uniform(cpu_range[0], max_cpu)
                    memory_required = random.uniform(memory_range[0], max_memory)
                    gpu_required = random.uniform(gpu_range[0], max_gpu)
                    disk_required = random.uniform(disk_range[0], max_disk)
                    
                    instance = Instance(
                        f"instance_{job_id}_{j}_{k}",
                        task.task_id,
                        task.task_type,
                        cpu_required=cpu_required,
                        memory_required=memory_required,
                        gpu_required=gpu_required,
                        disk_required=disk_required
                    )
                    
                    # Set instance timing based on job status
                    if job.status == 'terminated':
                        instance.start_time = job.start_time
                        instance.end_time = job.end_time
                        instance.status = 'terminated'
                    elif job.status == 'running':
                        instance.start_time = job.start_time
                        instance.status = 'running'
                    elif job.status == 'failed':
                        instance.start_time = job.start_time
                        instance.end_time = job.end_time
                        instance.status = 'failed'
                    elif job.status == 'interrupted':
                        instance.start_time = job.start_time
                        instance.end_time = job.end_time
                        instance.status = 'interrupted'
                    else:
                        instance.status = 'waiting'
                    
                    task.add_instance(instance)
                job.add_task(task)
            
            workload.append(job)
            job_id += 1
    
    return workload
