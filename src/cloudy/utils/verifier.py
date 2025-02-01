def verify_workload_execution(scheduler, jobs):
    """Verify the correctness of workload execution"""
    verification_results = {
        'dependency_violations': 0,
        'resource_violations': 0,
        'invalid_transitions': 0
    }
    
    # Check dependency violations
    for job_id in scheduler.completed_jobs:
        job = next(j for j in jobs if j.job_id == job_id)
        for dep_id in job.dependencies:
            if dep_id not in scheduler.completed_jobs:
                verification_results['dependency_violations'] += 1
    
    # Check for invalid status transitions
    valid_transitions = {
        'pending': {'running', 'interrupted'},
        'running': {'terminated', 'interrupted'},
        'terminated': set(),  # Terminal state
        'interrupted': set()  # Terminal state
    }
    
    for entry in scheduler.status_history:
        if entry['new_status'] not in valid_transitions[entry['old_status']]:
            verification_results['invalid_transitions'] += 1
    
    return verification_results
