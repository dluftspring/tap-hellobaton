"""Tests standard tap features using the built-in SDK tests library."""

import os
import json
import subprocess
from pathlib import Path
from argparse import ArgumentParser
from jsonschema import validate
from jsonschema.validators import Draft7Validator
from singer_sdk.testing import get_standard_tap_tests
from tap_hellobaton.tap import Taphellobaton
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent.parent.parent / Path('.secrets/config.json')

def set_sample_config(config_path: Path) -> Dict[str, Any]:

    file_config_params: Dict[str, Any] = {}
    
    if os.path.exists(config_path):
        with open(config_path) as config_params:
            file_config_params = json.load(config_params)

    #Just grab the config that they specify either through file or environment variables
    config_to_test: Dict[str, Any] = {
        "company": os.getenv('TAP_HELLOBATON_COMPANY') or file_config_params.get('company', None),
        "api_key": os.getenv('TAP_HELLOBATON_API_KEY') or file_config_params.get('api_key', None),
        "user_agent": os.getenv('TAP_HELLOBATON_USER_AGENT') or file_config_params.get('user_agent', None)
    }

    return config_to_test

def get_samples_from_streams() -> Dict[str, Any]:
    """
    Helper method that gets a single record from each supported stream
    and it's corresponding schema

    Returns:
        A dictionary with the stream name as the key and sub-dictionary keyed with both the record instance and associated schema
        e.g.
        { 'account': {
                'record': {'id': '123', 'name': 'test'},
                'schema: {'id': 'integer', 'name': 'string'} 
            }
          'account_transaction':
          .
          .
          .
        }
    """
    SAMPLE_CONFIG=set_sample_config(CONFIG_PATH)
    #The way to get a single record is to run the connection test and parse the command line
    for env_var,val in SAMPLE_CONFIG.items():
        #Only optional arguments should be unset
        if val:
            os.environ[env_var] = val
    cli_out = subprocess.run(['tap-hellobaton','--config', 'ENV', '--test'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    #Parse the output to get each record not the schema
    cli_out_lines = cli_out.split('\n')
    records = []
    schemas = []
    for line in cli_out_lines:
        if 'RECORD' in line:
            records.append(line)
        if 'SCHEMA' in line:
            schemas.append(line)

    json_records = [json.loads(record) for record in records]
    json_schemas = [json.loads(schema) for schema in schemas]

    return { record_item['stream'] : {'record': record_item['record'], 'schema': schema_item['schema'] } for record_item, schema_item in zip(json_records,json_schemas) }


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    SAMPLE_CONFIG = set_sample_config(CONFIG_PATH)

    tests = get_standard_tap_tests(
        Taphellobaton,
        config=SAMPLE_CONFIG
    )
    for test in tests:
        test()

def test_validate_schema():
    """Test that json schema is valid against a single record."""
    data_to_validate = get_samples_from_streams()

    validation_results = []
    errors_humanized = ""
    for stream in data_to_validate.keys():
        validator = Draft7Validator(data_to_validate[stream]['schema'])
        errors = sorted(validator.iter_errors(data_to_validate[stream]['record']), key=lambda e: e.path)
        if not errors:
            validation_results.append(True)
        else:
            validation_results.append(False)
            for error in errors:
                errors_humanized += (f"Error in stream {stream}: with field {error.schema_path[1]} and schema definition {error.schema}: {error.message}\n")

    assert all(validation_results), errors_humanized