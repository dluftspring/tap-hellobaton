"""
Command line utility to generate schema files from the baton swagger open API spec https://app.hellobaton.com/api/swagger.json.
"""

import glob
import json
import ast
import operator
from os import PathLike
from typing import Any, Iterable, List, Mapping, Tuple, Generator
from pathlib import Path
from functools import reduce
from jsonschema import Draft7Validator
from .templates import STREAM_TEMPLATE
import requests
import dictdiffer
import pandas as pd
import click


SWAGGER_URL: str = 'https://app.hellobaton.com/api/swagger.json'
# for the first few cycles of this implementation, we will only allow the swagger spec to add properties to our schemas
# we will not allow the swagger spec to remove properties or change existing properties that a human has already validated
ALLOWED_CHANGES = ['add']

class OpenApiSpec(object):

    """
    Base object that processes the open api spec from swagger
    """

    def __init__(self):

        self.spec = self._get_spec()
        self.url = SWAGGER_URL

    def _get_spec(self) -> dict:
        response = requests.get(SWAGGER_URL)
        assert response.status_code == 200, "Failed to get swagger spec from {}".format(SWAGGER_URL)
        return response.json()

    def openapi_to_jsonschema(self, openapi_schema: dict) -> dict:

        """
        Convert OpenAPI schema into valid json schema
        """

        json_schema = dict(required=list(), type='object', properties=dict())
        json_schema['required'] = openapi_schema.get('required', list())

        # restrict openAPI schema metadata we extract
        valid_keys = ['type', 'format']
        for key, value in openapi_schema['properties'].items():

            # if the value is a reference to another schema, we need to extract the object properties of the reference
            ref_value = value.get('$ref', None)
            complex_type = None
            properties = None
            if ref_value:
                schema_ref = value.get('$ref').split('/')[-1]
                complex_type = self.spec['definitions'][schema_ref]['type']
                # Recurse here because the nested objects conform to openAPI not jsonschema
                properties = self.openapi_to_jsonschema(self.spec['definitions'][schema_ref])['properties']

            type = value.get('type', complex_type or 'string')
            format = value.get('format', None)

            if 'x-nullable' in value.keys():
                type = [type]
                type.append("null")

            json_schema['properties'][key] = dict(type=type)

            # We have to add format only where it exists. Not all entries of json schema have a format string
            if format:
                json_schema['properties'][key]['format'] = format

            # Same idea as above but for the properties of complex json objects like arrays and nested json blobs
            if properties:
                json_schema['properties'][key]['properties'] = properties


        return json_schema


    def convert_to_schemas(self) -> Mapping[str, dict]:

        """
        Parse the spec for all available endpoints and return a dictionary of valid json schemas. This method validates the schema against Draft7.
        NOTE: This method will not validate json instances against the schema produced it only checks for internal validity of the schema itself.
        """

        schemas = {}
        for path in self.spec['paths']:
            if not ('{' in path or '}' in path):
                for method in self.spec['paths'][path]:
                    if method == 'get':
                        # Convert the openAPI paths e.g. /{endpoint}/ to 'endpoint' so they can be valid dictionary keys
                        schema_key = path.replace('/','')
                        # Get the relevant schema definition path from the response
                        definition = self.spec['paths'][path][method]['responses']['200']['schema']['properties']['results']['items']['$ref'].split('/')[-1]
                        valid_schema = self.openapi_to_jsonschema(self.spec['definitions'][definition])

                        schemas[schema_key] = valid_schema

                        # This check should return None if it passes
                        assert Draft7Validator.check_schema(valid_schema) is None, "Schema {} is not valid".format(schema_key)

        return schemas

class SchemaUpdater(object):

    """
    Determines which schemas to update and writes them to the schemas directory
    """

    def __init__(self, new_schemas: Mapping[str, dict], allowed_changes: List[str] = ALLOWED_CHANGES):
        self.new_schemas = new_schemas
        self.schema_dir: PathLike =  Path(__file__).parent.parent / Path('tap_hellobaton') / Path('schemas')
        self.existing_schemas: Mapping[str, dict] = self._read_schemas()
        self.allowed_changes: List[str] = allowed_changes
        self.updated_schemas: Mapping[str, dict] = { k:{} for k in self.new_schemas.keys() }
        self.list_of_modified_schemas: List[str] = list()
        self.list_of_new_schemas: List[str] = list()

    def _read_schemas(self) -> Mapping[str, dict]:
        """
        Reads all schemas from the tap schemas directory
        """

        schemas = {}
        for schema_file in glob.glob(str(self.schema_dir) + '/*.json'):
            with open(schema_file) as f:
                dict_key = schema_file.split('/')[-1].split('.')[0]
                schemas[dict_key] = json.load(f)

        return schemas

    def _track_schema_changes(self, json_path: str, raw_path: str) -> None:
        """
        Tracking whether or not schemas are being updated or newly created
        based on the output dictdiffer.diff(<old>, <new>)
        """
        if isinstance(json_path, list):
                schema = json_path[0]
            #@TODO - clunky to construct this then split it
        else:
            schema = json_path.split('.')[0]

        if schema not in self.list_of_modified_schemas:
            #@TODO - a bit clunky to check for this twice
            if not raw_path:
                self.list_of_new_schemas.append(schema)
            self.list_of_modified_schemas.append(schema)


    def _process_changes(self, diff: Generator[Tuple, None, None]) -> pd.DataFrame:

        """
        Process the incoming changeset into a more readable dataframe with the follow structure

        | type | path | change | old_value | new_value |
        |------|------|--------|-----------|-----------|
        | add  | actor.name | <raw changes> | None | John Doe |

        where
            type - the type of change e.g. add, change, remove
            path - the path of the schema being changed separated by dots e.g. key1.key2.key3
            old_value - the existing value of the schema at the path specified before the change
            new_value - the incoming change to the schema at the path specified
        """

        init_dict = dict(type=list(), path=list(), old_value=list(), new_value=list())

        for t, p, c in diff:
            if t in ['add', 'remove']:
                change_type = t

                for change in c:
                    # If a completely new schema is being added, the path is going to be missing or root so we get the path from the first entry of the changeset
                    print(p, change)
                    json_path = '.'.join([p, str(change[0])]) if p else change[0]
                    new_value = None if t == 'remove' else change[1]
                    old_value = None if t == 'add' else change[1]
                    self._track_schema_changes(json_path, p)

            elif t == 'change':
                change_type = t
                json_path = p
                old_value = c[0]
                new_value = c[1]
            else:
                raise ValueError("Unknown change type {}".format(t))

            init_dict['type'].append(change_type)
            init_dict['path'].append(json_path)
            init_dict['old_value'].append(old_value)
            init_dict['new_value'].append(new_value)

        diff_df = pd.DataFrame(init_dict)
        return diff_df

    def update_schemas(self) -> None:
        """
        Update schemas and write to a new directory called schemas
        """

        for key in self.existing_schemas.keys():
            self.updated_schemas[key] = self.existing_schemas[key]

        for path in self.calculate_diff():
            schema_path = path.split('.')
            leaf_to_set = schema_path[-1]
            new_val = reduce(operator.getitem, schema_path, self.new_schemas)
            reduce(operator.getitem, schema_path[:-1], self.updated_schemas)[leaf_to_set] = new_val

        for key in self.updated_schemas.keys():
            with open(str(self.schema_dir) + '/' + key + '.json', 'w') as f:
                json.dump(self.updated_schemas[key], f, indent=4)


    def calculate_diff(self) -> List[str]:
        """
        Summarize the changes being written into the schemas directory

        :returns: A list of keys that should be updated with the values in self.new_schemas
        """

        raw_diff = dictdiffer.diff(self.existing_schemas, self.new_schemas)
        keys_to_update = []

        for type, path, changes in raw_diff:
            if type in self.allowed_changes:
                for change in changes:
                    dict_path = '.'.join([path, change[0]])
                    if not path:
                        dict_path = change[0]
                    keys_to_update.append(dict_path)

        return keys_to_update

    def change_report(self) -> None:
        """
        Print a report of the changes being written into the schemas directory
        """
        raw_diff = dictdiffer.diff(self.existing_schemas, self.new_schemas)
        diff = self._process_changes(raw_diff)

        print("INFO - Your allowed changes are {}".format(self.allowed_changes))
        print(diff.loc[diff.type.isin(self.allowed_changes)].to_markdown(index=False))



class AstSchemaTemplate(object):

    """
    AST template class required for safely modifying this repositories python files
    """
    def __init__(self, new_streams: List[str]):
        self.stream_template: str = STREAM_TEMPLATE
        self.stream_path: PathLike = Path(__file__).parent.parent / Path('tap_hellobaton') / Path('streams.py')
        self.tap_path: PathLike = Path(__file__).parent.parent / Path('tap_hellobaton') / Path('tap.py')
        self.new_streams = new_streams

    def read_streams(self) -> ast.Module:
        """
        Reads the streams.py file and returns the contents of the abstract syntax tree
        """
        with open(self.stream_path) as f:
            return ast.parse(f.read())

    def read_tap(self) -> ast.Module:
        """
        Reads the tap.py file and returns the contents
        """
        with open(self.tap_path) as f:
            return ast.parse(f.read())

    def update_streams(self) -> None:
        """
        Updates the tap stream objects in place
        """
        stream_tree = self.read_streams()

        for new_stream in self.new_streams:
            stream_object_name = self._snake_to_pascal(new_stream)
            stream_name = new_stream
            unparsed_class_def = self.stream_template.format(
                stream_name=stream_name,
                stream_object_name=stream_object_name
                )
            #Dump the contents into the ast syntax tree
            stream_tree.body.append(ast.parse(unparsed_class_def))

        with open(self.stream_path, 'w') as out:
            out.write(ast.unparse(stream_tree))


    def update_tap(self) -> None:
        """
        Updates the tap object in place. It's really important that we initialize the proper
        ast objects to avoid a compilation error. This is why we don't template this out
        """
        tap_tree = self.read_tap()

        for new_stream in self.new_streams:
            object_stream_name = self._snake_to_pascal(new_stream)
            idx = self._find_tap_import_index(tap_tree)
            #Edit the import statement
            tap_tree.body[idx].names.append(ast.alias(name=object_stream_name))
            #Edit the assignment statement
            tap_tree.body[idx+1].value.elts.append(ast.Name(object_stream_name,ast.Load))

        with open(self.tap_path, 'w') as out:
            out.write(ast.unparse(tap_tree))

    def update(self) -> None:
        """
        Updates the streams.py and tap.py files in place.
        """
        self.update_streams()
        self.update_tap()

    def _snake_to_pascal(self, s: str) -> str:
        """
        Converts a snake case string to pascal case

        >>> _snake_to_pascal('hello_world')
        'HelloWorld'
        """
        return s.replace("_"," ").title().replace(" ","")

    def _find_tap_import_index(self, tree: ast.Module) -> int:
        """
        Helper method that parses a generic tap syntax tree and returns
        the indexer for the import statement which looks something like

        from <tap>.streams import [
            Stream1,
            Stream2,
        ]

        This is the import we are trying to modify in place
        """

        #Our premise is that the generic import must be followed by an assignment
        #There are more exhaustive ways to find these statments but this should work
        #Most of the time
        for i, obj in enumerate(tree.body):
            if isinstance(obj, ast.ImportFrom):
                if isinstance(tree.body[i+1], ast.Assign):
                    return i


@click.command()
def main():
    """
    Update schemas in the schemas directory based on the current swagger spec and open api definition
    """

    spec = OpenApiSpec()
    incoming_schemas = spec.convert_to_schemas()

    updater = SchemaUpdater(incoming_schemas)
    print(f"Updating schemas with changes... \n{updater.change_report()}")
    updater.update_schemas()

    code_generator = AstSchemaTemplate(new_streams = updater.list_of_new_schemas)
    print(f"Generating new stream objects... \n{updater.list_of_new_schemas}")
    code_generator.update()

if __name__ == "__main__":
    main()