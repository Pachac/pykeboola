from pykeboola.jobs import Jobs

class Client:
    """
    Object which hold the base url for Keboola and redirects user to individual objects
    to interact with via API calls.
    """
    base_url: str
    token: str
    jobs: Jobs
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.jobs = Jobs(base_url, token)
