import click
import os
from .adapter import BDSAdapter

@click.command()
@click.option('--input', required=True, help='Path to recording files')
@click.option('--output', required=True, help='Path for output vCon files')
@click.option('--max-files', type=int, help='Maximum files to process')
@click.option('--agent-role', default='agent', help='Role name for agent')
@click.option('--customer-role', default='customer', help='Role name for customer')
def main(input: str, output: str, max_files: int, agent_role: str, customer_role: str):
    """Convert BDS call recordings to vCon format."""
    
    if not os.path.exists(input):
        click.echo(f"Error: Input path does not exist: {input}")
        return 1
        
    config = {
        'recording_path': input,
        'output_path': output,
        'agent_role': agent_role,
        'customer_role': customer_role
    }
    
    adapter = BDSAdapter(config)
    processed = adapter.process_batch(max_files)
    
    click.echo(f"Successfully processed {len(processed)} recordings")
    return 0

if __name__ == '__main__':
    main()