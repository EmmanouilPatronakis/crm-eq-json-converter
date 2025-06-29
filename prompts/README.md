# CRM-EQ Prompt Templates

This folder contains the LLM prompt templates used in the custom pipeline for converting historical earthquake descriptions to CRM-EQ compliant RDF.

## Files
- `earthquake_prompt_template.txt` - Generic template with placeholders
- `earthquake_prompt_example.txt` - Complete example with actual earthquake data

## Usage
Replace placeholders in the template:
- `{DOMAIN}` - Your data domain (e.g., "earthquake")
- `{EXAMPLE_JSON_SCHEMA}` - Your target JSON schema
- `{SOURCE_TEXT_DATA}` - The historical text to convert

The prompts enforce strict JSON output and prevent LLM hallucination through explicit constraints.
