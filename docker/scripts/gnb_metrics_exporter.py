from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import os
import time

registry = CollectorRegistry()

# MAC stats
rsrp = Gauge('gnb_average_rsrp_db', 'Average RSRP in dB', registry=registry)
ph = Gauge('gnb_ph_db', 'Power Headroom in dB', registry=registry)
snr = Gauge('gnb_snr_db', 'SNR in dB', registry=registry)
bler = Gauge('gnb_bler', 'BLER', registry=registry)
mcs = Gauge('gnb_mcs', 'MCS', registry=registry)
mac_tx = Gauge('gnb_mac_tx_bytes', 'MAC TX bytes', registry=registry)
mac_rx = Gauge('gnb_mac_rx_bytes', 'MAC RX bytes', registry=registry)

# L1 stats
avg_io = Gauge('gnb_avg_i0_db', 'Average I0 in dB', registry=registry)
prach_i0 = Gauge('gnb_prach_i0_db', 'PRACH I0 in dB', registry=registry)
ulsch_power = Gauge('gnb_ulsch_power', 'ULSCH Power', registry=registry)
ulsch_noise_power = Gauge('gnb_ulsch_noise_power', 'ULSCH Noise Power', registry=registry)

# RRC stats
rrc_activity = Gauge('gnb_rrc_last_activity_seconds', 'Time since last RRC activity', registry=registry)
pdu_status = Gauge('gnb_pdu_session_established', 'PDU Session Established (1/0)', registry=registry)

log_paths = {
    "mac": "/opt/oai-gnb/nrMAC_stats.log",
    "l1": "/opt/oai-gnb/nrL1_stats.log",
    "rrc": "/opt/oai-gnb/nrRRC_stats.log",
}

def parse_logs():
    # MAC stats parsing
    if os.path.isfile(log_paths["mac"]):
        try:
            with open(log_paths["mac"], "r") as f:
                mac = f.read()
                if match := re.search(r'PH\s+(\d+)', mac):
                    ph.set(int(match.group(1)))
                if match := re.search(r'average RSRP\s+(-?\d+)', mac):
                    rsrp.set(int(match.group(1)))
                if match := re.search(r'SNR\s+([\d.]+)\s+dB', mac):
                    snr.set(float(match.group(1)))
                if match := re.search(r'BLER\s+([\d.]+)', mac):
                    bler.set(float(match.group(1)))
                if match := re.search(r'MCS\s+\(\d+\)\s+(\d+)', mac):
                    mcs.set(int(match.group(1)))
                if match := re.search(r'MAC:\s+TX\s+(\d+)\s+RX\s+(\d+)', mac):
                    mac_tx.set(int(match.group(1)))
                    mac_rx.set(int(match.group(2)))
        except Exception as e:
            print(f"MAC parsing failed: {e}")

    # L1 stats parsing
    if os.path.isfile(log_paths["l1"]):
        try:
            with open(log_paths["l1"], "r") as f:
                l1 = f.read()
                if match := re.search(r'avg_I0\s+=\s+([\d.]+)', l1):
                    avg_io.set(float(match.group(1)))
                if match := re.search(r'PRACH I0\s+=\s+([\d.]+)', l1):
                    prach_i0.set(float(match.group(1)))
                if match := re.search(r'ulsch_power\[0\]\s+([\d,]+)', l1):
                    ulsch_power.set(float(match.group(1).replace(",", ".")))
                if match := re.search(r'ulsch_noise_power\[0\]\s+([\d.]+)', l1):
                    ulsch_noise_power.set(float(match.group(1)))
        except Exception as e:
            print(f"L1 parsing failed: {e}")

    # RRC stats parsing
    if os.path.isfile(log_paths["rrc"]):
        try:
            with open(log_paths["rrc"], "r") as f:
                rrc = f.read()
                if match := re.search(r'last RRC activity:\s+(\d+)', rrc):
                    rrc_activity.set(int(match.group(1)))
                if match := re.search(r'status\s+(\w+)', rrc):
                    status = 1 if match.group(1).lower() == "established" else 0
                    pdu_status.set(status)
        except Exception as e:
            print(f"RRC parsing failed: {e}")

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            parse_logs()  # On-demand parsing
            self.send_response(200)
            self.send_header('Content-Type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest(registry))
        else:
            self.send_response(404)
            self.end_headers()

def start_server(port=9090):
    print(f"Starting Prometheus exporter on port {port}")
    server = HTTPServer(('0.0.0.0', port), MetricsHandler)
    server.serve_forever()

if __name__ == '__main__':
    start_server()
