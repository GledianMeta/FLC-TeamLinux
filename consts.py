
from os import environ as env

PORT = env.get("PORT", 8080)
HOST = env.get("HOST", "127.0.0.1")
CFG_PATH="./config/"
DEF_PATH="./default/"
SUMOCFG="sumo.sumocfg"
SUMOADD="sumo.add.xml"
SUMONET="sumo.net.xml"
SUMOROUTE="sumo.rou.xml"
OUTPUT_PATH="./output/"
DEF_OUTPUT_OPTS={'netstate-dump','emission-output', 'chargingstations-output', 'statistic-output'}
COMPRESSION_LEVEL=8
LAST_EXTENSIONS = {'xml'}
PREV_EXTENSIONS = {'add', 'net', 'rou'}
FLOAT_BATT_PARAMS= {'device.stationfinder.probability','device.stationfinder.reserveFactor', 'device.stationfinder.emptyThreshold', 'device.stationfinder.maxChargePower', 'device.battery.probability'}
BOOL_BATT_PARAMS= {'device.stationfinder.deterministic', 'device.battery.deterministic','device.battery.track-fuel'}
TIME_BATT_PARAMS= {'device.stationfinder.rescueTime', 'device.stationfinder.radius', 'device.stationfinder.repeat','device.stationfinder.waitForCharge'}
STRING_BATT_PARAMS= {'device.stationfinder.chargeType'}
STRARR_BATT_PARAMS= {'device.stationfinder.explicit','device.battery.explicit'}
OUTPUT_OPTS={'write-license', 'output-prefix', 'human-readable', 'netstate-dump',
             'netstate-dump.empty-edges', 'netstate-dump.precision', 'emission-output',
             'emission-output.precision', 'emission-output.geo', 'emission-output.step-scaled',
             'battery-output', 'battery-output.precision', 'elechybrid-output',
             'elechybrid-output.precision', 'elechybrid-output.aggregated', 'chargingstations-output',
             'overheadwiresegments-output', 'substations-output', 'substations-output.precision',
             'fcd-output', 'fcd-output.geo', 'fcd-output.signals', 'fcd-output.distance',
             'fcd-output.acceleration', 'fcd-output.max-leader', 'fcd-output.params',
             'fcd-output.filter-edges.input-file', 'fcd-output.attributes', 'fcd-output.filter-shapes',
             'full-output', 'queue-output', 'queue-output.period', 'vtk-output',
             'amitran-output', 'summary-output', 'summary-output.period',
             'person-summary', 'tripinfo-output', 'tripinfo-output.write-unfinished',
             'tripinfo-output.write-undeparted', 'personinfo-output', 'vehroute-output',
             'vehroute-output.exit-times', 'vehroute-output.last-route',
             'vehroute-output.sorted', 'vehroute-output.dua', 'vehroute-output.cost',
             'vehroute-output.intended-depart', 'vehroute-output.route-length',
             'vehroute-output.write-unfinished', 'vehroute-output.skip-ptlines',
             'vehroute-output.incomplete', 'vehroute-output.stop-edges',
             'vehroute-output.speedfactor', 'vehroute-output.internal', 'personroute-output',
             'link-output', 'railsignal-block', 'bt-output', 'lanechange-output',
             'lanechange-output.started', 'lanechange-output.ended', 'lanechange-output.xy',
             'stop-output', 'stop-output.write-unfinished', 'collision-output', 'edgedata-output',
             'lanedata-output', 'statistic-output', 'save-state.times', 'save-state.period',
             'save-state.period.keep', 'save-state.prefix', 'save-state.suffix', 'save-state.files',
             'save-state.rng', 'save-state.transportables', 'save-state.constraints',
             'save-state.precision'}

# REGEX TO EXTRACT THIS FROM https://sumo.dlr.de/docs/sumo.html#output
# field_names = re.findall(r'--\w+\-\w*(?:\.\w+\-*\w*)*', text)