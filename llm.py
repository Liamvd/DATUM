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
                             'relevant can be found in the source, leave the property blank. But with the booleans anders always false if not you do not know. Your answer should only ' \
                             'consist of the following structure: Event name: string, Date: date, Country: string, Region: string, Eating leaves/ seeds: boolean, Climate change/ natural disaster: boolean, Livestock death: boolean, Looting: boolean, Destruction of agriculture: boolean, Diversion of aid: boolean, Bad harvest/ crops inaccessible: boolean, Slaughtering/ stealing of animals: boolean, Preventing farming: boolean, Death from starvation: boolean, Water shortage: boolean, Occupation of water sources: boolean, Weapon of war: boolean, Deliberate starvation: boolean, Aid has run out: boolean, Aid unable to reach/ blocking of aid: boolean, Dismantling of the economic and food system: boolean, Denial of starvation (as weapon of war): boolean, (Potential) famine: boolean, Inaction for international actors: boolean' \
                             ', Eating leaves/ seeds: boolean, Climate change/ natural disaster: boolean, Livestock death: boolean, Looting: boolean, Destruction of agriculture: boolean, Diversion of aid: boolean, Bad harvest/ crops inaccessible: boolean, Slaughtering/ stealing of animals: boolean, Preventing farming: boolean, Death from starvation: boolean, Water shortage: boolean, Occupation of water sources: boolean, Weapon of war: boolean, Deliberate starvation: boolean, Aid has run out: boolean, Aid unable to reach/ blocking of aid: boolean, Dismantling of the economic and food system: boolean, Denial of starvation (as weapon of war): boolean, (Potential) famine: boolean, Inaction for international actors: boolean ' \
                             ', Occupied by armed groups: boolean, Medical supplies cannot reach: boolean, Transport of patients: boolean, Looting/ raiding: boolean, Humanitarian aid: boolean, Paying for health care: boolean, Fuel shortage: boolean, Internet: boolean, Vaccines: boolean }' \
                             'For example: Event name: Reports of rape of German women, Date: 2024-12-03, Country: Ethiopia, Region: Berlin, Eating leaves/ seeds: false, Climate change/ natural disaster: false, Livestock death: false, Looting: true, Destruction of agriculture: true, Diversion of aid: true, Bad harvest/ crops inaccessible: false, Slaughtering/ stealing of animals: false, Preventing farming: false, Death from starvation: false, Water shortage: false, Occupation of water sources: false, Weapon of war: true, Deliberate starvation: false, Aid has run out: false, Aid unable to reach/ blocking of aid: true, Dismantling of the economic and food system: false, Denial of starvation (as weapon of war): false, (Potential) famine: false, Inaction for international actors: true, Eating leaves/ seeds: false, Climate change/ natural disaster: false, Livestock death: false, Looting: true, Destruction of agriculture: true, Diversion of aid: true, Bad harvest/ crops inaccessible: false, Slaughtering/ stealing of animals: false, Preventing farming: false, Death from starvation: false, Water shortage: false, Occupation of water sources: false, Weapon of war: true, Deliberate starvation: false, Aid has run out: false, Aid unable to reach/ blocking of aid: true, Dismantling of the economic and food system: false, Denial of starvation (as weapon of war): false, (Potential) famine: false, Inaction for international actors: true }, Destruction of the Health System: { Occupied by armed groups: true, Medical supplies cannot reach: true, Transport of patients: true, Looting/ raiding: true, Humanitarian aid: true, Paying for health care: true, Fuel shortage: false, Internet: false, Vaccines: false '

    response = model.generate_content(prompt)
    return response.text


def parseMetadata(df_ontologies, results):
    parsed_results = {}
    csv_list = []
    results_list = results.split(',')
    count = 0
    g = Graph()
    BASE = Namespace('http://example.org/ontology/')
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

        # Parsing the properties under each category (like Sexual abuse, Deliberate Famine)
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

                # Optionally, configure RDF output if needed (assuming the output could be relevant)
                # For RDF, we treat the category as the property and value as the value of that property
                clean_category_rdf = category.replace(" ", "_")
                property = BASE[clean_category_rdf]
                g.add((BASE['Reports_of_rape_of_Tigray_women'], BASE["hasProperty"], property))
                g.add((property, BASE["hasValue"], Literal(parsed_results[category])))

        count += 1

    return parsed_results, root, csv_list, g


ontologies = readOntologies('Ontologies.xlsx')
aiModel = configureAi()
dataSource = getSource()
print('Source: ' + dataSource)
metadata = promptRequest(ontologies, aiModel, dataSource)
print('Output by LLM: ' + metadata)
parsed_metadata, data_xml, data_csv, data_rdf = parseMetadata(ontologies, metadata)
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
