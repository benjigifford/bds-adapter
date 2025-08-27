# BDS Adapter

Adapter for analyzing Better Debt Solutions call recordings for regulatory compliance. Converts call recordings to vCon format for silence detection and compliance analysis within the first 35 seconds of debt collection calls.

## Purpose

This adapter helps ensure compliance with:
- Fair Debt Collection Practices Act (FDCPA)
- Telephone Consumer Protection Act (TCPA)

It focuses on the critical first 35 seconds of each call where required disclosures must be made:
- Debt collector identification
- Purpose of call statement
- Other regulatory disclosures

## Features

- Processes 35-second call recordings for compliance analysis
- Converts recordings to vCon format for further processing
- Adds required metadata for tracking and auditing
- Supports batch processing with error handling
- Provides CLI interface for integration with existing workflows

## Installation

```bash
# Clone the repository
git clone https://github.com/benjigifford/bds-adapter

# Install dependencies
poetry install
```

## Usage

Basic usage:
```bash
# Convert recordings
poetry run bds-adapter --input /path/to/recordings --output /path/to/vcons
```

Options:
```bash
--input          Path to recording files (required)
--output         Path for output vCon files (required)
--max-files      Maximum files to process
--agent-role     Role name for agent (default: 'agent')
--customer-role  Role name for customer (default: 'customer')
```

Example with all options:
```bash
poetry run bds-adapter \
  --input ./recordings \
  --output ./vcons \
  --max-files 100 \
  --agent-role "debt_collector" \
  --customer-role "debtor"
```

## Development

```bash
# Run tests
poetry run pytest

# Run with debug logging
poetry run bds-adapter --input ./recordings --output ./vcons --max-files 10
```

## Compliance Notes

The adapter prepares recordings for analysis of:
- Silent periods in first 35 seconds
- Missing recording segments
- Required disclosure verification

This data helps identify potential compliance risks and supports:
- FDCPA/TCPA compliance monitoring
- Risk management
- Quality assurance
- Regulatory audit preparation

## Project Status

This is part of a larger compliance monitoring system that includes:
- Recording ingestion (this adapter)
- Silence detection
- Transcription
- Compliance analysis