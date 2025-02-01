from django import forms

class WorkloadConfigForm(forms.Form):
    num_jobs = forms.IntegerField(
        min_value=1,
        max_value=50000,  # Increased max jobs to 50,000
        initial=1000,
        label='Number of Jobs',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Total number of jobs to generate (1-50,000)'
    )
    tasks_per_job = forms.IntegerField(
        min_value=1,
        max_value=20,  # Increased max tasks to 20
        initial=5,
        label='Tasks per Job',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Maximum number of tasks per job (1-20)'
    )
    instances_per_task = forms.IntegerField(
        min_value=1,
        max_value=10,  # Increased max instances to 10
        initial=3,
        label='Instances per Task',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Maximum number of instances per task (1-10)'
    )
