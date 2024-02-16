from pykeboola.jobs import JobsClient
from pykeboola.tables import TablesClient

class Client:
    """
    Object which holds the base URL for Keboola and redirects the user to individual objects
    to interact with via API calls.

    Attributes:
        base_url (str): The base URL for Keboola.
        token (str): The authentication token for API calls.
        jobs (JobsClient): The client for interacting with jobs via API calls.
        tables (TablesClient): The client for interacting with tables via API calls.
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
