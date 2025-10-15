from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD
from datetime import datetime


def enrich_with_metadata(graph):
    if not len(graph):
        return graph  # Do not enrich an empty graph

    return graph
