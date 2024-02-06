import requests
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Table:
    id: str
    name: str
    schema: str
    schema_id: str
    description: str = field(default=None, compare=False)
    row_cnt: str = field(default=None, compare=False)
    columns: List = field(default_factory=list)
    native_types: bool = field(default=None, compare=False)

    @property
    def primary_keys(self) -> List: 
        return [column for column in self.columns if column.primary]
    
    @classmethod
    def from_keboola(cls, keboola_json: Dict):
        return cls(
            id = keboola_json['id'],
            name = keboola_json['displayName'],
            schema = keboola_json['bucket']['displayName'],
            schema_id = keboola_json['bucket']['id'],
            description = next(iter([meta['value'] for meta in keboola_json.get('metadata') or [] if meta['key'] == 'KBC.description']), None),
            row_cnt = keboola_json.get('rowsCount'),
            columns = Column.from_keboola(keboola_json.get('columnMetadata'), keboola_json.get('primaryKey'), keboola_json.get('columns')),
            native_types = keboola_json.get('isTyped')
        )
    
    def new_table(cls, name, schema_id, columns):
        return cls(
            id = None,
            name = name,
            schema = None,
            schema_id = schema_id,
            columns = columns
        )
        
@dataclass
class Column:
    name: str
    type: str
    descr: str = field(default=None, compare=False)
    primary: bool = field(default=False)
    length: str = field(default=None, compare=False)

    @classmethod
    def from_keboola(cls, column_metadata, primary_columns, columns) -> List:
        cols = []
        if column_metadata:
            for name, metadata in column_metadata.items():
                cols.append(cls(
                    name = name,
                    type = next(iter([meta['value'] for meta in metadata if meta['key'] == 'KBC.datatype.basetype' and meta['provider'] == 'storage']), None),
                    length = next(iter([meta['value'] for meta in metadata if meta['key'] == 'KBC.datatype.length' and meta['provider'] == 'storage']), None),
                    descr = next(iter([meta['value'] for meta in metadata if meta['key'] == 'KBC.description']), None),
                    primary = name in primary_columns
                ))
        elif columns:
            for name in columns:
                cols.append(cls(
                    name = name,
                    type = None,
                    length = None,
                    descr = None,
                    primary = name in primary_columns,
                ))
        return cols

class TablesClient:
    url: str
    token: str
    headers: dict
    def __init__(self, base_url: str, token: str):
        self.token = token
        self.url = f"{base_url.rstrip('/')}/v2/storage"
        self.headers = {
            'Content-Type': 'application/json',
            'X-StorageApi-Token': self.token
        }
    
    def get_tables(self) -> List[Table]:
        response = requests.get(f"{self.url}/tables?include=columns,buckets,metadata,columnMetadata", headers=self.headers)
        if response.status_code == 200:
            return [Table.from_keboola(table_json) for table_json in response.json()]
        else:
            err = response.text
            raise requests.HTTPError(f'Failed to retrieve tables from Keboola: {err}')
        
    def create_table(self, table: Table):
        url = f'{self.url}/buckets/{table.schema_id}/tables-definition'
        values = {
            "name": table.name,
            "primaryKeysNames": [column.name for column in table.primary_keys],
            "columns": [{"name": column.name,
                         "definition":
                         {
                             "type": column.type,
                             "length": column.length,
                         }} for column in table.columns]
        }
        response = requests.post(url, headers=self.headers, json=values)
        if response.status_code == 202:
            return response.json()['id']
        else:
            err = response.text
            raise requests.HTTPError(f'Failed to create table in Keboola: {err}\nBody: {values}')

    def delete_table(self, table_id):
        url = f'{self.url}/tables/{table_id}/?force=true'
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            return True
        else:
            err = response.text
            raise requests.HTTPError(f'Failed to delete table {table_id} in Keboola: {err}')