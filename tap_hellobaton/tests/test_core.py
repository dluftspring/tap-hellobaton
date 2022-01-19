"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os
import json
import pytest
from pathlib import Path
from argparse import ArgumentParser
from singer_sdk.testing import get_standard_tap_tests
from tap_hellobaton.tap import Taphellobaton
from singer_sdk.streams import RESTStream
from tap_hellobaton.client import hellobatonStream
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent.parent.parent / Path('.secrets/config.json')

def set_sample_config(config_path: Path) -> Dict[str, Any]:

    file_config_params: Dict[str, Any] = {}
    
    if os.path.exists(config_path):
        with open(config_path) as config_params:
            file_config_params: Dict[str, Any] = json.load(config_params)

    #Just grab the config that they specify either through file or environment variables
    config_to_test: Dict[str, Any] = {
        "company": os.getenv('TAP_HELLOBATON_COMPANY') or file_config_params['company'],
        "api_key": os.getenv('TAP_HELLOBATON_API_KEY') or file_config_params['api_key'],
        "user_agent": os.getenv('TAP_HELLOBATON_USER_AGENT') or file_config_params['user_agent']
    }

    return config_to_test

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


def test_check_connection():

    SAMPLE_CONFIG = set_sample_config(CONFIG_PATH)
    tap = Taphellobaton(config=SAMPLE_CONFIG)
    result = tap.run_connection_test()

    assert result