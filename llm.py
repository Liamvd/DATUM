import pandas as pd
import google.generativeai as genai
import xml.etree.ElementTree as ET
from rdflib import Graph, URIRef, Literal, Namespace
import os


# Parse ontologies from given ontology list and return ontologies in dataframe and sheet names per ontology category
def readOntologies(ontology_file):
    df_ontologies = pd.ExcelFile(ontology_file)
    return df_ontologies


# Configure ai api and model
def configureAi():
    # For real implementation: remove hardcoded key and set as environment variable
    # genai.configure(api_key=os.environ["API_KEY"])
    genai.configure(api_key='AIzaSyAFKsWfhHpgjN-kVclJo5rUC6X8f5StoSo')
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model


# Get the source that will be scanned by the llm
def getSource():
    source = 'Reports of rape of Tigray women as part of the violence carried out on civilians in Tigray.'
    return source


# Create prompt request and return metadata
def promptRequest(df_ontologies, model, source):
    prompt = 'Read the source: ' + source + ' And read the list of ontologies in this dataframe: ' + str(
        df_ontologies.parse('All')[
            'Ontology Concept']) + 'Decide to which ontology the source fits best and remember the row number of that ' \
                                   'ontology. Check the row corresponding to that number in the following ' \
                                   'dataframe: ' + str(
        df_ontologies.parse('All')[
            'Properties']) + 'For each property in that row, create a property value based on the source. If nothing ' \
                             'relevant can be found in the source, leave the property blank. Your answer should only ' \
                             'consist of the following structure: ontology concept, property name 1: property value ' \
                             '1, property name 2: property value 2, etc. As an example: Civilian Victims, age: 20, ' \
                             'gender: female, incident: physical assault, location: Khartoum'
    response = model.generate_content(prompt)
    return response.text


# Put the results from the LLM in the proper format to export (currently dictionary and xml)
def parseMetadata(df_ontologies, results):
    parsed_results = {}
    results_list = results.split(',')
    count = 0
    g = Graph()
    BASE = Namespace('http://example.org/ontology/')
    for i in results_list:
        if count == 0:
            for sheet_name in df_ontologies.sheet_names[1:]:
                df_sheet = df_ontologies.parse(sheet_name)
                if i in df_sheet['Ontology Concept'].values:
                    # configure dictionary output
                    parsed_results['Category'] = sheet_name
                    parsed_results['Ontology'] = i

                    # configure xml output
                    root = ET.Element(i)

                    # configure rdf output
                    category = BASE[sheet_name.replace(" ", "_")]
                    ontology = BASE[i.replace(" ", "_")]
                    g.add((ontology, BASE['hasCategory'], category))
                    break
        else:
            i_split = i.split(':')
            # configure dictionary output
            parsed_results[i_split[0].strip()] = i_split[1].strip()

            # configure xml output
            child = ET.SubElement(root, 'property', attrib={i_split[0].strip(): i_split[1].strip()})

            # configure rdf output
            property = BASE[i_split[0].strip().replace(" ", "_")]
            g.add((ontology, BASE["hasProperty"], property))
            g.add((ontology, BASE["hasValue"], Literal(i_split[1].strip())))
        count += 1
    return parsed_results, root, g


ontologies = readOntologies('Ontologies.xlsx')
aiModel = configureAi()
dataSource = getSource()
print('Source: ' + dataSource)
metadata = promptRequest(ontologies, aiModel, dataSource)
print('Output by LLM: ' + metadata)
parsed_metadata, data_xml, data_rdf = parseMetadata(ontologies, metadata)
print('Final output: ')
print(parsed_metadata)

# Save metadata as xml file; placeholder until automatic cedar integration
tree = ET.ElementTree(data_xml)
with open(r'output/metadata.xml', 'wb') as file:
    tree.write(file, encoding='utf-8', xml_declaration=True)

# Save metadata as rdf file; can be directly imported into ALlegroGraph
output_file = r'output/metadata.rdf'
data_rdf.serialize(destination=output_file, format='xml')
#print(g.serialize(format="turtle").decode("utf-8"))