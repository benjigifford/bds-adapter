from datetime import datetime
import os
from typing import Dict, Any, List
from vcon import Vcon, Party, Dialog
import uuid

class BDSAdapter:
    """BDS Adapter for converting 35-second call recordings to vCon format."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize adapter with configuration.
        
        Args:
            config: Dictionary containing:
                - recording_path: Path to input recordings
                - output_path: Path for output vCon files
                - agent_role: Role name for agent (default: 'agent')
                - customer_role: Role name for customer (default: 'customer')
        """
        self.recording_path = config.get('recording_path', '')
        self.output_path = config.get('output_path', '')
        self.agent_role = config.get('agent_role', 'agent')
        self.customer_role = config.get('customer_role', 'customer')

    def process_recording(self, recording_file: str) -> Vcon:
        """
        Convert a single recording to vCon format.
        
        Args:
            recording_file: Name of the recording file
            
        Returns:
            Vcon object containing the recording data
        """
        vcon = Vcon()
        
        # Set required fields
        vcon.id = str(uuid.uuid4())
        vcon.created = datetime.utcnow().isoformat()
        vcon.version = "1.1.0"
        
        # Add parties
        agent = Party(role=self.agent_role)
        customer = Party(role=self.customer_role)
        vcon.parties = [agent, customer]
        
        # Add dialog with recording
        dialog = Dialog()
        dialog.id = str(uuid.uuid4())
        dialog.type = "recording"
        dialog.created = datetime.utcnow().isoformat()
        
        # Add recording details
        recording_path = os.path.join(self.recording_path, recording_file)
        dialog.recording_url = f"file://{recording_path}"
        dialog.recording_format = "audio/mp3"
        dialog.recording_duration = 35  # 35 seconds per requirement
        
        vcon.dialog = [dialog]
        return vcon

    def process_batch(self, max_files: int = None) -> List[str]:
        """
        Process multiple recordings from input directory.
        
        Args:
            max_files: Optional maximum number of files to process
            
        Returns:
            List of processed vCon file paths
        """
        processed_files = []
        
        os.makedirs(self.output_path, exist_ok=True)
        
        for file in os.listdir(self.recording_path):
            if not file.endswith('.mp3'):
                continue
                
            if max_files and len(processed_files) >= max_files:
                break
                
            try:
                vcon = self.process_recording(file)
                output_file = os.path.join(
                    self.output_path, 
                    f"{vcon.id}.vcon.json"
                )
                vcon.save(output_file)
                processed_files.append(output_file)
                
            except Exception as e:
                print(f"Error processing {file}: {e}")
                continue
                
        return processed_files