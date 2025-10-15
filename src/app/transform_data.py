from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from datetime import datetime
from dateutil import parser
#from google import genai
import os, re


def ai_solution(input_data, var):
    #client = genai.Client()
    return


def define_namespaces(dataset):
    # dynamically define namespaces based on input data
    namespaces = []
    return namespaces


def get_data_record(input_data, var):
    # Define the dictionary keys to be populated (CDM structure)
    keys = [
        "case_id", "date_received", "incident_date", "topic", "town",
        "state", "perpetrators", "violations", "narrative", "publication_link"
    ]

    # Initialise the dictionary with empty strings
    record = {key: "" for key in keys}

    # Use regular expressions to find each key and extract its value
    for key in keys:
        pattern = re.compile(rf'{key}\s*:\s*(.*?)(?=\n\w+\s*:|$)', re.IGNORECASE | re.DOTALL)
        match = pattern.search(input_data[var]["data"])

        if match:
            value = match.group(1).strip()
            value = re.sub(r'\s*\n\s*', ' ', value)
            record[key] = value
    return record


def code_solution(input_data, var):
    # --- Define Namespaces - Dynamic version ---
    #namespaces = define_namespaces(var)

    # --- Define Namespaces - Hardcoded CDM version ---
    EX = Namespace("http://example.org/sv/")
    SVO = Namespace("http://example.org/sv/ontology#")
    SCHEMA = Namespace("http://schema.org/")

    record = get_data_record(input_data, var)

    g = Graph()
    g.bind("svo", SVO)
    g.bind("schema", SCHEMA)
    g.bind("ex", EX)

    case_id = record.get("case_id")
    if not case_id:
        return g  # Cannot process without a case ID

    # Create a main URI for the Incident
    incident_uri = EX[f"incident/{case_id}"]
    g.add((incident_uri, RDF.type, SVO.Incident))
    g.add((incident_uri, SVO.hasCaseNumber, Literal(case_id)))

    # --- Data Cleaning and Transformation - Hardcoded CDM version ---

    # Handle dates
    try:
        # Attempt to parse different date formats
        inc_date_str = record.get("incident_date")
        if inc_date_str:
            dt = datetime.strptime(inc_date_str, "%Y-%m-%d")  # Assumes YYYY-MM-DD
        g.add((incident_uri, SVO.incidentDate, Literal(dt.date(), datatype=XSD.date)))
    except (ValueError, TypeError):
        # Add robust date parsing for other formats if needed
        pass

    # Handle text fields (cleaning)
    topic = record.get("topic")
    if topic:
        g.add((incident_uri, SVO.hasTopic, Literal(topic.strip().title())))

    violations = record.get("violations")
    if violations:
        g.add((incident_uri, SVO.hasViolationType, Literal(violations.strip())))

    # Link to Location
    town = record.get("town")
    if town:
        location_uri = EX[f"location/{town.replace(' ', '_')}"]
        g.add((location_uri, RDF.type, SCHEMA.Place))
        g.add((location_uri, SCHEMA.addressTown, Literal(town)))
        g.add((incident_uri, SVO.hasLocation, location_uri))

    # Add Perpetrator
    perps = record.get("perpetrators")
    if perps:
        perp_uri = EX[f"perpetrator/{perps.replace(' ', '_')}"]
        g.add((perp_uri, RDF.type, SVO.Perpetrator))
        g.add((perp_uri, SCHEMA.name, Literal(perps)))
        g.add((incident_uri, SVO.involvesPerpetrator, perp_uri))

    turtle_data = g.serialize(format='turtle')

    return turtle_data


def transform_data(input_data):
    # data is transformed into rdf based on chosen format
    for var in input_data:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "dataset.ttl")

        if input_data[var].get("format") == 'structured':
            # --- LLM solution - Not yet implemented ---
            #input_data[var]["rdf"] = ai_solution(input_data, var)

            # --- Code solution ---
            input_data[var]["rdf"] = code_solution(input_data, var)

            with open(file_path, "w") as f:
                f.write(input_data[var]["rdf"])

        elif input_data[var].get("format") == 'unstructured':
            # TO DO
            input_data[var]["rdf"] = 'unstructured'
        else:
            # TO DO
            input_data[var]["rdf"] = ''

    return input_data


def determine_data_format(input_data):
    # determine the format the data is in to know which approach should be taken
    for var in input_data:
        # TO DO determine data format for each data set and add it to its dictionary
        data_formats = ['structured', 'unstructured']
        input_data[var]["format"] = 'structured'
    return input_data


def transform_to_rdf(file, url, text):
    print('File input: ' + file)
    print('URL input: ' + url)
    print('Text input: ' + text)
    input_data = {}

    for var, name in [(file, "File_input"), (url, "Url_input"), (text, "Text_input")]:
        if len(var) == 0:
            print(f"{name} is empty")
        else:
            input_data[name] = {"data": var}

    input_data = determine_data_format(input_data)
    transformed_data = transform_data(input_data)
    print('Transformed_data: ' + str(transformed_data))

    return transformed_data