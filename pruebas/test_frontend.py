from unittest.mock import patch
from pathlib import Path
import requests
from streamlit.testing.v1 import AppTest
from frontend.client import BackendError,call

def test_api_no_disponible(monkeypatch):
    def fail(*a,**kw):raise requests.ConnectionError('offline')
    monkeypatch.setattr(requests,'request',fail)
    import pytest
    with pytest.raises(BackendError,match='conectar'):call('/v1/clients')

def test_ui_maneja_backend_caido():
    with patch('frontend.client.call',side_effect=BackendError('API no disponible')):
        at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'frontend/app.py')).run()
        assert not at.exception
        assert 'API no disponible' in at.error[0].value
