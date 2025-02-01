class ResourceManager:
    def __init__(self, total_resources):
        self.total_resources = total_resources
        self.available_resources = total_resources.copy()
    
    def can_allocate(self, required_resources):
        return all(
            self.available_resources[resource] >= required_resources[resource]
            for resource in required_resources
        )
    
    def allocate(self, required_resources):
        if self.can_allocate(required_resources):
            for resource in required_resources:
                self.available_resources[resource] -= required_resources[resource]
            return True
        return False
    
    def release(self, resources):
        for resource in resources:
            self.available_resources[resource] += resources[resource]
