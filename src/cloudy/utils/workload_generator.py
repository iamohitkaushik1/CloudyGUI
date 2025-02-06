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
        'task_types': ['data_preparation', 'processing', 'aggregation'],
        'depends_on': ['batch_processing', 'analytics'],  # Can depend on batch processing or analytics jobs
        'dependency_probability': 0.4  # 40% chance of having dependencies
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
        'task_types': ['data_preprocessing', 'training', 'evaluation'],
        'depends_on': ['data_processing'],  # Usually depends on data processing jobs
        'dependency_probability': 0.7  # 70% chance of having dependencies
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
        'task_types': ['frontend', 'backend', 'database'],
        'depends_on': [],  # Web services typically don't depend on other jobs
        'dependency_probability': 0.1  # 10% chance of having dependencies
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
        'task_types': ['data_collection', 'analysis', 'visualization'],
        'depends_on': ['analytics'],  # Can depend on analytics jobs
        'dependency_probability': 0.3  # 30% chance of having dependencies
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
        'task_types': ['data_collection', 'analysis', 'visualization'],
        'depends_on': ['data_processing', 'batch_processing'],  # Can depend on data processing or batch processing jobs
        'dependency_probability': 0.5  # 50% chance of having dependencies
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
    job_lookup = {}  # Dictionary to store jobs by type for dependency assignment
    
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
            
            # Calculate submit time within the 7-day window
            submit_offset = random.uniform(0, time_window.total_seconds())
            submit_time = current_time - timedelta(seconds=submit_offset)
            
            # Create job with random priority
            job = Job(f"job_{job_id}", selected_type, random.randint(1, 5))
            job.submit_time = submit_time
            
            # Set job status immediately
            job.status = status
            
            # Set job timing based on status and 7-day window
            if status == 'terminated':
                job.start_time = submit_time
                job.end_time = submit_time + timedelta(minutes=random.randint(30, 180))
            elif status == 'running':
                job.start_time = submit_time
                # End time will be set based on instance durations
            elif status == 'failed':
                job.start_time = submit_time
                # Failed jobs have shorter duration
                job.end_time = submit_time + timedelta(minutes=random.randint(5, 30))
            elif status == 'interrupted':
                job.start_time = submit_time
                job.end_time = submit_time + timedelta(minutes=random.randint(15, 60))
            else:  # waiting
                job.start_time = None
                job.end_time = None
            
            # Store job in lookup for dependency assignment
            if selected_type not in job_lookup:
                job_lookup[selected_type] = []
            job_lookup[selected_type].append(job)
            
            # Generate random number of tasks
            num_tasks = random.randint(1, tasks_per_job)
            task_types = job_config['task_types']
            
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
                        # Set current usage for terminated instances
                        instance.current_usage = {
                            'cpu': cpu_required,
                            'memory': memory_required,
                            'gpu': gpu_required,
                            'disk': disk_required
                        }
                    elif job.status == 'running':
                        instance.start_time = job.start_time
                        # Calculate instance duration based on resource requirements
                        duration = max(30, int((cpu_required + memory_required/1024 + gpu_required*2) * random.uniform(0.8, 1.2)))
                        instance.end_time = job.start_time + timedelta(minutes=duration)
                        instance.status = 'running'
                        # Set current usage for running instances
                        instance.current_usage = {
                            'cpu': cpu_required * random.uniform(0.7, 1.0),  # Vary usage
                            'memory': memory_required * random.uniform(0.6, 0.9),
                            'gpu': gpu_required * random.uniform(0.8, 1.0),
                            'disk': disk_required * random.uniform(0.5, 0.8)
                        }
                    elif job.status == 'failed':
                        instance.start_time = job.start_time
                        instance.end_time = job.end_time
                        instance.status = 'failed'
                        # Set partial usage for failed instances
                        instance.current_usage = {
                            'cpu': cpu_required * random.uniform(0.1, 0.5),
                            'memory': memory_required * random.uniform(0.1, 0.4),
                            'gpu': gpu_required * random.uniform(0.1, 0.3),
                            'disk': disk_required * random.uniform(0.1, 0.3)
                        }
                    elif job.status == 'interrupted':
                        instance.start_time = job.start_time
                        instance.end_time = job.end_time
                        instance.status = 'interrupted'
                        # Set partial usage for interrupted instances
                        instance.current_usage = {
                            'cpu': cpu_required * random.uniform(0.3, 0.7),
                            'memory': memory_required * random.uniform(0.2, 0.6),
                            'gpu': gpu_required * random.uniform(0.2, 0.5),
                            'disk': disk_required * random.uniform(0.2, 0.5)
                        }
                    else:  # waiting
                        instance.status = 'waiting'
                        instance.current_usage = {
                            'cpu': 0,
                            'memory': 0,
                            'gpu': 0,
                            'disk': 0
                        }
                    
                    task.add_instance(instance)
                job.add_task(task)
            
            # Add job to workload
            workload.append(job)
            job_id += 1
    
    # Add dependencies after all jobs are created
    for job in workload:
        job_config = JOB_TYPES[job.job_type]
        current_job_id = int(job.job_id.split('_')[1])  # Extract job ID number
        
        # Check if this job should have dependencies
        if (random.random() < job_config['dependency_probability'] and 
            job_config['depends_on'] and job.submit_time and current_job_id > 10):  # Skip first 10 jobs
            
            # Get potential dependency types for this job
            possible_dep_types = job_config['depends_on']
            
            # Get all possible dependency jobs (must be submitted before this job)
            possible_deps = []
            for dep_type in possible_dep_types:
                if dep_type in job_lookup:
                    for dep_job in job_lookup[dep_type]:
                        dep_job_id = int(dep_job.job_id.split('_')[1])
                        if dep_job_id < current_job_id:  # Only allow dependencies on previous jobs
                            possible_deps.append(dep_job)
            
            # Add 1-3 dependencies if possible
            if possible_deps:
                num_deps = random.randint(1, min(3, len(possible_deps)))
                selected_deps = random.sample(possible_deps, num_deps)
                
                for dep_job in selected_deps:
                    job.dependencies.append(dep_job.job_id)
                    
                # Sort dependencies for consistent output
                job.dependencies.sort()
    
    return workload
