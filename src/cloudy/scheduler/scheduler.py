from queue import PriorityQueue
from datetime import timedelta
import networkx as nx

class Scheduler:
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.job_queue = PriorityQueue()
        self.running_jobs = {}
        self.completed_jobs = set()
        self.interrupted_jobs = set()
        self.dependency_graph = nx.DiGraph()
        self.status_history = []  # Track status changes for verification
        self.all_jobs = []  # Store all jobs
    
    def add_job(self, job):
        # Add job to dependency graph
        self.dependency_graph.add_node(job.job_id)
        for dep in job.dependencies:
            self.dependency_graph.add_edge(dep, job.job_id)
        
        # Store job in all_jobs list
        self.all_jobs.append(job)
        
        # Add to priority queue if no dependencies or all dependencies are met
        if self._can_start(job):
            self.job_queue.put((job.priority, job))
    
    def _can_start(self, job):
        return all(dep in self.completed_jobs for dep in job.dependencies)
    
    def verify_dependencies(self):
        """Verify that all dependencies are valid"""
        for node in self.dependency_graph.nodes():
            for dep in self.dependency_graph.predecessors(node):
                if dep not in self.dependency_graph.nodes():
                    raise ValueError(f"Invalid dependency: {dep} for job {node}")
        
        if not nx.is_directed_acyclic_graph(self.dependency_graph):
            raise ValueError("Circular dependency detected in job graph")
    
    def log_status_change(self, job_id, instance_id, old_status, new_status, time):
        self.status_history.append({
            'job_id': job_id,
            'instance_id': instance_id,
            'old_status': old_status,
            'new_status': new_status,
            'time': time
        })
    
    def schedule_next_batch(self, current_time):
        # Try to schedule as many jobs as possible
        scheduled_jobs = []
        skipped_jobs = []
        
        while not self.job_queue.empty():
            priority, job = self.job_queue.get()
            
            # Calculate total required resources for the job
            total_required_resources = {
                'cpu': 0,
                'memory': 0,
                'gpu': 0
            }
            
            for task in job.tasks:
                for resource in total_required_resources:
                    total_required_resources[resource] += task.required_resources[resource]
            
            # Try to allocate resources
            if self.resource_manager.can_allocate(total_required_resources):
                self.resource_manager.allocate(total_required_resources)
                
                # Start all instances in the job
                for task in job.tasks:
                    for instance in task.instances:
                        old_status = instance.status
                        instance.status = 'running'
                        instance.start_time = current_time
                        instance.end_time = current_time + timedelta(minutes=job.estimated_duration)
                        self.log_status_change(job.job_id, instance.instance_id, 
                                            old_status, 'running', current_time)
                
                scheduled_jobs.append(job)
                self.running_jobs[job.job_id] = (job, total_required_resources)
            else:
                # Put the job back in the queue if we can't schedule it now
                skipped_jobs.append((priority, job))
        
        # Put skipped jobs back in the queue
        for job in skipped_jobs:
            self.job_queue.put(job)
        
        return scheduled_jobs
    
    def update_job_status(self, current_time):
        completed_job_ids = []
        
        # Check for completed jobs and possible interruptions
        for job_id, (job, resources) in list(self.running_jobs.items()):
            job_status = {'terminated': 0, 'running': 0, 'interrupted': 0, 'pending': 0}
            
            for task in job.tasks:
                for instance in task.instances:
                    old_status = instance.status
                    
                    # Check for random interruptions (5% chance per update)
                    if instance.status == 'running' and instance.error_rate > 0.95:
                        instance.status = 'interrupted'
                        instance.end_time = current_time
                        self.log_status_change(job_id, instance.instance_id, old_status, 'interrupted', current_time)
                    
                    # Check for completion
                    elif instance.status == 'running' and instance.end_time <= current_time:
                        instance.status = 'terminated'
                        self.log_status_change(job_id, instance.instance_id, old_status, 'terminated', current_time)
                    
                    job_status[instance.status] += 1
            
            # Determine overall job status
            if job_status['interrupted'] > 0:
                self.interrupted_jobs.add(job_id)
                self.resource_manager.release(resources)
                del self.running_jobs[job_id]
            elif job_status['running'] == 0 and job_status['pending'] == 0:
                # All instances are either terminated or interrupted
                if job_status['terminated'] > 0:
                    completed_job_ids.append(job_id)
                    self.completed_jobs.add(job_id)
                self.resource_manager.release(resources)
                del self.running_jobs[job_id]
        
        # Check if any waiting jobs can now start
        newly_available_jobs = []
        for job_id in completed_job_ids:
            for successor in self.dependency_graph.successors(job_id):
                job = next(j for j in self.all_jobs if j.job_id == successor)
                if self._can_start(job):
                    newly_available_jobs.append(job)
        
        # Add newly available jobs to queue
        for job in newly_available_jobs:
            self.job_queue.put((job.priority, job))
    
    def get_status_summary(self):
        status_counts = {
            'pending': 0,
            'running': 0,
            'terminated': 0,
            'interrupted': 0
        }
        
        for job_id, (job, _) in self.running_jobs.items():
            for task in job.tasks:
                for instance in task.instances:
                    status_counts[instance.status] += 1
        
        return status_counts
