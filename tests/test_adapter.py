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

@pytest.fixture
def mock_vcon():
    """Create mock Vcon class that returns properly structured instances."""
    mock = MagicMock(spec=Vcon)
    
    def create_mock_instance():
        instance = MagicMock()
        # Set required attributes
        instance.version = "0.3.0"
        instance.id = str(uuid.uuid4())
        instance.created_at = datetime.now(UTC).isoformat()
        instance.parties = []
        instance.dialog = []
        
        # Mock instance methods
        def add_party(party):
            instance.parties.append({
                "role": party.role,
                "type": party.type
            })
            return instance
            
        def add_dialog(dialog):
            instance.dialog.append({
                "id": str(dialog.id),
                "type": dialog.type,
                "created_at": dialog.created_at,
                "start": dialog.start,
                "parties": dialog.parties,
                "recording_url": dialog.recording_url,
                "recording_format": dialog.recording_format,
                "recording_duration": dialog.recording_duration
            })
            return instance
            
        instance.add_party.side_effect = add_party
        instance.add_dialog.side_effect = add_dialog
        return instance

    # Set up class methods
    mock.build_new.side_effect = create_mock_instance
    mock.uuid8_time.return_value = str(uuid.uuid4())
    mock.uuid8_domain_name.return_value = str(uuid.uuid4())
    
    return mock

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
    with patch('bds_adapter.adapter.Vcon', mock_vcon):
        adapter = BDSAdapter(config)
        vcon = adapter.process_recording(temp_recording.name)
        
        assert vcon.version == "0.3.0"
        assert vcon.id
        assert len(vcon.parties) == 2
        assert len(vcon.dialog) == 1
        assert vcon.dialog[0]["type"] == "recording"

def test_process_batch(config, tmp_path, mock_vcon):
    """Test batch processing."""
    # Create output directory
    os.makedirs(config['output_path'], exist_ok=True)
    
    # Create test files
    for i in range(3):
        test_file = tmp_path / f"test_{i}.mp3"
        test_file.write_bytes(b"dummy audio data")
    
    with patch('bds_adapter.adapter.Vcon', mock_vcon):
        adapter = BDSAdapter(config)
        processed = adapter.process_batch(max_files=2)
        assert len(processed) == 2
        
        # Verify output files
        for file_path in processed:
            with open(file_path) as f:
                data = json.load(f)
                assert data["version"] == "0.3.0"
                assert len(data["parties"]) == 2
                assert len(data["dialog"]) == 1