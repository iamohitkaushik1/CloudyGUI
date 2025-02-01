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
        except DependencyError as e:
            logger.error(e)
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
                    
                    # Try to allocate resources
                    if self.resource_manager.can_allocate(total_required_resources):
                        self.resource_manager.allocate(total_required_resources)
                        
                        # Start all instances in the job
                        for task in job.tasks:
                            for instance in task.instances:
                                if instance.status == 'waiting':  # Only start waiting instances
                                    old_status = instance.status
                                    instance.status = 'running'
                                    instance.start_time = current_time
                                    # Set end time based on resource requirements
                                    duration = max(
                                        15,  # Minimum duration
                                        int(sum(instance.current_usage.values()) * random.uniform(0.8, 1.2))
                                    )
                                    instance.end_time = current_time + timedelta(minutes=duration)
                                    self.log_status_change(job.job_id, instance.instance_id, 
                                                        old_status, 'running', current_time)
                        
                        scheduled_jobs.append(job)
                        self.running_jobs[job.job_id] = (job, total_required_resources)
                        logger.info(f"Scheduled job {job.job_id}")
                    else:
                        # Put the job back in the queue if we can't schedule it now
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
            # Make sure skipped jobs are put back in the queue even if there's an error
            for priority, job in skipped_jobs:
                self.job_queue.put((priority, job))
            raise
    
    def update_job_status(self, current_time):
        """Update status of running jobs with error handling."""
        completed_job_ids = []
        
        try:
            # Check for completed jobs and possible interruptions
            for job_id, (job, resources) in list(self.running_jobs.items()):
                job_status = {'terminated': 0, 'running': 0, 'interrupted': 0, 'waiting': 0, 'failed': 0}
                
                for task in job.tasks:
                    for instance in task.instances:
                        old_status = instance.status
                        
                        try:
                            # Update instance resource usage
                            instance.update_usage(current_time)
                            
                            if instance.status == 'running':
                                # Check for completion
                                if instance.end_time <= current_time:
                                    # 90% chance of successful completion, 10% chance of failure
                                    if random.random() < 0.9:
                                        instance.status = 'terminated'
                                    else:
                                        instance.status = 'failed'
                                    self.log_status_change(job_id, instance.instance_id, 
                                                        old_status, instance.status, current_time)
                                # Check for random interruptions (5% chance per update)
                                elif instance.error_rate > 0.95:
                                    instance.status = 'interrupted'
                                    instance.end_time = current_time
                                    self.log_status_change(job_id, instance.instance_id, 
                                                        old_status, 'interrupted', current_time)
                            
                            job_status[instance.status] += 1
                        except Exception as e:
                            logger.error(f"Error updating instance {instance.instance_id}: {str(e)}")
                            # Mark instance as interrupted if there's an error
                            instance.status = 'interrupted'
                            instance.end_time = current_time
                            job_status['interrupted'] += 1
                
                # Update task and job status
                for task in job.tasks:
                    task.update_status()
                job.update_status()
                
                # Handle job completion or interruption
                if job_status['interrupted'] > 0 or job_status['failed'] > 0:
                    self.interrupted_jobs.add(job_id)
                    self.resource_manager.release(resources)
                    del self.running_jobs[job_id]
                    logger.info(f"Job {job_id} interrupted or failed")
                elif job_status['running'] == 0 and job_status['waiting'] == 0:
                    # All instances are terminated
                    if job_status['terminated'] > 0:
                        completed_job_ids.append(job_id)
                        self.completed_jobs.add(job_id)
                        logger.info(f"Job {job_id} completed successfully")
                    self.resource_manager.release(resources)
                    del self.running_jobs[job_id]
            
            # Check if any waiting jobs can now start
            newly_available_jobs = []
            for job_id in completed_job_ids:
                for successor in self.dependency_graph.successors(job_id):
                    job = next((j for j in self.all_jobs if j.job_id == successor), None)
                    if job and self._can_start(job):
                        newly_available_jobs.append(job)
            
            # Add newly available jobs to queue
            for job in newly_available_jobs:
                self.job_queue.put((job.priority, job))
                logger.info(f"Job {job.job_id} now available for scheduling")
                
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
