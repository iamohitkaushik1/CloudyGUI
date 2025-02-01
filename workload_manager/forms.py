from django import forms

class WorkloadConfigForm(forms.Form):
    num_jobs = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Number of jobs to generate (1-100)'
    )
    tasks_per_job = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Number of tasks per job (1-20)'
    )
    instances_per_task = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=3,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Number of instances per task (1-10)'
    )
