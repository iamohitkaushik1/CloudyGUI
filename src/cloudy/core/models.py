from typing import Dict, List, Union
import random
import math
from datetime import datetime, timedelta
import uuid

class Instance:
    """Represents a single instance of a task with its resource requirements and status.
    
    Attributes:
        instance_id: Unique identifier for the instance
        task_id: ID of the parent task
        task_type: Type of task (e.g., 'data_ingestion', 'model_training', etc.)
        cpu_required: CPU required in cores
        memory_required: Memory required in MB
        gpu_required: GPU required in units
        disk_required: Disk required in GB
        status: Current status (waiting, running, terminated, failed, interrupted)
        start_time: When the instance started running
        end_time: When the instance finished or was interrupted
        error_rate: Random value used for failure simulation
        peak_usage: Peak resource usage during execution
        final_usage: Final resource usage when job completed/terminated
    """
    # Define task types with their typical resource patterns and durations
    TASK_TYPES = {
        'data_ingestion': {
            'duration': (300, 1800),  # 5-30 minutes
            'resource_patterns': {
                'cpu': (0.4, 0.8),    # 40-80% CPU usage
                'memory': (0.3, 0.6),  # 30-60% memory usage
                'gpu': (0, 0),         # No GPU usage
                'disk': (0.7, 0.9)     # 70-90% disk usage
            }
        },
        'data_processing': {
            'duration': (1800, 7200),  # 30-120 minutes
            'resource_patterns': {
                'cpu': (0.6, 0.9),     # 60-90% CPU usage
                'memory': (0.5, 0.8),   # 50-80% memory usage
                'gpu': (0, 0),          # No GPU usage
                'disk': (0.4, 0.7)      # 40-70% disk usage
            }
        },
        'model_training': {
            'duration': (3600, 86400),  # 1-24 hours
            'resource_patterns': {
                'cpu': (0.7, 1.0),      # 70-100% CPU usage
                'memory': (0.6, 0.9),    # 60-90% memory usage
                'gpu': (0.8, 1.0),       # 80-100% GPU usage
                'disk': (0.3, 0.6)       # 30-60% disk usage
            }
        },
        'model_inference': {
            'duration': (60, 3600),     # 1-60 minutes
            'resource_patterns': {
                'cpu': (0.5, 0.8),      # 50-80% CPU usage
                'memory': (0.4, 0.7),    # 40-70% memory usage
                'gpu': (0.6, 0.9),       # 60-90% GPU usage
                'disk': (0.2, 0.4)       # 20-40% disk usage
            }
        },
        'etl_pipeline': {
            'duration': (900, 3600),    # 15-60 minutes
            'resource_patterns': {
                'cpu': (0.5, 0.9),      # 50-90% CPU usage
                'memory': (0.4, 0.8),    # 40-80% memory usage
                'gpu': (0, 0),           # No GPU usage
                'disk': (0.6, 0.9)       # 60-90% disk usage
            }
        },
        'data_analytics': {
            'duration': (1800, 14400),  # 30-240 minutes
            'resource_patterns': {
                'cpu': (0.6, 0.9),      # 60-90% CPU usage
                'memory': (0.7, 0.9),    # 70-90% memory usage
                'gpu': (0, 0),           # No GPU usage
                'disk': (0.3, 0.6)       # 30-60% disk usage
            }
        },
        'batch_processing': {
            'duration': (3600, 28800),  # 1-8 hours
            'resource_patterns': {
                'cpu': (0.7, 1.0),      # 70-100% CPU usage
                'memory': (0.6, 0.9),    # 60-90% memory usage
                'gpu': (0, 0),           # No GPU usage
                'disk': (0.5, 0.8)       # 50-80% disk usage
            }
        },
        'streaming_pipeline': {
            'duration': (43200, 172800),  # 12-48 hours
            'resource_patterns': {
                'cpu': (0.4, 0.7),       # 40-70% CPU usage
                'memory': (0.5, 0.8),     # 50-80% memory usage
                'gpu': (0, 0),            # No GPU usage
                'disk': (0.6, 0.9)        # 60-90% disk usage
            }
        }
    }

    def __init__(self, instance_id: str, task_id: str, task_type: str, cpu_required: float = 0, memory_required: float = 0, gpu_required: float = 0, disk_required: float = 0):
        """Initialize a new instance with given resources."""
        self.instance_id = instance_id
        self.task_id = task_id
        self.task_type = task_type
        self.cpu_required = cpu_required
        self.memory_required = memory_required
        self.gpu_required = gpu_required
        self.disk_required = disk_required
        self.status = "waiting"  # waiting, running, terminated, failed, interrupted
        self.start_time = None
        self.end_time = None
        self.error_rate = random.random()  # Used for failure simulation
        self.current_usage = {
            'cpu': 0,
            'memory': 0,
            'gpu': 0,
            'disk': 0
        }
        # Track peak resource usage
        self.peak_usage = {
            'cpu': 0,
            'memory': 0,
            'gpu': 0,
            'disk': 0
        }
        # Store final resource usage when job completes
        self.final_usage = {
            'cpu': 0,
            'memory': 0,
            'gpu': 0,
            'disk': 0
        }

        # Set duration based on task type
        if task_type in self.TASK_TYPES:
            min_duration, max_duration = self.TASK_TYPES[task_type]['duration']
            duration_seconds = random.uniform(min_duration, max_duration)
            if self.start_time:
                self.end_time = self.start_time + timedelta(seconds=duration_seconds)

    def update_usage(self, current_time: datetime):
        """Update current resource usage based on time and status"""
        if self.status == 'running':
            # For running jobs, always calculate resource usage
            if not self.start_time:
                self.start_time = current_time

            # Calculate how far along we are in the job
            if not self.end_time:
                # If end_time not set, calculate it based on task type duration
                if self.task_type in self.TASK_TYPES:
                    min_duration, max_duration = self.TASK_TYPES[self.task_type]['duration']
                    duration_seconds = random.uniform(min_duration, max_duration)
                    self.end_time = self.start_time + timedelta(seconds=duration_seconds)
                else:
                    # Default 1 hour duration if task type not found
                    self.end_time = self.start_time + timedelta(hours=1)

            total_duration = (self.end_time - self.start_time).total_seconds()
            elapsed_time = (current_time - self.start_time).total_seconds()
            progress = min(1.0, max(0.0, elapsed_time / total_duration))

            # Get resource patterns for this task type
            if self.task_type in self.TASK_TYPES:
                patterns = self.TASK_TYPES[self.task_type]['resource_patterns']
                
                # Calculate resource usage based on patterns and progress
                for resource in self.current_usage:
                    if resource in patterns:
                        min_usage, max_usage = patterns[resource]
                        # Base usage varies based on progress
                        base_usage = min_usage + (max_usage - min_usage) * progress
                        # Add small fluctuations
                        fluctuation = random.uniform(-0.05, 0.05)
                        usage = max(0, min(1.0, base_usage + fluctuation))
                        # Apply usage to required resources
                        required = getattr(self, f"{resource}_required")
                        self.current_usage[resource] = required * usage

                        # Update peak usage
                        self.peak_usage[resource] = max(self.peak_usage[resource], self.current_usage[resource])
            else:
                # If no patterns found, use 50-80% of required resources for running jobs
                for resource in self.current_usage:
                    required = getattr(self, f"{resource}_required")
                    base_usage = random.uniform(0.5, 0.8)  # Use 50-80% of required resources
                    self.current_usage[resource] = required * base_usage
                    self.peak_usage[resource] = max(self.peak_usage[resource], self.current_usage[resource])
            
        elif self.status in ['terminated', 'failed', 'interrupted']:
            if not any(self.final_usage.values()):  # If final usage not set
                # Calculate final usage based on task type patterns
                if self.task_type in self.TASK_TYPES:
                    patterns = self.TASK_TYPES[self.task_type]['resource_patterns']
                    for resource in self.current_usage:
                        if resource in patterns:
                            min_usage, max_usage = patterns[resource]
                            # Use average of min and max for final usage
                            usage = (min_usage + max_usage) / 2
                            required = getattr(self, f"{resource}_required")
                            self.final_usage[resource] = required * usage
                else:
                    # If no patterns found, use 50% of required resources
                    for resource in self.current_usage:
                        required = getattr(self, f"{resource}_required")
                        self.final_usage[resource] = required * 0.5
            
            # Use final usage for completed/failed/interrupted jobs
            self.current_usage = self.final_usage.copy()
        else:
            # Reset usage if waiting
            for resource in self.current_usage:
                self.current_usage[resource] = 0

    def get_required_resource(self, resource: str) -> float:
        """Get the required amount for a specific resource."""
        return getattr(self, f"{resource}_required", 0)

class Task:
    """Represents a task that contains multiple instances.
    
    Attributes:
        task_id: Unique identifier for the task
        job_id: ID of the parent job
        task_type: Type of task (e.g., 'data_ingestion', 'model_training', etc.)
        instances: List of instances belonging to this task
        status: Current status (waiting, running, terminated, failed, interrupted)
        start_time: When the task started
        end_time: When the task ended
    """
    def __init__(self, task_id: str, job_id: str, task_type: str):
        """Initialize a new task."""
        self.task_id = task_id
        self.job_id = job_id
        self.task_type = task_type
        self.instances: List[Instance] = []
        self.status = "waiting"  # waiting, running, terminated, failed, interrupted
        self.start_time = None
        self.end_time = None

    def add_instance(self, instance: Instance):
        """Add an instance to this task."""
        instance.task_type = self.task_type  # Ensure instance has the same task type
        self.instances.append(instance)

    def get_total_resources(self):
        """Calculate total resources required by all instances"""
        total_cpu = sum(instance.cpu_required for instance in self.instances)
        total_memory = sum(instance.memory_required for instance in self.instances)
        total_gpu = sum(instance.gpu_required for instance in self.instances)
        total_disk = sum(instance.disk_required for instance in self.instances)
        return {'cpu': total_cpu, 'memory': total_memory, 'gpu': total_gpu, 'disk': total_disk}
    
    def get_current_usage(self):
        """Get current resource usage across all instances"""
        usage = {'cpu': 0, 'memory': 0, 'gpu': 0, 'disk': 0}
        for instance in self.instances:
            for resource in usage:
                usage[resource] += instance.current_usage[resource]
        return usage

    def update_status(self):
        """Update task status based on instance statuses"""
        instance_statuses = [instance.status for instance in self.instances]
        
        if any(status == 'failed' for status in instance_statuses):
            self.status = 'failed'
            if not self.end_time:
                self.end_time = datetime.now()
        elif all(status == 'terminated' for status in instance_statuses):
            self.status = 'terminated'
            if not self.end_time:
                self.end_time = datetime.now()
        elif any(status == 'running' for status in instance_statuses):
            self.status = 'running'
            if not self.start_time:
                self.start_time = datetime.now()
                # Set end time based on task type's duration
                if self.instances and self.instances[0].task_type in Instance.TASK_TYPES:
                    min_duration, max_duration = Instance.TASK_TYPES[self.task_type]['duration']
                    duration_seconds = random.uniform(min_duration, max_duration)
                    self.end_time = self.start_time + timedelta(seconds=duration_seconds)
        elif any(status == 'interrupted' for status in instance_statuses):
            self.status = 'interrupted'
            if not self.end_time:
                self.end_time = datetime.now()
        else:
            self.status = 'waiting'

class Job:
    """Represents a job that contains multiple tasks and has dependencies.
    
    Attributes:
        job_id: Unique identifier for the job
        job_type: Type of job (data_pipeline, ml_training, batch_processing, etc.)
        tasks: List of tasks belonging to this job
        dependencies: List of job IDs this job depends on
        priority: Job priority (lower number means higher priority)
        status: Current status (waiting, running, terminated, failed, interrupted)
        start_time: When the job started running
        end_time: When the job finished or was interrupted
    """
    # Define job types and their typical task compositions
    JOB_TYPES = {
        'ml_training_pipeline': [
            ('data_ingestion', 1),
            ('data_processing', 1),
            ('model_training', 1),
            ('model_inference', 1)
        ],
        'data_analytics_pipeline': [
            ('data_ingestion', 1),
            ('data_processing', 2),
            ('data_analytics', 1)
        ],
        'batch_etl_pipeline': [
            ('data_ingestion', 1),
            ('etl_pipeline', 3),
            ('data_processing', 1)
        ],
        'streaming_analytics': [
            ('data_ingestion', 1),
            ('streaming_pipeline', 1),
            ('data_analytics', 1)
        ],
        'distributed_training': [
            ('data_ingestion', 1),
            ('data_processing', 2),
            ('model_training', 3),
            ('model_inference', 1)
        ]
    }

    def __init__(self, job_id: str, job_type: str, priority: int = 0):
        """Initialize a new job with given type and priority."""
        self.job_id = job_id
        self.job_type = job_type
        self.tasks: List[Task] = []
        self.dependencies: List[str] = []
        self.priority = priority
        self.status = "waiting"  # waiting, running, terminated, failed, interrupted
        self.start_time = None
        self.end_time = None
        self.submit_time = datetime.now()  # Track when the job was submitted

    def __lt__(self, other):
        """Compare jobs based on priority (lower number = higher priority)"""
        return self.priority < other.priority

    def __eq__(self, other):
        """Compare jobs for equality based on job_id"""
        return self.job_id == other.job_id

    def __hash__(self):
        """Hash based on job_id for set operations"""
        return hash(self.job_id)

    def add_task(self, task: Task):
        """Add a task to this job."""
        self.tasks.append(task)

    def add_dependency(self, job_id: str):
        """Add a dependency to this job if it doesn't already exist."""
        if job_id not in self.dependencies:
            self.dependencies.append(job_id)

    def get_total_resources(self):
        """Calculate total resources required by all tasks"""
        total_resources = {'cpu': 0, 'memory': 0, 'gpu': 0, 'disk': 0}
        for task in self.tasks:
            task_resources = task.get_total_resources()
            for resource in total_resources:
                total_resources[resource] += task_resources[resource]
        return total_resources

    def get_current_usage(self):
        """Get current resource usage across all tasks"""
        usage = {'cpu': 0, 'memory': 0, 'gpu': 0, 'disk': 0}
        for task in self.tasks:
            task_usage = task.get_current_usage()
            for resource in usage:
                usage[resource] += task_usage[resource]
        return usage

    def update_status(self):
        """Update job status based on task statuses"""
        task_statuses = [task.status for task in self.tasks]
        
        if any(status == 'failed' for status in task_statuses):
            self.status = 'failed'
            if not self.end_time:
                self.end_time = datetime.now()
        elif all(status == 'terminated' for status in task_statuses):
            self.status = 'terminated'
            if not self.end_time:
                self.end_time = datetime.now()
        elif any(status == 'running' for status in task_statuses):
            self.status = 'running'
            if not self.start_time:
                self.start_time = datetime.now()
        elif any(status == 'interrupted' for status in task_statuses):
            self.status = 'interrupted'
            if not self.end_time:
                self.end_time = datetime.now()
        else:
            self.status = 'waiting'
