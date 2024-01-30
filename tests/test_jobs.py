from conftest import URL, JOB_ID_SUCCESS, JOB_ID_ERROR
from pykeboola.jobs import JobsClient

def test_check_job_id(token):
    jobs = JobsClient(URL, token)
    assert jobs.check_job_status(JOB_ID_ERROR) == 'error'
    assert jobs.check_job_status(JOB_ID_SUCCESS) == 'success'