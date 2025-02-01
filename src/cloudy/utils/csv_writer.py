import csv

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
