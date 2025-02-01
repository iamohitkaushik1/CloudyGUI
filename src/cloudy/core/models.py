from typing import Dict, List, Union
import random
from datetime import datetime, timedelta
import uuid

class Instance:
    """Represents a single instance of a task with its resource requirements and status.
    
    Attributes:
        instance_id: Unique identifier for the instance
        task_id: ID of the parent task
        cpu_required: CPU required in cores
        memory_required: Memory required in MB
        gpu_required: GPU required in units
        disk_required: Disk required in GB
        status: Current status (pending, running, completed, failed)
        start_time: When the instance started running
        end_time: When the instance finished or was interrupted
    """
    def __init__(self, instance_id: str, task_id: str, cpu_required: float = 0, memory_required: float = 0, gpu_required: float = 0, disk_required: float = 0):
        """Initialize a new instance with given resources."""
        self.instance_id = instance_id
        self.task_id = task_id
        self.cpu_required = cpu_required
        self.memory_required = memory_required
        self.gpu_required = gpu_required
        self.disk_required = disk_required
        self.status = "pending"  # pending, running, completed, failed
        self.start_time = None
        self.end_time = None

class Task:
    """Represents a task that contains multiple instances.
    
    Attributes:
        task_id: Unique identifier for the task
        job_id: ID of the parent job
        instances: List of instances belonging to this task
        status: Current status (pending, running, completed, failed)
    """
    def __init__(self, task_id: str, job_id: str):
        """Initialize a new task."""
        self.task_id = task_id
        self.job_id = job_id
        self.instances: List[Instance] = []
        self.status = "pending"  # pending, running, completed, failed

    def add_instance(self, instance: Instance):
        """Add an instance to this task."""
        self.instances.append(instance)

    def get_total_resources(self):
        """Calculate total resources required by all instances"""
        total_cpu = sum(instance.cpu_required for instance in self.instances)
        total_memory = sum(instance.memory_required for instance in self.instances)
        total_gpu = sum(instance.gpu_required for instance in self.instances)
        total_disk = sum(instance.disk_required for instance in self.instances)
        return {'cpu': total_cpu, 'memory': total_memory, 'gpu': total_gpu, 'disk': total_disk}

class Job:
    """Represents a job that contains multiple tasks and has dependencies.
    
    Attributes:
        job_id: Unique identifier for the job
        job_type: Type of job (batch_processing, machine_learning, etc.)
        tasks: List of tasks belonging to this job
        dependencies: List of job IDs this job depends on
        priority: Job priority (lower number means higher priority)
        status: Current status (pending, running, completed, failed)
        start_time: When the job started running
        end_time: When the job finished or was interrupted
    """
    def __init__(self, job_id: str, job_type: str, priority: int = 0):
        """Initialize a new job with given type and priority."""
        self.job_id = job_id
        self.job_type = job_type
        self.tasks: List[Task] = []
        self.dependencies: List[str] = []  # List of job IDs this job depends on
        self.priority = priority  # Lower number means higher priority
        self.status = "pending"  # pending, running, completed, failed
        self.start_time = None
        self.end_time = None

    def add_task(self, task: Task):
        """Add a task to this job."""
        self.tasks.append(task)

    def add_dependency(self, job_id: str):
        """Add a dependency to this job if it doesn't already exist."""
        if job_id not in self.dependencies:
            self.dependencies.append(job_id)

    def get_total_resources(self):
        """Calculate total resources required by all tasks"""
        total_cpu = 0
        total_memory = 0
        total_gpu = 0
        total_disk = 0
        for task in self.tasks:
            resources = task.get_total_resources()
            total_cpu += resources['cpu']
            total_memory += resources['memory']
            total_gpu += resources['gpu']
            total_disk += resources['disk']
        return {'cpu': total_cpu, 'memory': total_memory, 'gpu': total_gpu, 'disk': total_disk}
