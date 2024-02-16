import requests
from dataclasses import dataclass, field, fields
from typing import List, Dict

@dataclass
class Table:
    """
    Represents a table in a database.

    Attributes:
        id (str): The ID of the table.
        name (str): The name of the table.
        schema (str): The schema of the table.
        schema_id (str): The ID of the schema.
        description (str, optional): The description of the table.
        row_cnt (str, optional): The row count of the table.
        columns (List, optional): The list of columns in the table.
        native_types (bool, optional): Indicates if the table has native types.

    Methods:
        primary_keys() -> List: Returns a list of primary key columns.
        from_keboola(keboola_json: Dict) -> Table: Creates a Table instance from a Keboola JSON.
        new_table(name, schema_id, columns) -> Table: Creates a new Table instance.
        __sub__(other) -> Dict: Compares two tables and returns the differences.
    """
    id: str = field(compare=False)
    name: str
    schema: str
    schema_id: str = field(compare=False)
    description: str = field(default=None)
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
    
    @classmethod
    def new_table(cls, name, schema_id, columns):
        return cls(
            id = None,
            name = name,
            schema = None,
            schema_id = schema_id,
            columns = columns
        )
    
    def __sub__(self, other):
        differences = {}
        for field in fields(self):
            if field.compare and getattr(self, field.name) != getattr(other, field.name):
                differences[field.name] = (getattr(self, field.name), getattr(other, field.name))
        
        if 'columns' in differences:
            col_dif = {}
            self_col_dict = {column.name: column for column in self.columns}
            other_col_dict = {column.name: column for column in other.columns}
            for col_name in self_col_dict:
                if col_name in other_col_dict:
                    dif = self_col_dict[col_name] - other_col_dict[col_name]
                    if dif:
                        col_dif[col_name] = dif
                else:
                    col_dif[col_name] = 'Left Only'
            for col_name in other_col_dict:
                if not col_name in self_col_dict:
                    col_dif[col_name] = 'Right Only'
            if col_dif:
                differences['columns'] = col_dif
            else:
                differences.pop('columns')
        
        return differences

@dataclass
class Column:
    """
    Represents a column in a table.

    Attributes:
        name (str): The name of the column.
        type (str): The data type of the column.
        description (str, optional): The description of the column. Defaults to None.
        primary (bool, optional): Indicates if the column is a primary key. Defaults to False.
        length (str, optional): The length of the column. Defaults to None.
    """

    name: str
    type: str
    description: str = field(default=None)
    primary: bool = field(default=False)
    length: str = field(default=None)

    @classmethod
    def from_keboola(cls, column_metadata, primary_columns, columns) -> List:
        cols = []
        if column_metadata:
            for name, metadata in column_metadata.items():
                cols.append(cls(
                    name = name,
                    type = next(iter([meta['value'] for meta in metadata if meta['key'] == 'KBC.datatype.basetype' and meta['provider'] == 'storage']), None),
                    length = next(iter([meta['value'] for meta in metadata if meta['key'] == 'KBC.datatype.length' and meta['provider'] == 'storage']), None),
                    description = next(iter([meta['value'] for meta in metadata if meta['key'] == 'KBC.description']), None),
                    primary = name in primary_columns
                ))
        elif columns:
            for name in columns:
                cols.append(cls(
                    name = name,
                    type = None,
                    length = None,
                    description = None,
                    primary = name in primary_columns,
                ))
        return cols
    
    def __sub__(self, other):
        differences = {}
        for field in fields(self):
            if field.compare and getattr(self, field.name) != getattr(other, field.name):
                differences[field.name] = (getattr(self, field.name), getattr(other, field.name))
        return differences
    

class TablesClient:
    """
    Client for interacting with tables in Keboola.

    Args:
        base_url (str): The base URL of the Keboola API.
        token (str): The API token for authentication.

    Attributes:
        url (str): The complete URL for the Keboola storage API.
        token (str): The API token for authentication.
        headers (dict): The headers to be included in API requests.

    Methods:
        get_tables(bucket: str = None) -> List[Table]: Retrieves a list of tables from Keboola.
        create_table(table: Table): Creates a new table in Keboola.
        delete_table(table_id): Deletes a table from Keboola.
        update_table_metadata(table: Table): Updates the metadata of a table in Keboola.
    """

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
    
    def get_tables(self, bucket: str = None) -> List[Table]:
        """
        Retrieves a list of tables from Keboola.

        Args:
            bucket (str, optional): The name of the bucket to filter tables by. Defaults to None.

        Returns:
            List[Table]: A list of Table objects representing the tables retrieved from Keboola.

        Raises:
            requests.HTTPError: If the request to Keboola fails.
        """
        if bucket:
            url = f"{self.url}/buckets/{bucket}/tables?include=columns,buckets,metadata,columnMetadata"
        else:
            url = f"{self.url}/tables?include=columns,buckets,metadata,columnMetadata"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return [Table.from_keboola(table_json) for table_json in response.json()]
        else:
            err = response.text
            raise requests.HTTPError(f'Failed to retrieve tables from Keboola: {err}')
        
    def create_table(self, table: Table):
        """
        Creates a new table in Keboola.

        Args:
            table (Table): The Table object representing the table to be created.

        Returns:
            str: The ID of the created table.

        Raises:
            requests.HTTPError: If the request to Keboola fails.
        """
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
        """
        Deletes a table from Keboola.

        Args:
            table_id: The ID of the table to be deleted.

        Returns:
            bool: True if the table was successfully deleted.

        Raises:
            requests.HTTPError: If the request to Keboola fails.
        """
        url = f'{self.url}/tables/{table_id}/?force=true'
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            return True
        else:
            err = response.text
            raise requests.HTTPError(f'Failed to delete table {table_id} in Keboola: {err}')
        
    def update_table_metadata(self, table: Table):
        """
        Updates the metadata of a table in Keboola.

        Args:
            table (Table): The Table object representing the table to update.

        Returns:
            dict: The response JSON containing the updated metadata.

        Raises:
            requests.HTTPError: If the request to Keboola fails.
        """
        url = f'{self.url}/tables/{table.id}/metadata'
        values = {
            'provider': 'user',
        }
        if table.description:
            values['metadata'] = [
                {
                    'key': 'KBC.description',
                    'value': table.description
                }
            ]

        if table.columns:
            values['columnsMetadata'] = {
                column.name: [{
                    'key': 'KBC.description', 
                    'value': column.description
                    }]
                for column in table.columns}
        
        response = requests.post(url, headers=self.headers, json=values)
        if response.status_code == 201:
            return response.json()
        else:
            err = response.text
            raise requests.HTTPError(f'Failed to add metadata to table in Keboola: {err}\nBody: {values}')