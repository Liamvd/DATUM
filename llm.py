import pandas as pd
import google.generativeai as genai
import xml.etree.ElementTree as ET
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


# Create prompt request and return metadata in xml format
def promptRequest(df_ontologies, model, source):
    prompt = 'Read the source: ' + source + ' And read the list of ontologies in this dataframe: ' + str(
        df_ontologies.parse('All')[
            'Ontology Concept']) + 'Decide to which ontology the source fits best and remember the row number of that ' \
                                   'ontology. Check the row number corresponding to that number in the following ' \
                                   'dataframe: ' + str(
        df_ontologies.parse('All')[
            'Properties']) + 'For each property in that row, create a property value based on the source. If nothing ' \
                             'relevant can be found in the source, leave the property blank. Your answer should only ' \
                             'consist of the following structure: Ontology concept, Property name 1: Property value ' \
                             '1, Property name 2: Property value 2, etc '
    response = model.generate_content(prompt)
    return response.text


# Put the results from the LLM in the proper format to export
def parseMetadata(df_ontologies, results):
    parsed_results = {}
    results_list = results.split(',')
    count = 0
    for i in results_list:
        if count == 0:
            for sheet_name in df_ontologies.sheet_names[1:]:
                df_sheet = df_ontologies.parse(sheet_name)
                if i in df_sheet['Ontology Concept'].values:
                    parsed_results['Category'] = sheet_name
                    parsed_results['Ontology'] = i
                    break
        else:
            i_split = i.split(':')
            parsed_results[i_split[0].strip()] = i_split[1].strip()
        count += 1
    return parsed_results


ontologies = readOntologies('Ontologies.xlsx')
aiModel = configureAi()
dataSource = getSource()
print('Source: ' + dataSource)
metadata = promptRequest(ontologies, aiModel, dataSource)
print('Output by LLM: ' + metadata)
parsed_metadata = parseMetadata(ontologies, metadata)
print('Final output: ')
print(parsed_metadata)

# TO DO: save output to appropriate format, or make cedar integration
# Save metadata as xml file; placeholder until automatic cedar integration
# """
# tree = ET.ElementTree(metadata.text)
# with open('metadata.xml', 'wb') as file:
#    tree.write(file, encoding='utf-8', xml_declaration=True)
# """
