from queue import PriorityQueue
from datetime import timedelta
import networkx as nx
import random

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
        import random
        completed_job_ids = []
        
        # Define possible status transitions and their probabilities
        # Increased probabilities for terminal states and reduced waiting times
        instance_transitions = {
            'pending': [('provisioning', 0.95), ('failed', 0.05)],  # Quick transition from pending
            'provisioning': [('starting', 0.9), ('failed', 0.1)],   # Faster provisioning
            'starting': [('running', 0.95), ('failed', 0.05)],      # Quick startup
            'running': [
                ('running', 0.4),      # 40% chance to keep running
                ('terminated', 0.3),   # 30% chance to complete
                ('degraded', 0.15),    # 15% chance to degrade
                ('unhealthy', 0.1),    # 10% chance to become unhealthy
                ('stopping', 0.05)     # 5% chance to stop
            ],
            'degraded': [
                ('running', 0.4),      # 40% chance to recover
                ('unhealthy', 0.3),    # 30% chance to get worse
                ('stopping', 0.3)      # 30% chance to stop
            ],
            'unhealthy': [
                ('running', 0.2),      # 20% chance to recover
                ('stopping', 0.5),     # 50% chance to stop
                ('failed', 0.3)        # 30% chance to fail
            ],
            'stopping': [('terminated', 0.95), ('failed', 0.05)]    # Quick termination
        }
        
        # Adjusted job transitions for better flow
        job_transitions = {
            'pending': [('queued', 0.9), ('failed', 0.1)],
            'queued': [('preparing', 0.8), ('throttled', 0.15), ('failed', 0.05)],
            'preparing': [('running', 0.9), ('failed', 0.05), ('throttled', 0.05)],
            'running': [
                ('running', 0.3),      # 30% chance to keep running
                ('completed', 0.4),    # 40% chance to complete
                ('paused', 0.15),      # 15% chance to pause
                ('interrupted', 0.1),  # 10% chance to interrupt
                ('failed', 0.05)       # 5% chance to fail
            ],
            'paused': [('resuming', 0.8), ('failed', 0.2)],
            'resuming': [('running', 0.9), ('failed', 0.1)],
            'throttled': [('preparing', 0.8), ('failed', 0.2)],
            'interrupted': [('preparing', 0.7), ('failed', 0.3)]
        }
        
        # Maximum time limits for each state (in seconds)
        max_state_duration = {
            'pending': 300,        # 5 minutes
            'provisioning': 180,   # 3 minutes
            'starting': 120,       # 2 minutes
            'running': 3600,       # 1 hour
            'degraded': 600,       # 10 minutes
            'unhealthy': 300,      # 5 minutes
            'stopping': 180,       # 3 minutes
            'queued': 600,        # 10 minutes
            'preparing': 300,      # 5 minutes
            'paused': 1800,       # 30 minutes
            'resuming': 180,       # 3 minutes
            'throttled': 900      # 15 minutes
        }
        
        # Check for completed jobs and status transitions
        for job_id, (job, resources) in list(self.running_jobs.items()):
            instance_status_counts = {
                'pending': 0, 'provisioning': 0, 'starting': 0, 'running': 0,
                'degraded': 0, 'unhealthy': 0, 'stopping': 0, 'terminated': 0, 'failed': 0
            }
            
            # Force status change if in state too long
            if hasattr(job, 'last_status_change') and job.last_status_change:
                time_in_state = (current_time - job.last_status_change).total_seconds()
                if job.status in max_state_duration and time_in_state > max_state_duration[job.status]:
                    if job.status in ['pending', 'queued', 'preparing', 'provisioning', 'starting']:
                        job.status = 'failed'
                    elif job.status in ['running', 'degraded', 'unhealthy']:
                        job.status = 'stopping'
                    elif job.status in ['paused', 'resuming', 'throttled']:
                        job.status = 'preparing'
            
            # Update job status based on conditions and randomization
            if job.status in job_transitions:
                transitions = job_transitions[job.status]
                rand_val = random.random()
                cumulative_prob = 0
                
                for new_status, prob in transitions:
                    cumulative_prob += prob
                    if rand_val <= cumulative_prob:
                        old_status = job.status
                        
                        # Apply special conditions
                        if new_status == 'failed' and job.retry_count < job.max_retries:
                            job.retry_count += 1
                            new_status = 'preparing'
                        elif new_status == 'throttled':
                            job.throttle_reason = random.choice([
                                'resource_limit_exceeded',
                                'rate_limit_reached',
                                'system_maintenance'
                            ])
                        
                        job.status = new_status
                        job.last_status_change = current_time
                        self.log_status_change(job_id, None, old_status, new_status, current_time)
                        break
            
            # Update instance statuses independently
            for task in job.tasks:
                for instance in task.instances:
                    # Force instance status change if in state too long
                    if instance.last_health_check:
                        time_in_state = (current_time - instance.last_health_check).total_seconds()
                        if instance.status in max_state_duration and time_in_state > max_state_duration[instance.status]:
                            if instance.status in ['pending', 'provisioning', 'starting']:
                                instance.status = 'failed'
                            elif instance.status in ['running', 'degraded', 'unhealthy']:
                                instance.status = 'stopping'
                    
                    # Update performance metrics
                    instance.update_performance_metrics()
                    
                    # Handle health checks
                    if instance.status == 'running':
                        if not instance.is_healthy():
                            instance.health_check_failures += 1
                            if instance.health_check_failures >= 3:
                                instance.status = 'unhealthy'
                        else:
                            instance.health_check_failures = 0
                    
                    # Apply random status transitions with time-based progression
                    if instance.status in instance_transitions:
                        transitions = instance_transitions[instance.status]
                        rand_val = random.random()
                        cumulative_prob = 0
                        
                        for new_status, prob in transitions:
                            cumulative_prob += prob
                            if rand_val <= cumulative_prob:
                                old_status = instance.status
                                
                                # Handle special cases
                                if new_status == 'failed' and instance.restart_count < instance.max_restarts:
                                    instance.restart_count += 1
                                    new_status = 'starting'
                                    
                                instance.status = new_status
                                if new_status == 'running' and not instance.start_time:
                                    instance.start_time = current_time
                                elif new_status in ['terminated', 'failed']:
                                    instance.end_time = current_time
                                
                                instance.last_health_check = current_time
                                self.log_status_change(job_id, instance.instance_id, 
                                                    old_status, new_status, current_time)
                                break
                    
                    instance_status_counts[instance.status] += 1
            
            # Determine job status based on instance states with adjusted thresholds
            total_instances = sum(instance_status_counts.values())
            failed_instances = instance_status_counts['failed']
            terminated_instances = instance_status_counts['terminated']
            running_instances = instance_status_counts['running']
            healthy_instances = running_instances + instance_status_counts['degraded']
            
            # Update job status based on instance health with more aggressive completion
            if terminated_instances / total_instances >= 0.8:
                job.status = 'completed'
            elif failed_instances / total_instances >= 0.5:
                job.status = 'failed'
            elif healthy_instances / total_instances < 0.3:
                job.status = 'interrupted'
            
            # Handle job completion or removal
            if job.status in ['completed', 'failed']:
                if job.status == 'completed':
                    completed_job_ids.append(job_id)
                    self.completed_jobs.add(job_id)
                else:
                    self.interrupted_jobs.add(job_id)
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
            'queued': 0,
            'preparing': 0,
            'running': 0,
            'paused': 0,
            'resuming': 0,
            'completed': 0,
            'failed': 0,
            'interrupted': 0,
            'throttled': 0
        }
        
        # Count job statuses
        for job in self.all_jobs:
            if hasattr(job, 'status'):
                status_counts[job.status] = status_counts.get(job.status, 0) + 1
        
        return status_counts
