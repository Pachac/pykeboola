# pykeboola
Python package for interacting with Keboola. I have just started this and will build it as needed for future development.
For now it includes only queueing jobs and checking on their statuses and listing all tables available to the token.

# How to use
You can use the `Client` class to gateway into individual functionalities:
```
from pykeboola import Client
client = Client('url', 'token')
```

For queueing jobs and checking their statuses you can use E.g.:
```
client.jobs.check_job_status(id_of_the_job)
```
