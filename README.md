# pykeboola
Python package for interacting with Keboola. I have just started this and will build it as needed for future development.
For now it includes only queueing jobs and checking on their statuses.

# How to use
You can use the `Client` class to gateway into individual functionalities:
```
from pykeboola import Client
client = Client('url', 'token')
```

For now there is only functionality for queueing jobs and checking their statuses. E.g.:
```
client.jobs.check_job_status(id_of_the_job)
```
