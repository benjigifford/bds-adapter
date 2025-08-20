import os
import pytest
from bds_adapter.adapter import BDSAdapter

def test_init():
    """Test adapter initialization."""
    config = {
        'recording_path': '/tmp/input',
        'output_path': '/tmp/output'
    }
    adapter = BDSAdapter(config)
    assert adapter.recording_path == '/tmp/input'
    assert adapter.output_path == '/tmp/output'
    assert adapter.agent_role == 'agent'
    assert adapter.customer_role == 'customer'

def test_process_recording(tmp_path):
    """Test processing a single recording."""
    config = {
        'recording_path': str(tmp_path),
        'output_path': str(tmp_path / 'output')
    }
    
    # Create test recording file
    test_file = tmp_path / "test.mp3"
    test_file.write_bytes(b"dummy audio data")
    
    adapter = BDSAdapter(config)
    vcon = adapter.process_recording("test.mp3")
    
    assert vcon.version == "1.1.0"
    assert len(vcon.parties) == 2
    assert vcon.parties[0].role == "agent"
    assert vcon.parties[1].role == "customer"
    assert len(vcon.dialog) == 1
    assert vcon.dialog[0].type == "recording"
    assert vcon.dialog[0].recording_duration == 35

def test_process_batch(tmp_path):
    """Test batch processing of recordings."""
    config = {
        'recording_path': str(tmp_path),
        'output_path': str(tmp_path / 'output')
    }
    
    # Create test files
    for i in range(3):
        test_file = tmp_path / f"test_{i}.mp3"
        test_file.write_bytes(b"dummy audio data")
    
    adapter = BDSAdapter(config)
    processed = adapter.process_batch(max_files=2)
    
    assert len(processed) == 2
    assert all(f.endswith('.vcon.json') for f in processed)