from pykeboola.tables import TablesClient, Table, Column
from pykeboola import Client
from conftest import URL
import json
import time

def test_get_tables(token):
    tables = TablesClient(URL, token)
    assert type(tables.get_tables()) == list
    assert type(tables.get_tables()[0]) == Table

def test_table_from_keboola():
    with open('tests/test_tables.json', 'r') as reader:
        json_list = json.loads(reader.read())
    
    for table_json in json_list:
        table = Table.from_keboola(table_json)
        assert table.id == table_json['id']
        assert table.name == table_json['displayName']
        assert table.schema_id == table_json['bucket']['id']
        assert table.schema == table_json['bucket']['displayName']
        assert table.description == next(iter([meta['value'] for meta in table_json['metadata'] or [] if meta['key'] == 'KBC.description']), None)
        assert table.row_cnt == table_json['rowsCount']
        assert table.native_types == table_json['isTyped']
        assert table.columns == Column.from_keboola(table_json['columnMetadata'], table_json['primaryKey'], table_json['columns'])

def test_table_from_keboola_no_meta():
    with open('tests/test_table_no_meta.json', 'r') as reader:
        json_dict = json.loads(reader.read())
    table = Table.from_keboola(json_dict)
    assert table.name == 'BULK_EXEC_TEST'
    assert table.schema == 'BULK_EXEC_TEST'
    assert table.description == None
    assert table.row_cnt == 1
    assert table.columns == []
    assert table.primary_keys == []

def test_table_create_delete_api_job(token):
    client = Client(URL, token)
    col1 = Column('TEST_COL1', 'VARCHAR', primary=True)
    col2 = Column('TEST_COL2', 'DATETIME')
    table = Table(
        id = None,
        name = 'PYTEST_TEST',
        schema_id = 'out.c-NATIVE_TABLE_TEST',
        schema = None,
        columns=[col1, col2],
    )
    job_id = client.tables.create_table(table)
    status = client.jobs.check_api_job_status(job_id)
    timeout = 10
    timer = 0
    while status != 'success':
        if status == 'error':
            raise ValueError('Table creation returned an error')
        
        timer += 1
        if timer > timeout:
            raise TimeoutError('Waiting for table creation is timing out.')
        time.sleep(1)
        status = client.jobs.check_api_job_status(job_id)
    delete_status = client.tables.delete_table(f'{table.schema_id}.{table.name}')
    assert delete_status == True
    
