import pytest

def pytest_addoption(parser):
    parser.addoption("--config", required=False, action='store', help="Path to config file")

@pytest.fixture
def config(request):
    return request.config.getoption("--config")