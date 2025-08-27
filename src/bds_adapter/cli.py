import argparse
import os
from typing import Dict, Any
from .adapter import BDSAdapter

def get_config() -> Dict[str, Any]:
    """Get configuration from command line arguments."""
    parser = argparse.ArgumentParser(description='Process BDS recordings to vCon format')
    parser.add_argument('--recording-path', required=True, help='Path to recording files')
    parser.add_argument('--output-path', required=True, help='Path for output files')
    parser.add_argument('--s3-bucket', help='S3 bucket for output')
    parser.add_argument('--s3-prefix', help='S3 prefix/folder for output')
    
    args = parser.parse_args()
    
    config = {
        'recording_path': args.recording_path,
        'output_path': args.output_path
    }
    
    # Add S3 config if provided
    if args.s3_bucket:
        config['s3'] = {
            'bucket': args.s3_bucket,
            'prefix': args.s3_prefix
        }
        
    return config

def get_default_config():
    return {
        'recording_path': '/path/to/recordings',  # Update this path
        'output_path': '/path/to/output',        # Update this path
        's3': {
            'bucket': 'my-vcon-bucket',          # Update bucket name
            'prefix': 'vcon-files'               # Update prefix
        }
    }

def main():
    """Main entry point for the CLI."""
    config = get_config()
    adapter = BDSAdapter(config)
    processed = adapter.process_batch()
    print(f"Processed {len(processed)} files")

if __name__ == '__main__':
    main()