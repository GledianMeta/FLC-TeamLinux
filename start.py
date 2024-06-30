import os
from flask import Flask, request, make_response
from os import path, listdir, mkdir
import gzip
import xml.etree.ElementTree as ET
import xmltodict
import shutil
import ujson
from consts import *
from libraries.simulation import Simulation  # Importing Simulation class from simulation.py

app = Flask(__name__)
sim_instance = Simulation()  # <- Create simulation instance


def error_400(message):
    return make_response(message, 400)


def error_key(key):
    return error_400("Invalid value for key: " + key)


def check_config_files():
    return path.exists(CFG_PATH) and path.isfile(CFG_PATH + SUMOCFG) and path.isfile(
        CFG_PATH + SUMONET) and path.isfile(CFG_PATH + SUMOROUTE) and path.isfile(CFG_PATH + SUMOADD)


@app.route('/network', methods=['PUT'])
def upload_network():
    if not sim_instance.is_busy():
        if request.data is None:
            return error_400("No file part")
        if len(request.data) > 1e9:
            return error_400("File too big")
        file = request.get_data(as_text=True)
        try:
            file = ET.fromstring(file)
        except ET.ParseError:
            return error_400("Invalid XML file")
        if file.tag == "net" or file.tag == "network":
            root = ET.ElementTree(file)
            with open(path.join(app.config['UPLOAD_FOLDER'], SUMONET), 'wb') as f:
                root.write(f, xml_declaration=True, encoding="utf-8")
            return "File uploaded"
        return error_400("File not allowed")
    else:
        return error_400("Simulation is running, cannot modify network!")


@app.route('/routes', methods=['PUT'])
def upload_routes():
    if not sim_instance.is_busy():
        if request.data is None:
            return error_400("No file part")
        if len(request.data) > 1e9:
            return error_400("File too big")
        file = request.get_data(as_text=True)
        try:
            file = ET.fromstring(file)
        except ET.ParseError:
            return error_400("Invalid XML file")
        if file.tag == "routes":
            root = ET.ElementTree(file)
            with open(path.join(app.config['UPLOAD_FOLDER'], SUMOROUTE), 'wb') as f:
                root.write(f, xml_declaration=True, encoding="utf-8")
            return "File uploaded "
        return error_400("File not allowed")
    else:
        return error_400("Simulation is running, cannot modify routes!")


@app.route('/charging_stations', methods=['PUT'])
def upload_stations():
    if not sim_instance.is_busy():
        reset = request.args.get('reset', default=False)
        if request.data is None:
            return error_400("No file part")
        if len(request.data) > 1e9:
            return error_400("File too big")
        file = request.get_data(as_text=True)
        try:
            file = ET.fromstring(file)
        except ET.ParseError:
            return error_400("Invalid XML file")
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
        return error_400("File not allowed")
    else:
        return error_400("Simulation is running, cannot modify stations")


@app.route('/battery_options', methods=['POST'])
def battery_options():
    if not sim_instance.is_busy():
        if request.get_json() is not None and check_config_files():
            tree = ET.parse(CFG_PATH + SUMOCFG)
            root = tree.getroot()
            if root.tag != "configuration":
                return error_400("Invalid configuration file")
            battery_xml = root.find('battery') if root.find('battery') is not None else ET.Element("battery")
            battery_opts = request.get_json()
            for key in battery_opts:
                elem = ET.Element(key)
                if key in FLOAT_BATT_PARAMS or key in TIME_BATT_PARAMS:
                    if isinstance(battery_opts[key], float) or isinstance(battery_opts[key], int):
                        elem.set('value', str(battery_opts[key]))
                        battery_xml.append(elem)
                    else:
                        return error_key(key)
                elif key in BOOL_BATT_PARAMS:
                    if isinstance(battery_opts[key], bool) or (battery_opts[key] == "t" or battery_opts[key] == "f"):
                        elem.set('value', str(battery_opts[key]).lower())
                        battery_xml.append(elem)
                    else:
                        return error_key(key)
                elif key in STRING_BATT_PARAMS:
                    if isinstance(battery_opts[key], str):
                        elem.set('value', battery_opts[key])
                        battery_xml.append(elem)
                    else:
                        return error_key(key)
                elif key in STRARR_BATT_PARAMS:
                    if len(battery_opts[key]) > 0:
                        elem.set('value', ' '.join(battery_opts[key]))
                        battery_xml.append(elem)
                else:
                    return error_key(key)
            if root.find('battery') is None:
                root.append(battery_xml)
            tree.write(CFG_PATH + SUMOCFG, xml_declaration=True)
            return "Battery options updated!"
        else:
            return error_400("Invalid request, or configuration file not found")
    else:
        return error_400("Simulation is running, cannot modify battery options!")


@app.route('/output_options', methods=['POST'])
def output_options():
    if not sim_instance.is_busy():
        if request.get_json() is not None and check_config_files():
            tree = ET.parse(CFG_PATH + SUMOCFG)
            root = tree.getroot()
            if root.tag != "configuration":
                return error_400("Invalid configuration file")
            output_xml = root.find('output') if root.find('output') is not None else ET.Element("output")
            output_opts = request.get_json()
            for key in output_opts:
                elem = ET.Element(key)
                if key in OUTPUT_OPTS and key not in DEF_OUTPUT_OPTS:
                    elem.set('value', str(output_opts[key]))
                    output_xml.append(elem)
                else:
                    return error_key(key)
            if root.find('output') is None:
                root.append(output_xml)
            tree.write(CFG_PATH + SUMOCFG, xml_declaration=True)
            return "Output options updated!"
        else:
            return error_400("Invalid request, or configuration file not found")
    else:
        return error_400("Simulation is running, cannot modify output options!")


@app.route('/init_simulation')
def init_simulation():
    """resets simulation files"""
    if sim_instance.is_busy():
        return error_400("Another simulation is running, cannot reset files!")
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
    return make_response("Simulation initialized", 200) if check_config_files() else make_response(
        "Error initializing simulation", 500)


@app.route('/start_simulation')
def start_simulation():
    try:
        if check_config_files():
            begin = request.args.get('begin', default=0, type=int)
            end = request.args.get('end', default=None, type=int)
            step_duration = request.args.get('step_duration', default=1, type=int)  # in seconds
            n_steps = request.args.get('n_steps', default=-1, type=int)
            return "Simulation started" if sim_instance.configure(begin, end, step_duration, n_steps) else error_400("Another simulation is running") # <------ Configure Simulation instance
        else:
            return make_response("Error starting simulation, configuration files not found", 500)
    except Exception as e:
        return make_response(f"Error starting simulation: {str(e)}", 500)


@app.route('/next_step')
def next_step():
    n = request.args.get('n', default=sim_instance.n_steps, type=int)
    return "Next step taken" if sim_instance.do_steps(n) else error_400("Simulation is busy or not initialized (check /status for more)")



@app.route('/stop_simulation')
def stop_simulation():
    if sim_instance:
        sim_instance.stop_simulation()
        return "Stopped Simulation"


@app.route('/status')
def status():
    if sim_instance.is_busy():
        return "Simulation running"
    else:
        return "Simulation not running"


@app.route('/outputs')
def results():
    if sim_instance.is_busy():
        return error_400("sim_instance is running, wait until the end of it to get outputs")
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
        content = gzip.compress(ujson.dumps(body).encode('utf8'), COMPRESSION_LEVEL)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    """normal jsonify 24.61s 18.21MB, 
     gzip compression=9 takes 27.52s (1.98MB),
     gzip compression=7 takes 27.91s (2.04MB)
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
    app.run(HOST, PORT)
