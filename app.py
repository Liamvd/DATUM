from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from llm import run_llm, export_xml, export_csv, export_rdf
import os
from dotenv import load_dotenv
import subprocess
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'

# Load environment variables
load_dotenv()

# Store generated outputs globally
outputs = {
    "data_xml": None,
    "data_csv": None,
    "data_rdf": None
}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect form data
        eventName = request.form.get('Event Name', '')
        date = request.form.get('Date', '')
        country = request.form.get('Country', '')
        region = request.form.get('Region', '')
        situation = request.form.get('Situation', '')
        
        # Convert inputs to JSON
        data = {
            "eventName": eventName,
            "date": date,
            "country": country,
            "region": region,
            "situation": situation
        }

        # Run LLM and collect results
        parsed_results, outputs['data_xml'], outputs['data_csv'], outputs['data_rdf'] = run_llm(data)

        # Create session data
        session['data'] = data
        session['parsed_results'] = parsed_results

        # Render the result page
        return render_template(
            "result.html",
            data=data,
            parsed_results=parsed_results
        )

    return render_template('index.html')


@app.route('/send_to_allegrograph')
def send_to_allegrograph():
    rdf_file_path = 'output/metadata.rdf'

    if not os.path.exists(rdf_file_path):
        flash("Error: RDF file 'metadata.rdf' not found in 'output' directory. Generate RDF first.", "warning")
        return render_template('result.html', data=session.get('data'), parsed_results=session.get('parsed_results'))

    try:
        event_name = session.get('data', {}).get('eventName')
        tree = ET.parse(rdf_file_path)
        root = tree.getroot()
        namespaces = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
        description = root.find('rdf:Description', namespaces)

        if description is not None:
            rdf_about = description.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about', '')
            if rdf_about.startswith("http://example.org/ontology/"):
                current_event_name = rdf_about[len("http://example.org/ontology/"):]
                current_event_name = current_event_name.replace('_', ' ')
            else:
                flash("Error: Incorrect RDF file. Unexpected URL format in rdf:about attribute.", "warning")
                return render_template('result.html', data=session.get('data'),
                                       parsed_results=session.get('parsed_results'))
        else:
            flash("Error: Incorrect RDF file. No rdf:Description element found.", "warning")
            return render_template('result.html', data=session.get('data'),
                                   parsed_results=session.get('parsed_results'))
        if event_name != current_event_name:
            flash("Error: Current RDF is not generated yet. Generate RDF first.", "warning")
            return render_template('result.html', data=session.get('data'),
                                   parsed_results=session.get('parsed_results'))

        result = subprocess.run(['python', 'allegrograph.py'], capture_output=True, text=True)

        if result.returncode == 0:
            ag_repo = os.getenv("ag_repo", "Unknown repository")
            ag_url = os.getenv("ag_url", "Unknown URL")
            flash(
                f"Your data has been passed to your AllegroGraph repository {ag_repo}. Access it by going to: {ag_url}",
                "success")
        else:
            flash(f"Error executing AllegroGraph script: {result.stderr}", "danger")

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")

    return render_template('result.html', data=session.get('data'), parsed_results=session.get('parsed_results'))


@app.route('/add_another_event')
def add_another_event():
    return redirect(url_for('index'))


@app.route('/output/xml')
def output_xml():
    if outputs['data_xml'] is None:
        flash("No XML data available to download. Please process the data first.", "warning")
        return redirect(url_for('index'))
    try:
        file_path = export_xml(outputs['data_xml'])
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"An error occurred while generating the XML file: {str(e)}", "danger")
        return redirect(url_for('index'))


@app.route('/output/csv')
def output_csv():
    if outputs['data_csv'] is None:
        flash("No CSV data available to download. Please process the data first.", "warning")
        return redirect(url_for('index'))
    try:
        file_path = export_csv(outputs['data_csv'])
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"An error occurred while generating the CSV file: {str(e)}", "danger")
        return redirect(url_for('index'))


@app.route('/output/rdf')
def output_rdf():
    if outputs['data_rdf'] is None:
        flash("No RDF data available to download. Please process the data first.", "warning")
        return redirect(url_for('index'))
    try:
        file_path = export_rdf(outputs['data_rdf'])
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"An error occurred while generating the RDF file: {str(e)}", "danger")
        return redirect(url_for('index'))


if __name__ == '__main__':
    os.makedirs("output", exist_ok=True)
    app.run(debug=True)
