# CRM-EQ JSON to RDF Converter

A Python tool for converting structured JSON earthquake data to RDF/TTL format following the CRM-EQ ontology. Developed as part of the "Ancient Earthquakes Knowledge Graph" project.

## Overview

This converter implements the custom pipeline methodology described in our paper, transforming JSON representations of historical earthquake data into CIDOC-CRM compliant RDF triples.

## Requirements

- Python 3.7+
- rdflib

```bash
pip install rdflib
```

## Usage

1. Place the `Earthquake_Model.ttl` ontology file in your working directory
2. Prepare your earthquake data in the JSON format (see example in code)
3. Run the converter:

```bash
python crm_eq_converter.py
```

## JSON Schema

The converter expects earthquake data with the following structure:

```json
{
  "name": "e165",
  "time_local_name": "1907-08-09_13:05_GMT+00",
  "year": "1907",
  "places_in_crete": ["Rethymnon"],
  "epicenter_coords": [35.6, 24.6],
  "dimensions": [
    {
      "id": "magnitude",
      "type": "magnitude",
      "unit": "Ms",
      "value": 4.6,
      "error_margin": "±0.3"
    }
  ],
  "references": ["Papadopoulos_Book"],
  "description": "Historical description text..."
}
```

## Output

The converter produces TTL files containing:
- Earthquake instances (EQ1_Earthquake)
- Temporal information (E52_Time-Span)
- Spatial data (E53_Place with coordinates)
- Seismic measurements (E54_Dimension)
- Bibliographic references (E31_Document)

## License

MIT License

## Citation

If you use this tool, please cite our paper:
**To Automate or not to Automate the Transcription of Ancient Earthquakes: Toward a Global Knowledge Graph about Ancient Earthquakes**, 2025.  
