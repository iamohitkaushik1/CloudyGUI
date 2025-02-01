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
            total_cpu = 0
            total_memory = 0
            total_gpu = 0
            total_disk = 0
            job_types = {}
            
            # Time-series data for line graphs
            timeline_data = []
            current_time = min(job.start_time for job in workload)
            end_time = max(job.end_time for job in workload)
            
            while current_time <= end_time:
                resources_at_time = {
                    'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'cpu': 0,
                    'memory': 0,
                    'gpu': 0,
                    'disk': 0,
                    'active_jobs': 0
                }
                
                for job in workload:
                    if job.start_time <= current_time <= job.end_time:
                        resources_at_time['active_jobs'] += 1
                        for task in job.tasks:
                            if task.start_time <= current_time <= task.end_time:
                                for instance in task.instances:
                                    if instance.start_time <= current_time <= instance.end_time:
                                        resources_at_time['cpu'] += instance.cpu_required
                                        resources_at_time['memory'] += instance.memory_required
                                        resources_at_time['gpu'] += instance.gpu_required
                                        resources_at_time['disk'] += instance.disk_required
                
                timeline_data.append(resources_at_time)
                current_time += timedelta(minutes=5)  # 5-minute intervals
            
            for job in workload:
                resources = job.get_total_resources()
                total_cpu += resources['cpu']
                total_memory += resources['memory']
                total_gpu += resources['gpu']
                total_disk += resources['disk']
                job_types[job.job_type] = job_types.get(job.job_type, 0) + 1

            # Prepare data for charts
            job_type_data = {
                'labels': list(job_types.keys()),
                'values': list(job_types.values())
            }

            stats = {
                'total_jobs': len(workload),
                'total_cpu': round(total_cpu, 2),
                'total_memory': round(total_memory / 1024, 2),  # Convert to GB
                'total_gpu': round(total_gpu, 2),
                'total_disk': round(total_disk, 2),  # In GB
                'job_types': job_type_data,
                'success': True,
                'output_file': 'workload_output.csv'
            }

            return render(request, 'workload_manager/generate.html', {
                'form': form,
                'stats': stats,
                'job_type_json': json.dumps(job_type_data),
                'timeline_json': json.dumps(timeline_data)
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
