import pandas as pd
import google.generativeai as genai
import xml.etree.ElementTree as ET
from rdflib import Graph, Literal, Namespace
import os
import csv

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GRPC_VERBOSITY'] = 'NONE'
os.environ['GRPC_TRACE'] = ''


# Parse ontologies from given ontology list and return ontologies in dataframe and sheet names per ontology category
def readOntologies(ontology_file):
    df_ontologies = pd.ExcelFile(ontology_file)
    return df_ontologies


# Configure ai api and model
def configureAi():
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model


# Get the source that will be scanned by the llm
def getSource():
    source = 'Reports of rape of Tigray women as part of the violence carried out on civilians in Tigray.'
    return source


# Create prompt request and return metadata
def promptRequest(df_ontologies, model, source):
    prompt = 'Read the source: ' + source + ' And read the list of ontologies in this dataframe: ' + str(
        df_ontologies.parse('All')['Ontology Concept']) + ' Choose the ontology that best fits the source. For ' \
                                                          'each of the properties in the following list of ' \
                                                          'properties, provide a true or false based on whether the ' \
                                                          'source is related to that property: ' + str(
        df_ontologies.parse('All')['Description']) + 'Your response should only consist of the following structure: ' \
                                                     'Event name: Event name, Label name 1: True/False, Label name ' \
                                                     '2: True/False, etc. For example: Event name: Reports of rape ' \
                                                     'of German women, Civilian Victims: True, Adbuction: False, ' \
                                                     'etc.'

    response = model.generate_content(prompt)
    return response.text


def parseMetadata(results):
    parsed_results = {}
    csv_list = []
    results_list = results.split(',')
    count = 0
    g = Graph()
    BASE = Namespace('http://example.org/ontology/') # Should be configured with own ontology usage
    root = None  # Initialize root to ensure it is accessible later

    # Clean up the results (to remove curly braces and split into properties)
    for i in results_list:
        i = i.strip()

        # Handle the first result to initialize the root element and metadata.
        if count == 0:
            # Initialize basic metadata (Event name, Country, Region, etc.)
            parsed_results['Event name'] = "Reports of rape of Tigray women"
            parsed_results['Date'] = '10-12-2024'
            parsed_results['Country'] = "Ethiopia"
            parsed_results['Region'] = "Tigray"

            # Add basic metadata to CSV export
            csv_list.append({
                "Property": "Event name",
                "Value": parsed_results['Event name']
            })
            csv_list.append({
                "Property": "Date",
                "Value": parsed_results['Date']
            })
            csv_list.append({
                "Property": "Country",
                "Value": parsed_results['Country']
            })
            csv_list.append({
                "Property": "Region",
                "Value": parsed_results['Region']
            })

            # Initialize the XML root
            root = ET.Element("Reports_of_rape_of_Tigray_women")

            # Add basic metadata to RDF
            g.add((BASE['Reports_of_rape_of_Tigray_women'], BASE["date"], Literal(parsed_results['Date'])))
            g.add((BASE['Reports_of_rape_of_Tigray_women'], BASE["country"], Literal(parsed_results['Country'])))
            g.add((BASE['Reports_of_rape_of_Tigray_women'], BASE["region"], Literal(parsed_results['Region'])))

        # Parsing the properties
        else:
            i_split = i.split(':')
            category = i_split[0].strip()
            value = i_split[1].strip()

            # Clean up curly braces if present
            if value.startswith('{'):
                value = value[1:].strip()
            if value.endswith('}'):
                value = value[:-1].strip()

            # Only add the individual properties with True/False values
            if value.lower() in ['true', 'false']:
                parsed_results[category] = value.lower() == 'true'

                # Add each property to XML as child elements
                if root is not None:  # Ensure root is initialized
                    clean_category = category.replace(" ", "_")
                    child = ET.SubElement(root, clean_category, attrib={"value": str(parsed_results[category])})

                # Add property to CSV export
                csv_list.append({
                    "Property": category,
                    "Value": parsed_results[category]
                })

                # Configure RDF output
                # For RDF, we treat the category as the property and value as the value of that property
                clean_category_rdf = category.replace(" ", "_")
                property = BASE[clean_category_rdf]
                if parsed_results[category]:  # Only add to RDF if the value is True
                    g.add((BASE['Reports_of_rape_of_Tigray_women'], BASE["relatesTo"], property))

        count += 1

    return parsed_results, root, csv_list, g


ontologies = readOntologies('sources/Ontologies.xlsx')
aiModel = configureAi()
dataSource = getSource()
print('Source: ' + dataSource)
metadata = promptRequest(ontologies, aiModel, dataSource)
print('Output by LLM: ' + metadata)
parsed_metadata, data_xml, data_csv, data_rdf = parseMetadata(metadata)
print('Final output: ')
print(parsed_metadata)

# Save metadata as xml file; placeholder until automatic cedar integration
tree = ET.ElementTree(data_xml)
with open(r'output/metadata.xml', 'wb') as file:
    tree.write(file, encoding='utf-8', xml_declaration=True)

# Save metadata as csv file; human-readable output that can be used for manual insertion, showcasing or visualisation
csv_headers = ['Property', 'Value']
with open(r'output/metadata.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(data_csv)

# Save metadata as rdf file; can be directly imported into ALlegroGraph
output_file = r'output/metadata.rdf'
data_rdf.serialize(destination=output_file, format='xml')
# print(g.serialize(format="turtle").decode("utf-8"))
