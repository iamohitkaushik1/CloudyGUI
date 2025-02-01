from typing import Dict, List, Union
import random
from datetime import datetime, timedelta
import uuid

class Instance:
    """Represents a single instance of a task with its resource requirements and status.
    
    Attributes:
        instance_id: Unique identifier for the instance
        task_id: ID of the parent task
        cpu_usage: CPU usage in cores
        memory_usage: Memory usage in MB
        gpu_usage: GPU usage in units
        status: Current status (pending, running, terminated, interrupted)
        start_time: When the instance started running
        end_time: When the instance finished or was interrupted
        error_rate: Random value used to simulate failures
    """
    def __init__(self, instance_id: str, task_id: str, resources: Dict[str, float]):
        """Initialize a new instance with given resources."""
        self.instance_id = instance_id
        self.task_id = task_id
        self.cpu_usage = resources['cpu']
        self.memory_usage = resources['memory']
        self.gpu_usage = resources['gpu']
        self.status = 'pending'  # pending, running, terminated, interrupted
        self.start_time: Union[datetime, None] = None
        self.end_time: Union[datetime, None] = None
        self.error_rate = random.uniform(0, 1)  # Used to simulate failures

class Task:
    """Represents a task that contains multiple instances.
    
    Attributes:
        task_id: Unique identifier for the task
        job_id: ID of the parent job
        instances: List of instances belonging to this task
        required_resources: Resource requirements for each instance
    """
    def __init__(self, task_id: str, job_id: str, num_instances: int, required_resources: Dict[str, float]):
        """Initialize a new task and create its instances."""
        self.task_id = task_id
        self.job_id = job_id
        self.instances: List[Instance] = []
        self.required_resources = required_resources
        
        # Create instances for this task
        for i in range(num_instances):
            resources = {
                'cpu': required_resources['cpu'] * random.uniform(0.8, 1.2),
                'memory': required_resources['memory'] * random.uniform(0.8, 1.2),
                'gpu': required_resources['gpu'] * random.uniform(0.8, 1.2) if required_resources['gpu'] > 0 else 0
            }
            instance = Instance(f"{task_id}_instance_{i}", task_id, resources)
            self.instances.append(instance)

class Job:
    """Represents a job that contains multiple tasks and has dependencies.
    
    Attributes:
        job_id: Unique identifier for the job
        job_type: Type of job (batch_processing, machine_learning, etc.)
        tasks: List of tasks belonging to this job
        dependencies: List of job IDs this job depends on
        submit_time: When the job was submitted
        priority: Job priority (lower number means higher priority)
        estimated_duration: Estimated runtime in minutes
    """
    def __init__(self, job_id: str, job_type: str, priority: int = 0):
        """Initialize a new job with given type and priority."""
        self.job_id = job_id
        self.job_type = job_type
        self.tasks: List[Task] = []
        self.dependencies: List[str] = []  # List of job IDs this job depends on
        self.submit_time = datetime.now() - timedelta(minutes=random.randint(0, 60))
        self.priority = priority  # Lower number means higher priority
        self.estimated_duration = random.randint(5, 30)  # minutes

    def add_dependency(self, job_id: str) -> None:
        """Add a dependency to this job if it doesn't already exist."""
        if job_id not in self.dependencies:
            self.dependencies.append(job_id)
    
    def __lt__(self, other: 'Job') -> bool:
        """Compare jobs based on priority for sorting."""
        return self.priority < other.priority
    
    def __eq__(self, other: object) -> bool:
        """Check if two jobs have the same priority."""
        if not isinstance(other, Job):
            return NotImplemented
        return self.priority == other.priority
