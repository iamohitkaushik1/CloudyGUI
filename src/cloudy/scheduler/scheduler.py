from queue import PriorityQueue
from datetime import datetime, timedelta
import networkx as nx
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerError(Exception):
    """Base class for Scheduler exceptions"""
    pass

class ResourceAllocationError(SchedulerError):
    """Raised when resource allocation fails"""
    pass

class DependencyError(SchedulerError):
    """Raised when there are dependency issues"""
    pass

class Scheduler:
    def __init__(self, resource_manager):
        """Initialize the scheduler with a resource manager."""
        self.resource_manager = resource_manager
        self.job_queue = PriorityQueue()
        self.running_jobs = {}
        self.completed_jobs = set()
        self.interrupted_jobs = set()
        self.dependency_graph = nx.DiGraph()
        self.status_history = []
        self.all_jobs = []
        
        # Simplified cloud-like behavior settings
        self.preemption_grace_period = timedelta(minutes=2)  # Standard cloud preemption notice
        self.spot_instance_probability = 0.6  # 60% chance of spot instances
        self.instance_types = {
            'standard': {'preemption_probability': 0.1, 'cost_multiplier': 1.0},
            'spot': {'preemption_probability': 0.3, 'cost_multiplier': 0.3}
        }
        
        # Resource quotas (simplified to one zone)
        self.zone_quotas = {
            'cpu': self.resource_manager.total_resources['cpu'] * 0.8,
            'memory': self.resource_manager.total_resources['memory'] * 0.8,
            'gpu': self.resource_manager.total_resources['gpu'] * 0.8
        }
    
    def add_job(self, job):
        """Add a job to the scheduler with error handling."""
        try:
            # Add job to dependency graph
            self.dependency_graph.add_node(job.job_id)
            for dep in job.dependencies:
                if not any(j.job_id == dep for j in self.all_jobs):
                    raise DependencyError(f"Dependency {dep} not found for job {job.job_id}")
                self.dependency_graph.add_edge(dep, job.job_id)
            
            # Verify no cycles are created
            if not nx.is_directed_acyclic_graph(self.dependency_graph):
                raise DependencyError(f"Adding job {job.job_id} would create a circular dependency")
            
            # Store job in all_jobs list
            self.all_jobs.append(job)
            
            # Add to priority queue if no dependencies or all dependencies are met
            if self._can_start(job):
                self.job_queue.put((job.priority, job))
            
            logger.info(f"Added job {job.job_id} to scheduler")
        except Exception as e:
            logger.error(f"Error adding job {job.job_id}: {str(e)}")
            raise
    
    def _can_start(self, job):
        """Check if a job can start based on its dependencies."""
        return all(dep in self.completed_jobs for dep in job.dependencies)
    
    def verify_dependencies(self):
        """Verify that all dependencies are valid with error handling."""
        try:
            for node in self.dependency_graph.nodes():
                for dep in self.dependency_graph.predecessors(node):
                    if dep not in self.dependency_graph.nodes():
                        raise DependencyError(f"Invalid dependency: {dep} for job {node}")
            
            if not nx.is_directed_acyclic_graph(self.dependency_graph):
                raise DependencyError("Circular dependency detected in job graph")
            
            logger.info("All dependencies verified successfully")
        except Exception as e:
            logger.error(f"Dependency verification failed: {str(e)}")
            raise
    
    def log_status_change(self, job_id, instance_id, old_status, new_status, time):
        """Log a status change with error handling."""
        try:
            self.status_history.append({
                'job_id': job_id,
                'instance_id': instance_id,
                'old_status': old_status,
                'new_status': new_status,
                'time': time
            })
            logger.debug(f"Status change logged: {job_id} instance {instance_id}: {old_status} -> {new_status}")
        except Exception as e:
            logger.error(f"Error logging status change: {str(e)}")
    
    def schedule_next_batch(self, current_time):
        """Schedule the next batch of jobs with error handling."""
        scheduled_jobs = []
        skipped_jobs = []
        
        try:
            while not self.job_queue.empty():
                priority, job = self.job_queue.get()
                
                try:
                    # Get total required resources for the job
                    total_required_resources = job.get_total_resources()
                    
                    # Check zone quotas
                    if not self._check_zone_quotas(total_required_resources):
                        logger.info(f"Job {job.job_id} exceeds zone quotas, will retry later")
                        skipped_jobs.append((priority, job))
                        continue
                    
                    # Check if we need to preempt lower priority jobs
                    if not self.resource_manager.can_allocate(total_required_resources):
                        # Find running jobs with lower priority that can be preempted
                        preemptable_jobs = []
                        available_resources = {}
                        
                        for running_job_id, (running_job, resources) in self.running_jobs.items():
                            if running_job.priority > priority:  # Lower priority = higher number
                                # Check if job is using spot instances
                                is_spot = self._is_spot_instance(running_job)
                                if is_spot or self._should_preempt(running_job, job):
                                    preemptable_jobs.append((running_job_id, running_job, resources))
                                    # Accumulate resources that could be freed
                                    for resource, amount in resources.items():
                                        available_resources[resource] = available_resources.get(resource, 0) + amount
                                    
                        # Check if preempting would free enough resources
                        can_preempt = all(
                            available_resources.get(resource, 0) >= amount
                            for resource, amount in total_required_resources.items()
                        )
                        
                        if can_preempt:
                            # Sort preemptable jobs by cost-effectiveness
                            preemptable_jobs.sort(key=lambda x: self._calculate_preemption_cost(x[1]))
                            
                            # Preempt jobs until we have enough resources
                            needed_resources = total_required_resources.copy()
                            for job_id, running_job, resources in preemptable_jobs:
                                if all(needed_resources.get(r, 0) <= 0 for r in needed_resources):
                                    break
                                    
                                # Give grace period for preemption
                                self._schedule_preemption(job_id, running_job, resources, current_time)
                                
                                # Update needed resources
                                for resource, amount in resources.items():
                                    if resource in needed_resources:
                                        needed_resources[resource] -= amount
                    
                    # Try to allocate resources
                    if self.resource_manager.can_allocate(total_required_resources):
                        self.resource_manager.allocate(total_required_resources)
                        
                        # Start all instances in the job
                        for task in job.tasks:
                            for instance in task.instances:
                                if instance.status in ['waiting', 'interrupted']:
                                    old_status = instance.status
                                    instance.status = 'running'
                                    instance.start_time = current_time
                                    
                                    # Set spot instance attributes if applicable
                                    if random.random() < self.spot_instance_probability:
                                        instance.is_spot = True
                                        instance.spot_price = self._calculate_spot_price()
                                    
                                    # Set end time based on resource requirements and instance type
                                    duration = self._calculate_instance_duration(instance)
                                    instance.end_time = current_time + timedelta(minutes=duration)
                                    
                                    # Set up checkpointing intervals if spot instance
                                    if getattr(instance, 'is_spot', False):
                                        instance.next_checkpoint = current_time + timedelta(minutes=5)
                                    
                                    self.log_status_change(job.job_id, instance.instance_id, 
                                                        old_status, 'running', current_time)
                        
                        scheduled_jobs.append(job)
                        self.running_jobs[job.job_id] = (job, total_required_resources)
                        logger.info(f"Scheduled job {job.job_id}")
                    else:
                        skipped_jobs.append((priority, job))
                        logger.debug(f"Insufficient resources for job {job.job_id}, skipping")
                except Exception as e:
                    logger.error(f"Error scheduling job {job.job_id}: {str(e)}")
                    skipped_jobs.append((priority, job))
            
            # Put skipped jobs back in the queue
            for priority, job in skipped_jobs:
                self.job_queue.put((priority, job))
            
            return scheduled_jobs
        except Exception as e:
            logger.error(f"Error in schedule_next_batch: {str(e)}")
            for priority, job in skipped_jobs:
                self.job_queue.put((priority, job))
            raise

    def _check_zone_quotas(self, required_resources):
        """Check if required resources are within zone quotas."""
        return all(
            required_resources.get(resource, 0) <= quota
            for resource, quota in self.zone_quotas.items()
        )

    def _is_spot_instance(self, job):
        """Check if job is running on spot instances."""
        return any(
            getattr(instance, 'is_spot', False)
            for task in job.tasks
            for instance in task.instances
        )

    def _should_preempt(self, running_job, new_job):
        """Simplified preemption decision based on key factors."""
        if running_job.priority > new_job.priority:  # Lower number = higher priority
            # Don't preempt if job is almost done
            if self._get_job_progress(running_job) > 0.8:
                return False
            
            # Spot instances are more likely to be preempted
            if self._is_spot_instance(running_job):
                return True
            
            # For standard instances, only preempt if significant priority difference
            return running_job.priority > new_job.priority + 2
        
        return False

    def _calculate_preemption_cost(self, job):
        """Calculate the cost of preempting a job based on simplified metrics."""
        progress = self._get_job_progress(job)
        resource_cost = sum(sum(instance.current_usage.values()) 
                          for task in job.tasks 
                          for instance in task.instances)
        
        # Simplified cost calculation focusing on key factors
        cost = (
            progress * 50 +                    # Progress weight
            resource_cost * 0.3 +              # Resource usage weight
            (1 / (job.priority + 1)) * 20 +    # Priority weight
            (1 if self._is_spot_instance(job) else 2) * 10  # Instance type weight
        )
        
        return cost

    def _get_job_progress(self, job):
        """Calculate job progress as a percentage."""
        total_instances = 0
        completed_instances = 0
        
        for task in job.tasks:
            for instance in task.instances:
                total_instances += 1
                if instance.status in ['terminated', 'failed']:
                    completed_instances += 1
                elif instance.status == 'running':
                    # Calculate partial progress
                    if instance.end_time and instance.start_time:
                        total_time = (instance.end_time - instance.start_time).total_seconds()
                        elapsed_time = (datetime.now() - instance.start_time).total_seconds()
                        completed_instances += min(1.0, elapsed_time / total_time)
        
        return completed_instances / total_instances if total_instances > 0 else 0

    def _calculate_spot_price(self):
        """Calculate spot instance price based on market conditions."""
        base_price = 0.1  # Base price per hour
        # Simulate market fluctuations
        return base_price * random.uniform(0.8, 2.0)

    def _calculate_instance_duration(self, instance):
        """Calculate instance duration with simplified variability."""
        base_duration = max(
            15,  # Minimum duration
            int(sum(instance.current_usage.values()) * random.uniform(0.8, 1.2))
        )
        
        # Spot instances have more variable duration
        if getattr(instance, 'is_spot', False):
            base_duration = int(base_duration * random.uniform(0.5, 1.0))
        
        return base_duration

    def _schedule_preemption(self, job_id, job, resources, current_time):
        """Schedule a job for preemption with grace period."""
        try:
            # Set preemption warning time
            preemption_time = current_time + self.preemption_grace_period
            
            for task in job.tasks:
                for instance in task.instances:
                    if instance.status == 'running':
                        # Trigger checkpoint if spot instance
                        if getattr(instance, 'is_spot', False):
                            self._checkpoint_instance(instance, current_time)
                        
                        old_status = instance.status
                        instance.status = 'preempting'  # New status for grace period
                        instance.preemption_time = preemption_time
                        self.log_status_change(job_id, instance.instance_id,
                                            old_status, 'preempting', current_time)
            
            logger.info(f"Job {job_id} scheduled for preemption at {preemption_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling preemption for job {job_id}: {str(e)}")
            raise

    def _checkpoint_instance(self, instance, current_time):
        """Simulate checkpointing of instance state."""
        try:
            # Record checkpoint time
            instance.last_checkpoint = current_time
            instance.next_checkpoint = current_time + timedelta(minutes=5)
            logger.debug(f"Checkpoint created for instance {instance.instance_id}")
        except Exception as e:
            logger.error(f"Error checkpointing instance {instance.instance_id}: {str(e)}")

    def update_job_status(self, current_time):
        """Update status of running jobs with realistic failure patterns."""
        completed_job_ids = []
        
        try:
            for job_id, (job, resources) in list(self.running_jobs.items()):
                job_status = {'terminated': 0, 'running': 0, 'interrupted': 0, 
                            'waiting': 0, 'failed': 0, 'preempting': 0}
                
                for task in job.tasks:
                    for instance in task.instances:
                        old_status = instance.status
                        
                        try:
                            # Update instance resource usage
                            instance.update_usage(current_time)
                            
                            if instance.status == 'running':
                                # Handle normal completion
                                if instance.end_time <= current_time:
                                    instance.status = 'terminated' if random.random() < 0.9 else 'failed'
                                    self.log_status_change(job_id, instance.instance_id, 
                                                        old_status, instance.status, current_time)
                                
                                # Handle spot instance preemption
                                elif getattr(instance, 'is_spot', False):
                                    preemption_prob = self.instance_types['spot']['preemption_probability']
                                    if random.random() < preemption_prob:
                                        instance.status = 'preempting'
                                        instance.preemption_time = current_time + self.preemption_grace_period
                                        self.log_status_change(job_id, instance.instance_id,
                                                            old_status, 'preempting', current_time)
                            
                            # Handle instances in preemption grace period
                            elif instance.status == 'preempting':
                                if current_time >= instance.preemption_time:
                                    instance.status = 'interrupted'
                                    self.log_status_change(job_id, instance.instance_id,
                                                        'preempting', 'interrupted', current_time)
                            
                            job_status[instance.status] += 1
                            
                        except Exception as e:
                            logger.error(f"Error updating instance {instance.instance_id}: {str(e)}")
                            instance.status = 'failed'
                            job_status['failed'] += 1
                
                # Update job status based on instance states
                if job_status['failed'] > 0:
                    job.status = 'failed'
                elif job_status['interrupted'] > 0:
                    job.status = 'interrupted'
                    self.interrupted_jobs.add(job_id)
                elif job_status['preempting'] > 0:
                    job.status = 'preempting'
                elif job_status['running'] > 0:
                    job.status = 'running'
                elif job_status['terminated'] == len([i for t in job.tasks for i in t.instances]):
                    job.status = 'terminated'
                    completed_job_ids.append(job_id)
                    self.completed_jobs.add(job_id)
                
                # Release resources for completed/failed/interrupted jobs
                if job.status in ['terminated', 'failed', 'interrupted']:
                    self.resource_manager.release(resources)
                    del self.running_jobs[job_id]
                    
                    # Requeue interrupted jobs
                    if job.status == 'interrupted':
                        self.job_queue.put((job.priority, job))
            
            return completed_job_ids
            
        except Exception as e:
            logger.error(f"Error in update_job_status: {str(e)}")
            raise
    
    def get_status_summary(self):
        """Get a summary of job statuses with error handling."""
        try:
            status_counts = {
                'waiting': 0,
                'running': 0,
                'terminated': 0,
                'interrupted': 0,
                'failed': 0
            }
            
            for job in self.all_jobs:
                status_counts[job.status] += 1
            
            return status_counts
        except Exception as e:
            logger.error(f"Error getting status summary: {str(e)}")
            return {status: 0 for status in ['waiting', 'running', 'terminated', 'interrupted', 'failed']}
