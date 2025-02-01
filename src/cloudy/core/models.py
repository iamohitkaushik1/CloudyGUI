from typing import Dict, List, Union
import random
from datetime import datetime, timedelta
import uuid

class Instance:
    """Represents an instance of a task.
    
    Attributes:
        instance_id: Unique identifier for the instance
        task_id: ID of the parent task
        workload_type: Type of workload (general_purpose, compute_intensive, memory_intensive, gpu_intensive)
        status: Current status of the instance
        start_time: When the instance started running
        end_time: When the instance finished or was interrupted
        cpu_required: CPU cores required
        memory_required: Memory required in MB
        gpu_required: GPU units required
        health_check_failures: Number of consecutive health check failures
        error_rate: Random error rate for this instance
    """
    
    # Realistic workload profiles based on common cloud usage patterns
    WORKLOAD_PROFILES = {
        'general_purpose': {
            'cpu': (1, 4),      # 1-4 cores
            'memory': (2, 8),   # 2-8 GB
            'gpu': (0, 0),      # No GPU
            'weight': 0.5       # 50% of workloads
        },
        'compute_intensive': {
            'cpu': (8, 32),     # 8-32 cores
            'memory': (8, 16),  # 8-16 GB
            'gpu': (0, 0),      # No GPU
            'weight': 0.2       # 20% of workloads
        },
        'memory_intensive': {
            'cpu': (4, 8),      # 4-8 cores
            'memory': (32, 128),# 32-128 GB
            'gpu': (0, 0),      # No GPU
            'weight': 0.2       # 20% of workloads
        },
        'gpu_intensive': {
            'cpu': (8, 16),     # 8-16 cores
            'memory': (16, 32), # 16-32 GB
            'gpu': (1, 4),      # 1-4 GPUs
            'weight': 0.1       # 10% of workloads
        }
    }

    def __init__(self, instance_id: str, task_id: str, workload_type: str = None):
        """Initialize a new instance with realistic resource requirements."""
        self.instance_id = instance_id
        self.task_id = task_id
        
        # Select workload type based on weights if not specified
        if workload_type is None:
            workload_type = random.choices(
                list(self.WORKLOAD_PROFILES.keys()),
                weights=[profile['weight'] for profile in self.WORKLOAD_PROFILES.values()]
            )[0]
        
        self.workload_type = workload_type
        profile = self.WORKLOAD_PROFILES[workload_type]
        
        # Assign resources based on workload profile
        self.cpu_required = random.randint(profile['cpu'][0], profile['cpu'][1])
        # Convert GB to MB for memory
        self.memory_required = random.randint(profile['memory'][0], profile['memory'][1]) * 1024
        self.gpu_required = random.randint(profile['gpu'][0], profile['gpu'][1])
        
        self.status = "pending"  # pending, provisioning, starting, running, degraded, unhealthy, stopping, terminated, failed
        self.start_time = None
        self.end_time = None
        self.health_check_failures = 0
        self.error_rate = random.random()  # Random error probability
        self.last_health_check = None
        
        # Initialize performance metrics based on workload type
        self.performance_metrics = {
            'cpu_utilization': self._initial_cpu_utilization(),
            'memory_utilization': self._initial_memory_utilization(),
            'network_latency': random.uniform(10, 50)  # 10-50ms initial latency
        }
        self.restart_count = 0
        self.max_restarts = 3
        
    def _initial_cpu_utilization(self):
        """Set initial CPU utilization based on workload type."""
        if self.workload_type == 'compute_intensive':
            return random.uniform(70, 90)
        elif self.workload_type == 'gpu_intensive':
            return random.uniform(50, 70)
        return random.uniform(20, 60)
    
    def _initial_memory_utilization(self):
        """Set initial memory utilization based on workload type."""
        if self.workload_type == 'memory_intensive':
            return random.uniform(60, 80)
        return random.uniform(20, 50)
        
    def update_performance_metrics(self):
        """Update instance performance metrics with realistic fluctuations based on workload type."""
        # CPU utilization changes
        cpu_fluctuation = {
            'compute_intensive': (-5, 15),
            'gpu_intensive': (-10, 10),
            'memory_intensive': (-8, 8),
            'general_purpose': (-15, 15)
        }
        
        # Memory utilization changes
        mem_fluctuation = {
            'memory_intensive': (-5, 15),
            'compute_intensive': (-10, 10),
            'gpu_intensive': (-8, 8),
            'general_purpose': (-10, 10)
        }
        
        # Update based on workload type
        cpu_range = cpu_fluctuation[self.workload_type]
        mem_range = mem_fluctuation[self.workload_type]
        
        self.performance_metrics['cpu_utilization'] = min(100, max(0, 
            self.performance_metrics['cpu_utilization'] + random.uniform(cpu_range[0], cpu_range[1])))
        self.performance_metrics['memory_utilization'] = min(100, max(0, 
            self.performance_metrics['memory_utilization'] + random.uniform(mem_range[0], mem_range[1])))
        self.performance_metrics['network_latency'] = max(0, 
            self.performance_metrics['network_latency'] + random.uniform(-20, 20))
        
    def is_healthy(self):
        """Check if the instance is healthy based on workload-specific thresholds."""
        thresholds = {
            'compute_intensive': {'cpu': 95, 'memory': 80, 'latency': 150},
            'memory_intensive': {'cpu': 80, 'memory': 90, 'latency': 200},
            'gpu_intensive': {'cpu': 85, 'memory': 85, 'latency': 100},
            'general_purpose': {'cpu': 90, 'memory': 85, 'latency': 200}
        }
        
        limits = thresholds[self.workload_type]
        return (
            self.performance_metrics['cpu_utilization'] < limits['cpu'] and
            self.performance_metrics['memory_utilization'] < limits['memory'] and
            self.performance_metrics['network_latency'] < limits['latency'] and
            self.health_check_failures < 3
        )

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
        return {'cpu': total_cpu, 'memory': total_memory, 'gpu': total_gpu}

class Job:
    """Represents a job that contains multiple tasks and has dependencies.
    
    Attributes:
        job_id: Unique identifier for the job
        job_type: Type of job (batch_processing, machine_learning, etc.)
        tasks: List of tasks belonging to this job
        dependencies: List of job IDs this job depends on
        priority: Job priority (lower number means higher priority)
        status: Current status (pending, queued, preparing, running, paused, resuming, completed, failed, interrupted, throttled)
        start_time: When the job started running
        end_time: When the job finished or was interrupted
        retry_count: Number of times the job has been retried
        max_retries: Maximum number of times the job can be retried
        last_status_change: When the job's status was last changed
        throttle_reason: Reason for throttling the job
    """
    def __init__(self, job_id: str, job_type: str, priority: int = 0):
        """Initialize a new job with given type and priority."""
        self.job_id = job_id
        self.job_type = job_type
        self.tasks: List[Task] = []
        self.dependencies: List[str] = []  # List of job IDs this job depends on
        self.priority = priority  # Lower number means higher priority
        self.status = "pending"  # pending, queued, preparing, running, paused, resuming, completed, failed, interrupted, throttled
        self.start_time = None
        self.end_time = None
        self.retry_count = 0
        self.max_retries = 3
        self.last_status_change = None
        self.throttle_reason = None

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
        for task in self.tasks:
            resources = task.get_total_resources()
            total_cpu += resources['cpu']
            total_memory += resources['memory']
            total_gpu += resources['gpu']
        return {'cpu': total_cpu, 'memory': total_memory, 'gpu': total_gpu}
