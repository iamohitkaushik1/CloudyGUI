import csv
import os

def save_to_csv(jobs, scheduler, filename='workload_output.csv'):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Job ID', 'Job Type', 'Priority', 'Dependencies', 'Submit Time',
                        'Task ID', 'Instance ID', 'Instance Status', 'Start Time', 'End Time',
                        'CPU Usage (%)', 'Memory Usage (MB)', 'GPU Usage (units)'])
        
        for job in jobs:
            deps = ','.join(job.dependencies) if job.dependencies else 'None'
            for task in job.tasks:
                for instance in task.instances:
                    writer.writerow([
                        job.job_id,
                        job.job_type,
                        job.priority,
                        deps,
                        job.submit_time.strftime('%Y-%m-%d %H:%M:%S'),
                        task.task_id,
                        instance.instance_id,
                        instance.status,
                        instance.start_time.strftime('%Y-%m-%d %H:%M:%S') if instance.start_time else 'Not Started',
                        instance.end_time.strftime('%Y-%m-%d %H:%M:%S') if instance.end_time else 'Not Finished',
                        f"{instance.cpu_usage:.2f}",
                        f"{instance.memory_usage:.2f}",
                        f"{instance.gpu_usage:.2f}"
                    ])

def write_workload_to_csv(workload, output_file):
    """
    Write workload data to a CSV file.
    
    Args:
        workload (list): List of Job objects
        output_file (str): Path to output CSV file
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Job ID', 
            'Job Type', 
            'Priority',
            'Job Status',
            'Dependencies',
            'Job Start Time',
            'Job End Time',
            'Task ID', 
            'Task Status',
            'Task Start Time',
            'Task End Time',
            'Instance ID', 
            'Instance Status',
            'Instance Start Time',
            'Instance End Time',
            'CPU', 
            'Memory (MB)', 
            'GPU',
            'Disk (GB)'
        ])
        
        for job in workload:
            for task in job.tasks:
                for instance in task.instances:
                    writer.writerow([
                        job.job_id,
                        job.job_type,
                        job.priority,
                        job.status,
                        ','.join(job.dependencies) if job.dependencies else '',
                        job.start_time.strftime('%Y-%m-%d %H:%M:%S') if job.start_time else '',
                        job.end_time.strftime('%Y-%m-%d %H:%M:%S') if job.end_time else '',
                        task.task_id,
                        task.status,
                        task.start_time.strftime('%Y-%m-%d %H:%M:%S') if task.start_time else '',
                        task.end_time.strftime('%Y-%m-%d %H:%M:%S') if task.end_time else '',
                        instance.instance_id,
                        instance.status,
                        instance.start_time.strftime('%Y-%m-%d %H:%M:%S') if instance.start_time else '',
                        instance.end_time.strftime('%Y-%m-%d %H:%M:%S') if instance.end_time else '',
                        round(instance.cpu_required, 2),
                        round(instance.memory_required, 2),
                        round(instance.gpu_required, 2),
                        round(instance.disk_required, 2)
                    ])
