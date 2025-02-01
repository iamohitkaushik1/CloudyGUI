from datetime import datetime, timedelta
from src.cloudy import (
    generate_workload,
    ResourceManager,
    Scheduler,
    save_to_csv,
    verify_workload_execution
)

def main():
    # Define total available resources
    total_resources = {
        'cpu': 100,  # 100 CPU cores
        'memory': 32000,  # 32 GB RAM
        'gpu': 4  # 4 GPU units
    }
    
    # Initialize resource manager and scheduler
    resource_manager = ResourceManager(total_resources)
    scheduler = Scheduler(resource_manager)
    
    # Generate workload
    print("Generating hierarchical workload with dependencies...")
    jobs = generate_workload(num_jobs=10)
    
    # Add all jobs to scheduler
    for job in jobs:
        scheduler.add_job(job)
    
    # Verify initial dependency graph
    try:
        scheduler.verify_dependencies()
        print("Initial dependency verification: PASSED")
    except ValueError as e:
        print(f"Initial dependency verification: FAILED - {str(e)}")
        return
    
    # Simulate scheduling for a period of time
    current_time = datetime.now()
    end_time = current_time + timedelta(hours=1)
    
    while current_time < end_time:
        # Schedule next batch of jobs
        scheduled_jobs = scheduler.schedule_next_batch(current_time)
        if scheduled_jobs:
            print(f"\nScheduled jobs at {current_time}:")
            for job in scheduled_jobs:
                print(f"- {job.job_id} (Type: {job.job_type}, Priority: {job.priority})")
        
        # Update job status
        scheduler.update_job_status(current_time)
        
        # Print status summary every 15 minutes of simulation time
        if current_time.minute % 15 == 0:
            status_counts = scheduler.get_status_summary()
            print(f"\nStatus Summary at {current_time}:")
            for status, count in status_counts.items():
                print(f"{status.capitalize()}: {count}")
        
        # Move time forward
        current_time += timedelta(minutes=5)
    
    # Verify workload execution
    verification_results = verify_workload_execution(scheduler, jobs)
    print("\nWorkload Execution Verification:")
    print(f"Dependency Violations: {verification_results['dependency_violations']}")
    print(f"Invalid Status Transitions: {verification_results['invalid_transitions']}")
    
    # Save final state to CSV
    output_file = 'generated_workloads/workload_output.csv'
    save_to_csv(jobs, scheduler, output_file)
    print(f"\nWorkload saved to {output_file}")
    
    # Print final summary
    total_tasks = sum(len(job.tasks) for job in jobs)
    total_instances = sum(sum(len(task.instances) for task in job.tasks) for job in jobs)
    print(f"\nFinal Workload Summary:")
    print(f"Total Jobs: {len(jobs)}")
    print(f"Total Tasks: {total_tasks}")
    print(f"Total Instances: {total_instances}")
    print(f"Completed Jobs: {len(scheduler.completed_jobs)}")
    print(f"Interrupted Jobs: {len(scheduler.interrupted_jobs)}")
    print(f"Running Jobs: {len(scheduler.running_jobs)}")
    print(f"Queued Jobs: {scheduler.job_queue.qsize()}")

if __name__ == "__main__":
    main()
