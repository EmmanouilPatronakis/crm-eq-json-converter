#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON to CRM-EQ RDF Converter

Converts structured JSON earthquake data to RDF/TTL format compliant with 
the CRM-EQ ontology. Part of the "Ancient Earthquakes Knowledge Graph" project.

Usage:
    1. Load the base Earthquake_Model.ttl ontology
    2. Parse JSON earthquake data  
    3. Generate RDF triples following CRM-EQ patterns
    4. Serialize to TTL format

Author: [Your Name]
License: MIT
"""

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

# Namespace definitions
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
CRMINF = Namespace("http://www.cidoc-crm.org/extensions/crminf/")
CRMSCI = Namespace("http://www.cidoc-crm.org/extensions/crmsci/")
EQ = Namespace("https://crm-eq.ics.forth.gr/ontology#")


def ensure_crete(graph: Graph) -> URIRef:
    """Ensure Crete exists as an E53_Place in the graph."""
    crete_uri = EQ["Crete"]
    if (crete_uri, RDF.type, None) not in graph:
        graph.add((crete_uri, RDF.type, CRM["E53_Place"]))
        graph.add((crete_uri, RDFS.label, Literal("Crete", datatype=XSD.string)))
    return crete_uri


def ensure_place_in_crete(graph: Graph, local_name: str) -> URIRef:
    """
    Create or reuse a place within Crete.
    Links to Crete via P89_falls_within.
    """
    place_uri = EQ[local_name]
    if (place_uri, RDF.type, None) not in graph:
        graph.add((place_uri, RDF.type, CRM["E53_Place"]))
        graph.add((place_uri, RDFS.label, Literal(local_name, datatype=XSD.string)))
    
    crete_uri = ensure_crete(graph)
    if (place_uri, CRM["P89_falls_within"], None) not in graph:
        graph.add((place_uri, CRM["P89_falls_within"], crete_uri))
    return place_uri


def ensure_time_span(graph: Graph, local_name: str, year: str = None) -> URIRef:
    """
    Create or reuse an E52_Time-Span.
    Stores year in P82_at_some_time_within if provided.
    """
    ts_uri = URIRef(f"https://crm-eq.ics.forth.gr/ontology#{local_name}")
    if (ts_uri, RDF.type, None) not in graph:
        graph.add((ts_uri, RDF.type, CRM["E52_Time-Span"]))
        if year:
            try:
                y_int = int(year)
                graph.add((ts_uri, CRM["P82_at_some_time_within"], Literal(y_int, datatype=XSD.int)))
            except ValueError:
                graph.add((ts_uri, CRM["P82_at_some_time_within"], Literal(year, datatype=XSD.string)))
    return ts_uri


def ensure_type(graph: Graph, local_name: str, class_type="E55_Type") -> URIRef:
    """Create or reuse a type (E55_Type or E58_Measurement_Unit)."""
    t_uri = EQ[local_name]
    if (t_uri, RDF.type, None) not in graph:
        if class_type == "E55_Type":
            graph.add((t_uri, RDF.type, CRM["E55_Type"]))
        elif class_type == "E58_Measurement_Unit":
            graph.add((t_uri, RDF.type, CRM["E58_Measurement_Unit"]))
        graph.add((t_uri, RDFS.label, Literal(local_name, datatype=XSD.string)))
    return t_uri


def ensure_document(graph: Graph, doc_name: str) -> URIRef:
    """Create or reuse an E31_Document."""
    doc_uri = EQ[doc_name]
    if (doc_uri, RDF.type, None) not in graph:
        graph.add((doc_uri, RDF.type, CRM["E31_Document"]))
        graph.add((doc_uri, RDFS.label, Literal(doc_name, datatype=XSD.string)))
    return doc_uri


def create_dimension(graph: Graph,
                     quake_name: str,
                     dim_id: str,
                     dim_type: str,
                     value=None,
                     lower=None,
                     upper=None,
                     unit=None,
                     error_margin=None,
                     uncertainty_factor=None,
                     note=None) -> URIRef:
    """
    Create an E54_Dimension for earthquake measurements.
    
    Supports:
    - Single values or ranges (lower/upper bounds)
    - Measurement units
    - Error margins and uncertainty factors
    - Additional notes
    """
    dimension_uri = EQ[f"{quake_name}_{dim_id}"]
    if (dimension_uri, RDF.type, None) not in graph:
        graph.add((dimension_uri, RDF.type, CRM["E54_Dimension"]))

        # Type assignment
        t_uri = ensure_type(graph, dim_type, "E55_Type")
        graph.add((dimension_uri, CRM["P2_has_type"], t_uri))

        # Measurement unit
        if unit:
            unit_uri = ensure_type(graph, unit, "E58_Measurement_Unit")
            graph.add((dimension_uri, CRM["P91_has_unit"], unit_uri))

        # Values: range or single
        if lower is not None and upper is not None:
            graph.add((dimension_uri, CRM["P90a_has_lower_value_limit"], Literal(lower, datatype=XSD.double)))
            graph.add((dimension_uri, CRM["P90b_has_upper_value_limit"], Literal(upper, datatype=XSD.double)))
        elif value is not None:
            if isinstance(value, (int, float)):
                graph.add((dimension_uri, CRM["P90_has_value"], Literal(value, datatype=XSD.double)))
            else:
                graph.add((dimension_uri, CRM["P90_has_value"], Literal(value, datatype=XSD.string)))

        # Extended properties
        if error_margin:
            graph.add((dimension_uri, EQ["PEQ1_has_error_margin"], Literal(error_margin, datatype=XSD.string)))
        if uncertainty_factor:
            graph.add((dimension_uri, EQ["PEQ9_has_documented_uncertainty_factor"], Literal(uncertainty_factor, datatype=XSD.string)))
        if note:
            graph.add((dimension_uri, CRM["P3_has_note"], Literal(note, datatype=XSD.string)))

    return dimension_uri


def ensure_triggered_event(graph: Graph, local_name: str, event_type: str = None) -> URIRef:
    """
    Create triggered events (destruction, alteration, etc.).
    Links to earthquake via O13_triggered.
    """
    evt_uri = EQ[local_name]
    if (evt_uri, RDF.type, None) not in graph:
        if event_type == "S18_Alteration":
            graph.add((evt_uri, RDF.type, CRMSCI["S18_Alteration"]))
        elif event_type == "E6_Destruction":
            graph.add((evt_uri, RDF.type, CRM["E6_Destruction"]))
        else:
            graph.add((evt_uri, RDF.type, CRM["E7_Activity"]))
        graph.add((evt_uri, RDFS.label, Literal(local_name, datatype=XSD.string)))
    return evt_uri


def create_reference_list_object(graph: Graph, list_local_name: str, data: dict) -> URIRef:
    """
    Create an E73_Information_Object for bibliographic references.
    Uses P67_refers_to and P70i_is_documented_in.
    """
    list_uri = EQ[list_local_name]
    if (list_uri, RDF.type, None) not in graph:
        graph.add((list_uri, RDF.type, CRM["E73_Information_Object"]))
        graph.add((list_uri, RDFS.label, Literal(list_local_name, datatype=XSD.string)))

    # References
    for ref_item in data.get("refers_to", []):
        ref_uri = URIRef(ref_item) if ref_item.startswith("http") else EQ[ref_item]
        graph.add((list_uri, CRM["P67_refers_to"], ref_uri))

    # Source document
    if "is_documented_in" in data:
        doc_uri = ensure_document(graph, data["is_documented_in"])
        graph.add((list_uri, CRM["P70i_is_documented_in"], doc_uri))

    return list_uri


def create_epicenter_coords_dimension(graph: Graph, quake_name: str, lat: float, lon: float) -> URIRef:
    """
    Create coordinate dimensions for epicenter location.
    
    Structure:
    - Main coordinate dimension
    - Subdimensions for latitude and longitude
    - Links via P89_falls_within
    """
    coords_name = f"{quake_name}_epicenter_coords"
    coords_uri = EQ[coords_name]

    if (coords_uri, RDF.type, None) not in graph:
        graph.add((coords_uri, RDF.type, CRM["E54_Dimension"]))

        # Latitude subdimension
        lat_name = f"{coords_name}_lat"
        lat_uri = EQ[lat_name]
        if (lat_uri, RDF.type, None) not in graph:
            graph.add((lat_uri, RDF.type, CRM["E54_Dimension"]))
            ensure_type(graph, "latitude", "E55_Type")
            graph.add((lat_uri, CRM["P2_has_type"], EQ["latitude"]))
            graph.add((lat_uri, CRM["P90_has_value"], Literal(lat, datatype=XSD.double)))

        # Longitude subdimension
        lon_name = f"{coords_name}_lon"
        lon_uri = EQ[lon_name]
        if (lon_uri, RDF.type, None) not in graph:
            graph.add((lon_uri, RDF.type, CRM["E54_Dimension"]))
            ensure_type(graph, "longitude", "E55_Type")
            graph.add((lon_uri, CRM["P2_has_type"], EQ["longitude"]))
            graph.add((lon_uri, CRM["P90_has_value"], Literal(lon, datatype=XSD.double)))

        # Link subdimensions
        graph.add((coords_uri, CRM["P89_falls_within"], lat_uri))
        graph.add((coords_uri, CRM["P89_falls_within"], lon_uri))

    return coords_uri


def create_earthquake(graph: Graph, eq_data: dict) -> URIRef:
    """
    Create a complete EQ1_Earthquake instance with all properties.
    
    Handles:
    - Temporal information (PEQ5)
    - Affected places (PEQ6)
    - Epicenter location (PEQ7)
    - Seismic dimensions (PEQ8)
    - Triggered events (O13)
    - Bibliographic references
    - Descriptive notes
    """
    eq_name = eq_data["name"]
    quake_uri = EQ[eq_name]
    
    # Create earthquake instance
    if (quake_uri, RDF.type, None) not in graph:
        graph.add((quake_uri, RDF.type, EQ["EQ1_Earthquake"]))

    # Time span
    if "time_local_name" in eq_data:
        ts_uri = ensure_time_span(graph, eq_data["time_local_name"], eq_data.get("year"))
        graph.add((quake_uri, EQ["PEQ5_has_documented_possible_timespan"], ts_uri))

    # Affected places
    for pl_local in eq_data.get("places_in_crete", []):
        pl_uri = ensure_place_in_crete(graph, pl_local)
        graph.add((quake_uri, EQ["PEQ6_has_documented_possible_place"], pl_uri))

    # Epicenter with coordinates
    if "epicenter_coords" in eq_data:
        lat, lon = eq_data["epicenter_coords"]
        epic_local_name = f"{eq_name}_epicenter"
        epic_uri = ensure_place_in_crete(graph, epic_local_name)
        
        coords_dim_uri = create_epicenter_coords_dimension(graph, eq_name, lat, lon)
        graph.add((epic_uri, CRMSCI["O12_has_dimension"], coords_dim_uri))
        graph.add((quake_uri, EQ["PEQ7_has_documented_possible_epicenter_place"], epic_uri))

    # Seismic dimensions
    for d in eq_data.get("dimensions", []):
        dim_uri = create_dimension(
            graph,
            quake_name=eq_name,
            dim_id=d["id"],
            dim_type=d["type"],
            value=d.get("value"),
            lower=d.get("lower"),
            upper=d.get("upper"),
            unit=d.get("unit"),
            error_margin=d.get("error_margin"),
            uncertainty_factor=d.get("uncertainty_factor"),
            note=d.get("note")
        )
        graph.add((quake_uri, EQ["PEQ8_has_documented_possible_dimension"], dim_uri))

    # Triggered events
    for evt in eq_data.get("triggered_events", []):
        evt_uri = ensure_triggered_event(graph, evt["local_name"], evt.get("type"))
        graph.add((quake_uri, CRMSCI["O13_triggered"], evt_uri))

    # Direct references
    for ref_name in eq_data.get("references", []):
        doc_uri = ensure_document(graph, ref_name)
        graph.add((quake_uri, CRM["P70i_is_documented_in"], doc_uri))

    # Reference list object
    if "list_of_references" in eq_data:
        list_info = eq_data["list_of_references"]
        list_uri = create_reference_list_object(graph, list_info["local_name"], list_info)
        graph.add((quake_uri, CRM["P129i_is_subject_of"], list_uri))

    # Description
    if desc := eq_data.get("description"):
        graph.add((quake_uri, CRM["P3_has_note"], Literal(desc, datatype=XSD.string)))

    # Label
    label = eq_data.get("label", eq_name)
    graph.add((quake_uri, RDFS.label, Literal(label, datatype=XSD.string)))

    return quake_uri


def main():
    """Example usage demonstrating earthquake e165 creation."""
    # Load base ontology
    input_ontology = "Earthquake_Model.ttl"
    g = Graph()
    g.parse(input_ontology, format="turtle")
    print(f"Loaded Earthquake Model: {len(g)} triples")

    # Example earthquake data
    e165_data = {
        "name": "e165",
        "time_local_name": "1907-08-09_13:05_GMT+00",
        "year": "1907",
        "places_in_crete": ["Rethymnon"],
        "epicenter_coords": (35.6, 24.6),
        "dimensions": [
            {"id": "reliability", "type": "reliability", "value": 3},
            {"id": "focal_depth", "type": "focal_depth", "value": "shallow"},
            {"id": "intensity", "type": "intensity", "lower": 2, "upper": 3},
            {
                "id": "magnitude",
                "type": "magnitude",
                "unit": "Ms",
                "value": 4.6,
                "error_margin": "±0.3",
                "uncertainty_factor": "Possible"
            }
        ],
        "references": ["Papadopoulos_Book"],
        "description": (
            "This is an earthquake unknown in seismological literature. "
            "Vlastos (unpublished, p. 374) recalled:\n"
            "Καὶ τὴν 28 Ἰουλίου 1907 ἡμέρα Σάββατον ὥραν 5 καὶ 5'. μ.μ. "
            "Σεισμὸς μικρὸς με ἐλαφρᾶς δονήσεις τὸν ἠσθάνθην ἐργαζόμενος "
            "ἐν τῷ γραφείῳ μου ἐν Ῥεθύμνῳ.\n"
            "that is:\n"
            "And on 28 July 1907, Saturday hour 5 and 5 min. pm. Earthquake small with slight shocks, "
            "I felt it when I was working in my office in Rethymnon.\n"
            "Earthquake parameters: I distilled the same source as that of 30 July 1907."
        ),
        "label": "Earthquake #165 (1907-08-09)"
    }

    # Create earthquake
    e165_uri = create_earthquake(g, e165_data)
    print(f"Created: {e165_uri}")

    # Serialize result
    output_file = "earthquake_output.ttl"
    g.serialize(destination=output_file, format="turtle")
    print(f"Saved to {output_file}: {len(g)} triples")


if __name__ == "__main__":
    main()