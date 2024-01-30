from pykeboola.tables import TablesClient, Table, Column
from conftest import URL
import json

def test_get_tables(token):
    tables = TablesClient(URL, token)
    assert type(tables.get_tables()) == list
    assert type(tables.get_tables()[0]) == Table

def test_table_from_keboola():
    with open('tests/test_table.json', 'r') as reader:
        json_dict = json.loads(reader.read())
    table = Table.from_keboola(json_dict)
    assert table.name == 'BULK_EXEC_TEST'
    assert table.schema == 'BULK_EXEC_TEST'
    assert table.description == 'This is a test description to see in the Storage API'
    assert table.row_cnt == 1
    columns = Column.from_column_metadata(json_dict['columnMetadata'], json_dict['primaryKey'])
    assert table.columns == columns
    assert table.primary_keys == [columns[0]]

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