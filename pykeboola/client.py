from pykeboola.jobs import JobsClient
from pykeboola.tables import TablesClient

class Client:
    """
    Object which hold the base url for Keboola and redirects user to individual objects
    to interact with via API calls.
    """
    base_url: str
    token: str
    jobs: JobsClient
    tables: TablesClient
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.jobs = JobsClient(base_url, token)
        self.tables = TablesClient(base_url, token)
