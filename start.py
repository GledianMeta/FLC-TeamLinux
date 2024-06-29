import json
import os

from flask import Flask, request, make_response
from flask_compress import Compress
import ujson
from os import path, listdir, mkdir
import gzip
import xml.etree.ElementTree as ET
import xmltodict
import shutil
from consts import *
from libraries.simulation import Simulation  # Importing Simulation class from simulation.py

app = Flask(__name__)
app.config["COMPRESS_REGISTER"] = False  # disable default compression of all eligible requests
app.config["COMPRESS_LEVEL"] = COMPRESSION_LEVEL
app.config['COMPRESS_ALGORITHM'] = 'deflate'
compress = Compress()
compress.init_app(app)


# Ensure the necessary directories and default files exist
if not path.isdir(CFG_PATH):
    mkdir(CFG_PATH)
if not path.isdir(DEF_PATH) or not path.isfile(DEF_PATH + SUMOCFG) or not path.isfile(DEF_PATH + SUMONET) or not path.isfile(DEF_PATH + SUMOROUTE) or not path.isfile(DEF_PATH + SUMOADD):
    raise FileNotFoundError("Default SUMO configuration files not found.")

# Global Simulation instance
sim_instance = None  # <------ Global variable to hold the instance of Simulation class

def check_config_files():
    return path.exists(CFG_PATH) and path.isfile(CFG_PATH + SUMOCFG) and path.isfile(
        CFG_PATH + SUMONET) and path.isfile(CFG_PATH + SUMOROUTE) and path.isfile(CFG_PATH + SUMOADD)




@app.route('/network', methods=['PUT'])
def upload_network():
    if request.data is None:
        return "No file part"
    if len(request.data) > 1e9:
        return "File too big"
    file = request.get_data(as_text=True)
    try:
        file = ET.fromstring(file)
    except ET.ParseError:
        return "Invalid XML file"
    if file.tag == "net" or file.tag == "network":
        root = ET.ElementTree(file)
        with open(path.join(app.config['UPLOAD_FOLDER'], SUMONET), 'wb') as f:
            root.write(f, xml_declaration=True, encoding="utf-8")
        return "File uploaded"
    return "File not allowed"


@app.route('/routes', methods=['PUT'])
def upload_routes():
    if request.data is None:
        return "No file part"
    if len(request.data) > 1e9:
        return "File too big"
    file = request.get_data(as_text=True)
    try:
        file = ET.fromstring(file)
    except ET.ParseError:
        return "Invalid XML file"
    if file.tag == "routes":
        root = ET.ElementTree(file)
        with open(path.join(app.config['UPLOAD_FOLDER'], SUMOROUTE), 'wb') as f:
            root.write(f, xml_declaration=True, encoding="utf-8")
        return "File uploaded "
    return "File not allowed"


@app.route('/charging_stations', methods=['PUT'])
def upload_stations():
    reset = request.args.get('reset', default=False)
    if request.data is None:
        return "No file part"
    if len(request.data) > 1e9:
        return "File too big"
    file = request.get_data(as_text=True)
    try:
        file = ET.fromstring(file)
    except ET.ParseError:
        return "Invalid XML file"
    if file.tag == "additional":
        if reset or not path.exists(CFG_PATH + SUMOADD):
            if path.exists(CFG_PATH + SUMOADD):
                os.remove(CFG_PATH + SUMOADD)
            root = ET.ElementTree(file)
            with open(path.join(app.config['UPLOAD_FOLDER'], SUMOADD), 'wb') as f:
                root.write(f, xml_declaration=True, encoding="utf-8")
        else:
            existree = ET.parse(CFG_PATH + SUMOADD)
            oldstations = existree.getroot()
            for station in file.iter('chargingStation'):
                oldstations.append(station)
            existree.write(CFG_PATH + SUMOADD, xml_declaration=True)
        return "File uploaded"
    return "File not allowed"


@app.route('/battery_options', methods=['POST'])
def battery_options():
    if request.get_json() is not None and check_config_files():
        tree = ET.parse(CFG_PATH + SUMOCFG)
        root = tree.getroot()
        if root.tag != "configuration":
            return "Invalid configuration file"
        battery_xml = root.find('battery') if root.find('battery') is not None else ET.Element("battery")
        battery_opts = request.get_json()
        for key in battery_opts:
            elem = ET.Element(key)
            if key in FLOAT_BATT_PARAMS or key in TIME_BATT_PARAMS:
                if isinstance(battery_opts[key], float) or isinstance(battery_opts[key], int):
                    elem.set('value', str(battery_opts[key]))
                    battery_xml.append(elem)
                else:
                    return "Invalid value for " + key
            elif key in BOOL_BATT_PARAMS:
                if isinstance(battery_opts[key], bool) or (battery_opts[key] == "t" or battery_opts[key] == "f"):
                    elem.set('value', str(battery_opts[key]).lower())
                    battery_xml.append(elem)
                else:
                    return "Invalid value for " + key
            elif key in STRING_BATT_PARAMS:
                if isinstance(battery_opts[key], str):
                    elem.set('value', battery_opts[key])
                    battery_xml.append(elem)
                else:
                    return "Invalid value for " + key
            elif key in STRARR_BATT_PARAMS:
                if len(battery_opts[key]) > 0:
                    elem.set('value', ' '.join(battery_opts[key]))
                    battery_xml.append(elem)
            else:
                return "Invalid parameter " + key
        if root.find('battery') is None:
            root.append(battery_xml)
        tree.write(CFG_PATH + SUMOCFG, xml_declaration=True)
        return "Battery options updated!"
    else:
        return "Invalid request, or configuration file not found"


@app.route('/output_options', methods=['POST'])
def output_options():
    if request.get_json() is not None and check_config_files():
        tree = ET.parse(CFG_PATH + SUMOCFG)
        root = tree.getroot()
        if root.tag != "configuration":
            return "Invalid configuration file"
        output_xml = root.find('output') if root.find('output') is not None else ET.Element("output")
        output_opts = request.get_json()
        for key in output_opts:
            elem = ET.Element(key)
            if key in OUTPUT_OPTS and key not in DEF_OUTPUT_OPTS:
                elem.set('value', str(output_opts[key]))
                output_xml.append(elem)
            else:
                return "Invalid parameter " + key
        if root.find('output') is None:
            root.append(output_xml)
        tree.write(CFG_PATH + SUMOCFG, xml_declaration=True)
        return "Output options updated!"
    else:
        return "Invalid request, or configuration file not found"


@app.route('/init_simulation')
def init_simulation():
    """resets simulation files"""
    if path.exists(CFG_PATH):
        shutil.rmtree(CFG_PATH)
    os.mkdir(CFG_PATH)
    if not (path.isfile(CFG_PATH + SUMOCFG)):
        shutil.copyfile(DEF_PATH + SUMOCFG, CFG_PATH + SUMOCFG)
    if not (path.isfile(CFG_PATH + SUMONET)):
        shutil.copyfile(DEF_PATH + SUMONET, CFG_PATH + SUMONET)
    if not (path.isfile(CFG_PATH + SUMOROUTE)):
        shutil.copyfile(DEF_PATH + SUMOROUTE, CFG_PATH + SUMOROUTE)
    if not (path.isfile(CFG_PATH + SUMOADD)):
        shutil.copyfile(DEF_PATH + SUMOADD, CFG_PATH + SUMOADD)
    return "Simulation initialized" if check_config_files() else "Error initializing simulation"


@app.route('/start_simulation')
def start_simulation():
    global sim_instance  # <------ Use global variable sim_instance
    try:
        if check_config_files():
            begin = request.args.get('begin', default=0)
            end = request.args.get('end', default=None)
            step_duration = request.args.get('step_duration', default=1)  # in seconds
            n_steps = request.args.get('n_steps', default=-1)
            sim_instance = Simulation(begin, end, step_duration, n_steps)  # <------ Create Simulation instance
            return "Simulation started"
        else:
            return "Error starting simulation, configuration files not found"
    except Exception as e:
        #app.logger.error(f"Error starting simulation: {str(e)}")
        return f"Error starting simulation: {str(e)}"


@app.route('/next_step')
def next_step():
    global sim_instance  # <------ Use global variable sim_instance
    if sim_instance:
        n = request.args.get('n')
        sim_instance.simulation_step(int(n))  # Example call to simulation_step method of Simulation class
        return "Next step taken"
    else:
        return "Simulation not yet started"


@app.route('/stop_simulation')
def stop_simulation():
    global sim_instance  # <------ Use global variable sim_instance
    if sim_instance:
        sim_instance.stop_simulation()
        sim_instance = None  # <------ Reset sim_instance
        return "Simulation stopped"
    else:
        return "Simulation not running"


@app.route('/status')
def status():
    global sim_instance  # <------ Use global variable sim_instance
    if sim_instance:
        return "Simulation running"
    else:
        return "Simulation not running"


@app.route('/outputs')
@compress.compressed()
def results():
    if len(request.args) == 0:
        available = []
        if path.exists(OUTPUT_PATH):
            for file in listdir(OUTPUT_PATH):
                if path.isfile(OUTPUT_PATH + file) and file.endswith('.xml'):
                    available.append(file.rsplit('.', 1)[0])
        return available
    else:
        body = []
        files = [el.rsplit('.', 1)[0] for el in listdir(OUTPUT_PATH) if el.endswith('.xml')]
        for key in request.args:
            if key in files:
                with open(OUTPUT_PATH + key + '.xml') as f:
                    xmldict = xmltodict.parse(f.read())
                    body.append({key: xmldict})
        return body
        """content=gzip.compress(ujson.dumps(body).encode('utf8'), COMPRESSION_LEVEL)
        response= make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response"""
    """normal jsonify response takes 47.11s,
     gzip compression=6 takes 47.33s (>2MB), 
     gzip compression=9 takes 48.16s (<2MB),
     Compress BR takes 47.10s (18.2MB),
     Compress GZIP takes 50s (1.98MB),
     
     """


@app.route('/hc')
def health_check():
    return "I'm alive"


if __name__ == "__main__":
    if not path.isdir(CFG_PATH):
        mkdir(CFG_PATH)
    if not (path.isdir(DEF_PATH)) or not (path.isfile(DEF_PATH + SUMOCFG)) or not (
            path.isfile(DEF_PATH + SUMONET)) or not (
            path.isfile(DEF_PATH + SUMOROUTE) or not (path.isfile((DEF_PATH + SUMOADD)))):
        raise FileNotFoundError("Default sumo configuration files not found,  machine is broken")
    app.config['UPLOAD_FOLDER'] = CFG_PATH
    app.run(HOST, port=8080)
