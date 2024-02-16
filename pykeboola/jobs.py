import requests
from typing import Dict

class JobsClient:
    """
    Class to interact with jobs in Keboola queue.

    Attributes:
        queue_url (str): The URL of the Keboola queue.
        token (str): The API token for authentication.

    Methods:
        __init__(base_url: str, token: str): Initializes a new instance of the JobsClient class.
        queue_job(component_id: str, configuration_id: int, variable_values: dict = None, branch_id: int = None): Queues a job in Keboola.
        check_job_status(job_id): Checks the status of a job.
        get_job(job_id): Gets all information about a queue job.
        check_api_job_status(job_id): Checks the status of an API job.
        get_api_job(job_id): Gets all information about an API job.
    """
    queue_url: str
    token: str

    def __init__(self, base_url: str, token: str):
        self.queue_url = base_url.replace('connection', 'queue').rstrip('/')
        self.storage_url = f'{base_url.rstrip("/")}/v2/storage'
        self.token = token

    def queue_job(self, component_id: str, configuration_id: int, variable_values: dict = None, branch_id: int = None):
        """
        Queues a job in Keboola. Returns job_id and raises error on response codes >= 400.

        Args:
            component_id (str): The ID of the component.
            configuration_id (int): The ID of the configuration.
            variable_values (dict, optional): The variable values for the job. Defaults to None.
            branch_id (int, optional): The ID of the branch. Defaults to None.

        Returns:
            str: The ID of the queued job.
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
        response = requests.post(f'{self.queue_url}/jobs', headers=headers, json=body)
        if response.status_code >= 400:
            err = response.text
            raise requests.HTTPError(f"Failed to queue a job in Keboola. API Response: {err}")
        
        return response.json()['id']
    
    def check_job_status(self, job_id) -> str:
        """
        Checks the status of the job. Returns current status.

        Args:
            job_id: The ID of the job.

        Returns:
            str: The current status of the job.
        """
        return self.get_job(job_id)['status']
    
    def get_job(self, job_id) -> Dict:
        """
        Gets all info about a queue job.

        Args:
            job_id: The ID of the job.

        Returns:
            dict: All information about the queue job.
        """
        url = f'{self.queue_url}/jobs/{job_id}'
        headers = {
            'Content-Type': 'application/json',
            'X-StorageApi-Token': self.token
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 400:
            err = response.text
            raise requests.HTTPError(f"Failed to find a job in Keboola. API Response: {err}")
        return response.json()
    
    def check_api_job_status(self, job_id) -> str:
        """
        Checks the status of the job. Returns current status.

        Args:
            job_id: The ID of the job.

        Returns:
            str: The current status of the job.
        """
        return self.get_api_job(job_id)['status']

    def get_api_job(self, job_id):
        """
        Gets all info about an API job.

        Args:
            job_id: The ID of the job.

        Returns:
            dict: All information about the API job.
        """
        url = f'{self.storage_url}/jobs/{job_id}'
        headers = {
            'Content-Type': 'application/json',
            'X-StorageApi-Token': self.token
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 400:
            err = response.text
            raise requests.HTTPError(f"Failed to find a job in Keboola. API Response: {err}")
        return response.json()
