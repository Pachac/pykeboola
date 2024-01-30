import requests

class JobsClient:
    """
    Class to interact with jobs in Keboola queue.
    """
    queue_url: str
    token: str

    def __init__(self, base_url: str, token: str):
        self.queue_url = base_url.replace('connection', 'queue').rstrip('/')
        self.token = token

    def queue_job(self, component_id: str, configuration_id: int, variable_values: dict = None, branch_id: int = None):
        """
        Queues a job in Keboola. Returns job_id and raises error on response codes >= 400.
        """
        body = {
        'component': component_id,
        'config': configuration_id,
        'mode': 'run',
        }
        if variable_values:
            body['variableValuesData'] = {'values': variable_values}
        if branch_id:
            body['branchId'] = branch_id
        headers = {
            'X-StorageApi-Token': self.token
        }
        response = requests.post(f'{self.queue_job}/jobs', headers=headers, json=body)
        if response.status_code >= 400:
            err = response.text
            raise requests.HTTPError(f"Failed to queue a job in Keboola. API Response: {err}")
        
        return response.json()['id']
    
    def check_job_status(self, job_id) -> str:
        """
        Checks the status of the job. Returns current status.
        """
        url = f'{self.queue_url}/jobs/{job_id}'
        headers = {
            'Content-Type': 'application/json',
            'X-StorageApi-Token': self.token
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 400:
            err = response.text
            raise requests.HTTPError(f"Failed to queue a job in Keboola. API Response: {err}")
        return response.json()['status']