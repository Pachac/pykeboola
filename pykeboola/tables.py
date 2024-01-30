import requests
from dataclasses import dataclass, field

@dataclass
class Table:
    name: str
    schema: str
    description: str = field(compare=False)
    row_cnt: str = field(default=None, compare=False)
    columns: list = field(default_factory=list)

    @property
    def primary_keys(self) -> list: 
        return [column for column in self.columns if column.primary]
    
    @classmethod
    def from_keboola(cls, keboola_json: dict):
        return cls(
            name = keboola_json['displayName'],
            schema = keboola_json['bucket']['displayName'],
            description = next(iter([meta['value'] for meta in keboola_json.get('metadata') or [] if meta['key'] == 'KBC.description']), None),
            row_cnt = keboola_json.get('rowsCount'),
            columns = Column.from_column_metadata(keboola_json.get('columnMetadata'), keboola_json.get('primaryKey'))
        )
        
@dataclass
class Column:
    name: str
    type: str
    descr: str = field(compare=False)
    primary: bool
    length: str = field(default=None, compare=False)

    @classmethod
    def from_column_metadata(cls, column_metadata, primary_columns) -> list:
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
        return cols




class TablesClient:
    url: str
    token: str
    headers: dict
    def __init__(self, base_url: str, token: str):
        self.token = token
        self.url = f"{base_url.rstrip('/')}/v2/storage/tables"
        self.headers = {
            'Content-Type': 'application/json',
            'X-StorageApi-Token': self.token
        }
    
    def get_tables(self) -> list[Table]:
        response = requests.get(f"{self.url}?include=buckets,metadata,columnMetadata", headers=self.headers)
        if response.status_code == 200:
            return [Table.from_keboola(table_json) for table_json in response.json()]
        else:
            err = response.text
            raise requests.HTTPError(f'Failed to retrieve tables from Keboola: {err}')