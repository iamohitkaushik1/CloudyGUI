import csv
import os
from datetime import datetime

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
    Write workload data to a CSV file with enhanced information.
    
    Args:
        workload (list): List of Job objects
        output_file (str): Path to output CSV file
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    current_time = datetime.now()
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Job ID',
            'Job Type',
            'Task ID',
            'Task Type',
            'Priority',
            'Dependencies',
            'Instance ID', 
            'Instance Status',
            'Instance Start Time',
            'Instance End Time',
            'CPU Required',
            'CPU Usage',
            'Memory Required (MB)',
            'Memory Usage (MB)',
            'GPU Required',
            'GPU Usage',
            'Disk Required (GB)',
            'Disk Usage (GB)'
        ])
        
        for job in workload:
            # Update resource usage for all instances
            for task in job.tasks:
                for instance in task.instances:
                    instance.update_usage(current_time)
                    
                    writer.writerow([
                        job.job_id,
                        job.job_type,
                        task.task_id,
                        task.task_type,
                        job.priority,
                        ','.join(job.dependencies) if job.dependencies else '',
                        instance.instance_id,
                        instance.status,
                        instance.start_time.strftime('%Y-%m-%d %H:%M:%S') if instance.start_time else 'Not Started',
                        instance.end_time.strftime('%Y-%m-%d %H:%M:%S') if instance.end_time else 'Not Finished',
                        f"{instance.cpu_required:.2f}",
                        f"{instance.current_usage['cpu']:.2f}",
                        f"{instance.memory_required:.2f}",
                        f"{instance.current_usage['memory']:.2f}",
                        f"{instance.gpu_required:.2f}",
                        f"{instance.current_usage['gpu']:.2f}",
                        f"{instance.disk_required:.2f}",
                        f"{instance.current_usage['disk']:.2f}"
                    ])
