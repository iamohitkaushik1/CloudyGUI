import random
import uuid
from datetime import datetime, timedelta
from ..core.models import Job, Task, Instance, predefined_vms, job_profiles

def generate_workload(num_jobs=10, tasks_per_job=5, instances_per_task=3):
    """
    Generate a workload with specified number of jobs, tasks per job, and instances per task.
    
    Args:
        num_jobs (int): Number of jobs to generate
        tasks_per_job (int): Number of tasks per job
        instances_per_task (int): Number of instances per task
    
    Returns:
        list: List of Job objects
    """
    jobs = []
    base_time = datetime.now()

    for i in range(num_jobs):
        job = Job(f"job_{uuid.uuid4().hex[:8]}", random.choice([jp.profile_name for jp in job_profiles]), priority=random.randint(1, 5))
        job.start_time = base_time + timedelta(minutes=random.randint(0, 60))
        job.end_time = job.start_time + timedelta(minutes=random.randint(30, 180))

        # Find the job profile based on the job type
        job_profile = next((jp for jp in job_profiles if jp.profile_name == job.job_type), None)

        # Allocate a VM based on the job profile
        allocated_vm = None
        for vm in predefined_vms:
            if (vm.cpu >= job_profile.cpu_required and 
                vm.memory >= job_profile.memory_required and 
                vm.gpu >= job_profile.gpu_required):
                allocated_vm = vm
                break

        if allocated_vm is None:
            raise Exception(f"No suitable VM found for job {job.job_id} with profile {job_profile.profile_name}")

        # Generate tasks for each job
        for j in range(tasks_per_job):
            task = Task(f"{job.job_id}_task_{j}", job.job_id)
            task.start_time = job.start_time + timedelta(minutes=random.randint(0, 30))
            task.end_time = task.start_time + timedelta(minutes=random.randint(15, 90))

            # Generate instances for each task
            for k in range(instances_per_task):
                instance = Instance(
                    f"{task.task_id}_instance_{k}",
                    task.task_id,
                    cpu_required=job_profile.cpu_required,
                    memory_required=job_profile.memory_required,
                    gpu_required=job_profile.gpu_required,
                    disk_required=0  # Set as needed
                )
                instance.start_time = task.start_time + timedelta(minutes=random.randint(0, 15))
                instance.end_time = instance.start_time + timedelta(minutes=random.randint(5, 45))

                # Set status based on time
                if instance.end_time < datetime.now():
                    instance.status = "completed"
                elif instance.start_time < datetime.now():
                    instance.status = "running"

                # Assign instance to the allocated VM
                allocated_vm.add_instance(instance)
                task.instances.append(instance)

            # Update task status based on instance statuses
            if all(i.status == "completed" for i in task.instances):
                task.status = "completed"
            elif any(i.status == "running" for i in task.instances):
                task.status = "running"

            job.tasks.append(task)

        # Update job status based on task statuses
        if all(t.status == "completed" for t in job.tasks):
            job.status = "completed"
        elif any(t.status == "running" for t in job.tasks):
            job.status = "running"

        jobs.append(job)

    # Add some random dependencies (ensuring no cycles)
    for i, job in enumerate(jobs):
        # Can only depend on jobs that come before this one to avoid cycles
        if i > 0:
            # 30% chance to add a dependency
            if random.random() < 0.3:
                dependency_job = random.choice(jobs[:i])
                job.add_dependency(dependency_job.job_id)

    return jobs
