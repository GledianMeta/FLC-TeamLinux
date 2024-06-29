import os
from flask import Flask, request, make_response
import gzip
import ujson
from os import path
from os import listdir
from os import mkdir
import xml.etree.ElementTree as ET
import xmltodict
import shutil
from consts import *

app = Flask(__name__)
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
    if request.get_json() != None and check_config_files():
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
    if request.get_json() != None and check_config_files():
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
    if check_config_files():
        begin = request.args.get('begin', default=0)
        end = request.args.get('end', default=None)
        step_duration = request.args.get('step_duration', default=1)  # in seconds
        n_steps = request.args.get('n_steps', default=-1)
        return True
    else:
        return "Error starting simulation, configuration files not found"


@app.route('/next_step')
def next_step():
    if request.args.get('n') != None:
        #update simulation's step size
        n = request.args.get('n')
    return True


@app.route('/stop_simulation')
def stop_simulation():
    return True


@app.route('/status')
def status():
    return True


@app.route('/outputs')
def results():
    if(len(request.args)==0):
        available = []
        if path.exists(OUTPUT_PATH):
            for file in listdir(OUTPUT_PATH):
                if path.isfile(OUTPUT_PATH + file) and file.endswith('.xml'):
                    available.append(file.rsplit('.', 1)[0])
        return available
    else:
        body=[]
        files=[el.rsplit('.',1)[0] for el in listdir(OUTPUT_PATH) if el.endswith('.xml')]
        for key in request.args:
            if key in files:
                with open(OUTPUT_PATH+key+'.xml') as f:
                    xmldict=xmltodict.parse(f.read())
                    body.append({key:xmldict})
        content=gzip.compress(ujson.dumps(body).encode('utf8'), COMPRESSION_LEVEL)
        response= make_response(content)
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
