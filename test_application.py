import requests
import application
import pytest
from threading import Thread

@pytest.fixture(scope="module", autouse=True)
def setup():
    # Start running mock server in a separate thread.
    # Daemon threads automatically shut down when the main process exits.
    mock_server_thread = Thread(target=application.init_api)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()

def test_index():
    rtn = requests.get(url='http://127.0.0.1:5000/')
    print(f'status code: {rtn.status_code}')
    assert rtn.status_code == 200