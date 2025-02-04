from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, FileResponse
import os
import json
from datetime import datetime, timedelta
from .forms import WorkloadConfigForm
from src.cloudy.utils.workload_generator import generate_workload
from src.cloudy.utils.csv_writer import write_workload_to_csv

# Create your views here.

def generate_workload_view(request):
    if request.method == 'POST':
        form = WorkloadConfigForm(request.POST)
        if form.is_valid():
            num_jobs = form.cleaned_data['num_jobs']
            tasks_per_job = form.cleaned_data['tasks_per_job']
            instances_per_task = form.cleaned_data['instances_per_task']

            # Generate workload
            workload = generate_workload(
                num_jobs=num_jobs,
                tasks_per_job=tasks_per_job,
                instances_per_task=instances_per_task
            )

            # Save to CSV
            output_file = os.path.join(settings.GENERATED_WORKLOADS_DIR, 'workload_output.csv')
            write_workload_to_csv(workload, output_file)

            # Calculate resource statistics for visualization
            current_time = datetime.now()
            total_resources = {
                'cpu': 0,
                'memory': 0,
                'gpu': 0,
                'disk': 0
            }
            job_types = {}
            job_statuses = {
                'waiting': 0,
                'running': 0,
                'terminated': 0,
                'failed': 0,
                'interrupted': 0
            }
            
            # Time-series data for line graphs
            timeline_data = []
            
            # Get jobs with start and end times
            jobs_with_start = [job for job in workload if job.start_time]
            jobs_with_end = [job for job in workload if job.end_time]
            
            # Check if we have any jobs with times
            if not jobs_with_start or not jobs_with_end:
                # Handle the case where no jobs have start/end times
                current_time = datetime.now()
                start_time = current_time - timedelta(hours=1)  # Default to 1 hour ago
                end_time = current_time
            else:
                start_time = min(job.start_time for job in jobs_with_start)
                end_time = max(job.end_time for job in jobs_with_end)
            
            # Generate timeline data points
            current = start_time
            while current <= end_time:
                resources_at_time = {
                    'time': current.strftime('%Y-%m-%d %H:%M:%S'),
                    'cpu': 0,
                    'memory': 0,
                    'gpu': 0,
                    'disk': 0,
                    'active_jobs': 0,
                    'waiting_jobs': 0,
                    'failed_jobs': 0,
                    'terminated_jobs': 0,
                    'interrupted_jobs': 0
                }
                
                # Update all instances' resource usage at this time
                for job in workload:
                    # Update job and task statuses
                    for task in job.tasks:
                        for instance in task.instances:
                            # Only update and count resources if the instance is active at this time
                            if instance.start_time and instance.start_time <= current:
                                if not instance.end_time or current <= instance.end_time:
                                    instance.update_usage(current)
                                    current_usage = instance.current_usage
                                    resources_at_time['cpu'] += current_usage['cpu']
                                    resources_at_time['memory'] += current_usage['memory']
                                    resources_at_time['gpu'] += current_usage['gpu']
                                    resources_at_time['disk'] += current_usage['disk']
                        task.update_status()
                    job.update_status()
                    
                    # Count job types
                    job_types[job.job_type] = job_types.get(job.job_type, 0) + 1
                    
                    # Track job status at current time
                    if job.start_time and job.start_time <= current:
                        if not job.end_time or current <= job.end_time:
                            if job.status == 'failed':
                                resources_at_time['failed_jobs'] += 1
                            elif job.status == 'waiting':
                                resources_at_time['waiting_jobs'] += 1
                            elif job.status == 'running':
                                resources_at_time['active_jobs'] += 1
                            elif job.status == 'terminated':
                                resources_at_time['terminated_jobs'] += 1
                            elif job.status == 'interrupted':
                                resources_at_time['interrupted_jobs'] += 1
                
                timeline_data.append(resources_at_time)
                current += timedelta(minutes=5)  # 5-minute intervals
            
            # Calculate final statistics
            for job in workload:
                job_statuses[job.status] += 1
                resources = job.get_total_resources()
                for resource in total_resources:
                    total_resources[resource] += resources[resource]
            
            # Track instance status distribution
            instance_status_counts = {
                'running': 0,
                'waiting': 0,
                'failed': 0,
                'terminated': 0,
                'interrupted': 0
            }
            
            for job in workload:
                for task in job.tasks:
                    for instance in task.instances:
                        status = instance.status.lower()
                        if status in instance_status_counts:
                            instance_status_counts[status] += 1
                        elif status == 'interrupted':
                            instance_status_counts['interrupted'] += 1

            # Prepare instance status data for the chart
            instance_status_data = {
                'labels': list(instance_status_counts.keys()),
                'values': list(instance_status_counts.values())
            }

            # Prepare job type distribution data
            job_type_data = {
                'labels': list(job_types.keys()),
                'values': list(job_types.values())
            }
            
            # Prepare job status distribution data
            job_status_data = {
                'labels': list(job_statuses.keys()),
                'values': list(job_statuses.values())
            }

            stats = {
                'total_jobs': len(workload),
                'total_cpu': round(total_resources['cpu'], 2),
                'total_memory': round(total_resources['memory'] / 1024, 2),  # Convert to GB
                'total_gpu': round(total_resources['gpu'], 2),
                'total_disk': round(total_resources['disk'], 2),  # In GB
                'job_statuses': job_statuses,
                'success': True,
                'output_file': 'workload_output.csv'
            }

            # Convert data to JSON for template
            timeline_json = json.dumps(timeline_data)
            job_type_json = json.dumps(job_type_data)
            instance_status_json = json.dumps(instance_status_data)

            return render(request, 'workload_manager/generate.html', {
                'form': form,
                'stats': stats,
                'job_type_json': job_type_json,
                'job_status_json': json.dumps(job_status_data),
                'instance_status_json': instance_status_json,
                'timeline_json': timeline_json
            })
    else:
        form = WorkloadConfigForm()

    return render(request, 'workload_manager/generate.html', {'form': form})

def download_workload(request):
    file_path = os.path.join(settings.GENERATED_WORKLOADS_DIR, 'workload_output.csv')
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = 'attachment; filename="workload_output.csv"'
        return response
    return HttpResponse("File not found", status=404)
