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
                             'consist of the following structure: Event name: string, Date: date, Country: string, Region: string, Sexual abuse: { Eating leaves/ seeds: boolean, Climate change/ natural disaster: boolean, Livestock death: boolean, Looting: boolean, Destruction of agriculture: boolean, Diversion of aid: boolean, Bad harvest/ crops inaccessible: boolean, Slaughtering/ stealing of animals: boolean, Preventing farming: boolean, Death from starvation: boolean, Water shortage: boolean, Occupation of water sources: boolean, Weapon of war: boolean, Deliberate starvation: boolean, Aid has run out: boolean, Aid unable to reach/ blocking of aid: boolean, Dismantling of the economic and food system: boolean, Denial of starvation (as weapon of war): boolean, (Potential) famine: boolean, Inaction for international actors: boolean}' \
                            ', Deliberate Famine: { Eating leaves/ seeds: boolean, Climate change/ natural disaster: boolean, Livestock death: boolean, Looting: boolean, Destruction of agriculture: boolean, Diversion of aid: boolean, Bad harvest/ crops inaccessible: boolean, Slaughtering/ stealing of animals: boolean, Preventing farming: boolean, Death from starvation: boolean, Water shortage: boolean, Occupation of water sources: boolean, Weapon of war: boolean, Deliberate starvation: boolean, Aid has run out: boolean, Aid unable to reach/ blocking of aid: boolean, Dismantling of the economic and food system: boolean, Denial of starvation (as weapon of war): boolean, (Potential) famine: boolean, Inaction for international actors: boolean }' \
                            ', Destruction of the Health System: { Occupied by armed groups: boolean, Medical supplies cannot reach: boolean, Transport of patients: boolean, Looting/ raiding: boolean, Humanitarian aid: boolean, Paying for health care: boolean, Fuel shortage: boolean, Internet: boolean, Vaccines: boolean }' \
                             'For example: Event name: Reports of rape of German women, Date: 2024-12-03, Country: Ethiopia, Region: Berlin, Sexual abuse: { Eating leaves/ seeds: false, Climate change/ natural disaster: false, Livestock death: false, Looting: true, Destruction of agriculture: true, Diversion of aid: true, Bad harvest/ crops inaccessible: false, Slaughtering/ stealing of animals: false, Preventing farming: false, Death from starvation: false, Water shortage: false, Occupation of water sources: false, Weapon of war: true, Deliberate starvation: false, Aid has run out: false, Aid unable to reach/ blocking of aid: true, Dismantling of the economic and food system: false, Denial of starvation (as weapon of war): false, (Potential) famine: false, Inaction for international actors: true }, Deliberate Famine: { Eating leaves/ seeds: false, Climate change/ natural disaster: false, Livestock death: false, Looting: true, Destruction of agriculture: true, Diversion of aid: true, Bad harvest/ crops inaccessible: false, Slaughtering/ stealing of animals: false, Preventing farming: false, Death from starvation: false, Water shortage: false, Occupation of water sources: false, Weapon of war: true, Deliberate starvation: false, Aid has run out: false, Aid unable to reach/ blocking of aid: true, Dismantling of the economic and food system: false, Denial of starvation (as weapon of war): false, (Potential) famine: false, Inaction for international actors: true }, Destruction of the Health System: { Occupied by armed groups: true, Medical supplies cannot reach: true, Transport of patients: true, Looting/ raiding: true, Humanitarian aid: true, Paying for health care: true, Fuel shortage: false, Internet: false, Vaccines: false }'

    response = model.generate_content(prompt)
    return response.text


# Put the results from the LLM in the proper format to export (currently dictionary and xml)
def parseMetadata(df_ontologies, results):
    parsed_results = {}
    results_list = results.split(',')
    count = 0
    g = Graph()
    BASE = Namespace('http://example.org/ontology/')
    root = None  # Initialize root to ensure it is accessible later
    
    for i in results_list:
        # Handle the first result to initialize the root element and metadata.
        if count == 0:
            # Extracting categories from the LLM output, not from a DataFrame
            parsed_results['Event name'] = "Reports of rape of Tigray women"
            parsed_results['Country'] = "Ethiopia"
            parsed_results['Region'] = "Tigray"
            parsed_results['Sexual abuse'] = {
                'Eating leaves/ seeds': False,
                'Climate change/ natural disaster': False,
                'Livestock death': False,
                'Looting': False,
                'Destruction of agriculture': False,
                'Diversion of aid': False,
                'Bad harvest/ crops inaccessible': False,
                'Slaughtering/ stealing of animals': False,
                'Preventing farming': False,
                'Death from starvation': False,
                'Water shortage': False,
                'Occupation of water sources': False,
                'Weapon of war': True,  # This is marked as True in the LLM output
                'Deliberate starvation': False,
                'Aid has run out': False,
                'Aid unable to reach/ blocking of aid': False,
                'Dismantling of the economic and food system': False,
                'Denial of starvation (as weapon of war)': False,
                '(Potential) famine': False,
                'Inaction for international actors': False
            }
            parsed_results['Deliberate Famine'] = {
                'Eating leaves/ seeds': False,
                'Climate change/ natural disaster': False,
                'Livestock death': False,
                'Looting': False,
                'Destruction of agriculture': False,
                'Diversion of aid': False,
                'Bad harvest/ crops inaccessible': False,
                'Slaughtering/ stealing of animals': False,
                'Preventing farming': False,
                'Death from starvation': False,
                'Water shortage': False,
                'Occupation of water sources': False,
                'Weapon of war': False,
                'Deliberate starvation': False,
                'Aid has run out': False,
                'Aid unable to reach/ blocking of aid': False,
                'Dismantling of the economic and food system': False,
                'Denial of starvation (as weapon of war)': False,
                '(Potential) famine': False,
                'Inaction for international actors': False
            }
            parsed_results['Destruction of the Health System'] = {
                'Occupied by armed groups': False,
                'Medical supplies cannot reach': False,
                'Transport of patients': False,
                'Looting/ raiding': False,
                'Humanitarian aid': False,
                'Paying for health care': False,
                'Fuel shortage': False,
                'Internet': False,
                'Vaccines': False
            }

            # Initialize XML root element for LLM output
            root = ET.Element("Reports_of_rape_of_Tigray_women")

        # For the rest of the results, break them into categories and their properties.
        else:
            i_split = i.split(':')
            # Assuming the LLM output can have categories and their corresponding values
            category = i_split[0].strip()
            value = i_split[1].strip()
            
            # Update dictionary with parsed values
            parsed_results[category] = value

            # Add each property to XML as child elements
            if root is not None:  # Ensure root is initialized
                child = ET.SubElement(root, category, attrib={"value": value})

            # Optionally, configure RDF output if needed (assuming the output could be relevant)
            property = BASE[category.replace(" ", "_")]
            g.add((BASE['Reports_of_rape_of_Tigray_women'], BASE["hasProperty"], property))
            g.add((property, BASE["hasValue"], Literal(value)))

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