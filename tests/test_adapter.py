import os
import uuid
import pytest
from pathlib import Path
from datetime import datetime, UTC
import json
from unittest.mock import MagicMock, patch
from vcon.vcon import Vcon
from vcon.dialog import Dialog
from vcon.party import Party
from bds_adapter.adapter import BDSAdapter

class MockVcon:
    """A serializable mock Vcon implementation."""
    def __init__(self, data=None):
        self.vcon_dict = {
            "version": "0.3.0",
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "parties": [],
            "dialog": []
        }
        if data:
            self.vcon_dict.update(data)

    def add_party(self, party):
        self.vcon_dict["parties"].append({
            "role": party.role,
            "type": party.type
        })
        return self

    def add_dialog(self, dialog):
        self.vcon_dict["dialog"].append({
            "id": str(dialog.id),
            "type": dialog.type,
            "created_at": dialog.created_at,
            "start": dialog.start,
            "parties": dialog.parties,
            "recording_url": dialog.recording_url,
            "recording_format": dialog.recording_format,
            "recording_duration": dialog.recording_duration
        })
        return self

    @property
    def version(self):
        return self.vcon_dict["version"]

    @property
    def id(self):
        return self.vcon_dict["id"]

    @property
    def created_at(self):
        return self.vcon_dict["created_at"]

    @property
    def parties(self):
        return self.vcon_dict["parties"]

    @property
    def dialog(self):
        return self.vcon_dict["dialog"]

    @classmethod
    def build_new(cls):
        """Create a new vCon instance."""
        return cls()

@pytest.fixture
def mock_vcon():
    """Create mock Vcon class."""
    with patch('vcon.vcon.Vcon') as mock:
        # Create class with required methods
        mock_class = type('MockVconClass', (), {
            'build_new': staticmethod(MockVcon.build_new),
            'uuid8_time': staticmethod(lambda x=0: str(uuid.uuid4())),
            'uuid8_domain_name': staticmethod(lambda x: str(uuid.uuid4()))
        })
        
        # Return mock class that creates MockVcon instances
        mock.side_effect = MockVcon
        mock.build_new.side_effect = MockVcon.build_new
        mock.uuid8_time.side_effect = mock_class.uuid8_time
        mock.uuid8_domain_name.side_effect = mock_class.uuid8_domain_name
        
        yield mock

@pytest.fixture
def config(tmp_path):
    """Create test configuration."""
    return {
        'recording_path': str(tmp_path),
        'output_path': str(tmp_path / 'output'),
        'agent_role': 'test_agent',
        'customer_role': 'test_customer',
        's3': {
            'bucket': 'test-bucket',
            'prefix': 'test-prefix'
        }
    }

@pytest.fixture
def temp_recording(tmp_path):
    """Create a temporary recording file."""
    recording = tmp_path / "test.mp3"
    recording.write_bytes(b"dummy audio data")
    return recording

def test_process_recording(config, temp_recording, mock_vcon):
    """Test single recording processing."""
    with patch('vcon.vcon.Vcon', mock_vcon):
        adapter = BDSAdapter(config)
        vcon = adapter.process_recording(temp_recording.name)
        
        assert vcon.version == "0.3.0"
        assert vcon.id
        assert len(vcon.parties) == 2
        assert len(vcon.dialog) == 1

def test_process_batch(config, tmp_path, mock_vcon):
    """Test batch processing."""
    # Create test files
    for i in range(3):
        test_file = tmp_path / f"test_{i}.mp3"
        test_file.write_bytes(b"dummy audio data")
    
    with patch('vcon.vcon.Vcon', mock_vcon):
        adapter = BDSAdapter(config)
        processed = adapter.process_batch(max_files=2)
        assert len(processed) == 2