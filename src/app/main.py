from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for, flash
from ontologyLinking import run_llm, export_xml, export_csv, export_rdf
from transform_data import *
from add_metadata import *
from send_to_allegrograph import *
import os
from dotenv import load_dotenv

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'

# Load environment variables
load_dotenv()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/communication')
def communication():
    return render_template('communication.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/transform', methods=['POST'])
def transform():
    data = request.get_json()
    file = data['file']
    url = data['url']
    text = data['text']
    result = transform_to_rdf(file, url, text)
    print('result: ' + str(result))
    session['rdf_result'] = result['Text_input']['rdf']
    rdf_data = {key: value.get('rdf', '') for key, value in result.items()}
    print('Rdf_data: ' + str(rdf_data))
    return jsonify({'rdf_transformed': rdf_data})


@app.route('/export', methods=['POST'])
def export():
    data = session['rdf_result']
    print('data: ' + str(data))
    SERVER_URL = "https://ag1xtpydmme0ldlr.allegrograph.cloud"
    REPO_NAME = "DATUM"
    USER = "admin"
    PASS = "T4pVVZCPb46dA1TNmqrHmq"
    send_to_allegrograph(data, SERVER_URL, REPO_NAME, USER, PASS)


if __name__ == '__main__':
    os.makedirs("../../output", exist_ok=True)
    app.run(debug=True)
