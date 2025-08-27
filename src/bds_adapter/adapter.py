from datetime import datetime, UTC
import os
import json
import uuid
from typing import Dict, Any, List, Optional
from vcon.vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from .s3 import S3Handler

class BDSAdapter:
    """BDS Adapter for converting 35-second call recordings to vCon format."""
    
    def __init__(self, config: Dict[str, Any]):
        self.recording_path = config.get('recording_path', '')
        self.output_path = config.get('output_path', '')
        self.agent_role = config.get('agent_role', 'agent')
        self.customer_role = config.get('customer_role', 'customer')
        
        s3_config = config.get('s3', {})
        self.s3_handler = None
        if s3_config and 'bucket' in s3_config:
            self.s3_handler = S3Handler(
                bucket=s3_config['bucket'],
                prefix=s3_config.get('prefix')
            )

    def process_recording(self, recording_file: str) -> Vcon:
        """Convert a single recording to vCon format."""
        vcon = Vcon.build_new()
        timestamp = datetime.now(UTC).isoformat()

        # Add parties
        agent = Party(role=self.agent_role, type="person")
        customer = Party(role=self.customer_role, type="person")
        vcon.add_party(agent)
        vcon.add_party(customer)

        # Create dialog
        dialog = Dialog(
            id=str(uuid.uuid4()),
            type="recording",
            created_at=timestamp,
            start=timestamp,
            parties=[
                {"role": self.agent_role, "type": "person"},
                {"role": self.customer_role, "type": "person"}
            ],
            recording_url=f"file://{os.path.join(self.recording_path, recording_file)}",
            recording_format="audio/mp3",
            recording_duration=35
        )

        # Add dialog and return
        vcon.add_dialog(dialog)
        return vcon

    def process_batch(self, max_files: Optional[int] = None) -> List[str]:
        """Process multiple recordings from input directory."""
        processed_files = []
        os.makedirs(self.output_path, exist_ok=True)
        
        try:
            files = sorted([f for f in os.listdir(self.recording_path) if f.endswith('.mp3')])
            if max_files:
                files = files[:max_files]
            
            for file in files:
                try:
                    vcon = self.process_recording(file)
                    output_file = os.path.join(self.output_path, f"{vcon.id}.vcon.json")
                    
                    # Convert to dict for serialization
                    vcon_data = {
                        "version": vcon.version,
                        "id": vcon.id,
                        "created_at": vcon.created_at,
                        "parties": vcon.parties,
                        "dialog": vcon.dialog
                    }
                    
                    # Write to file
                    with open(output_file, 'w') as f:
                        json.dump(vcon_data, f, indent=2)
                
                    processed_files.append(output_file)
                    
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
                    continue
    
        except Exception as e:
            print(f"Batch processing error: {str(e)}")
    
        return processed_files