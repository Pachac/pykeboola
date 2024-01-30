from conftest import URL, JOB_ID_SUCCESS, JOB_ID_ERROR, TEST_TRANS_SQL, TEST_TRANS_PY
from pykeboola.jobs import JobsClient
from datetime import datetime

def test_check_job_id(token):
    jobs = JobsClient(URL, token)
    assert jobs.check_job_status(JOB_ID_ERROR) == 'error'
    assert jobs.check_job_status(JOB_ID_SUCCESS) == 'success'

def test_queue_job(token):
    jobs = JobsClient(URL, token)
    values = [{
        "name": "test_datetime",
        "value": f"'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'"
    },
    {
        "name": "test_version",
        "value": f"1"
    }]
    job_id_sql = jobs.queue_job('keboola.snowflake-transformation',TEST_TRANS_SQL, values)
    job_id_py = jobs.queue_job('keboola.python-transformation-v2',TEST_TRANS_PY, values)
    assert int(job_id_sql) > 0
    assert int(job_id_py) > 0
    