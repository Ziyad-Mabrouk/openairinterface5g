from prometheus_client import start_http_server, Gauge
import time
import re
import os

# Define the metric
rsrp_gauge = Gauge('gnb_average_rsrp_db', 'Average RSRP in dB')

# Path to log file
log_file = '/opt/oai-gnb/nrMAC_stats.log'

# Regex to match average RSRP
rsrp_regex = re.compile(r'average RSRP (-?\d+)')

def follow(file):
    """Generator function that yields new lines in a file like `tail -F`."""
    file.seek(0, os.SEEK_END)  # Go to end of file
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.2)
            continue
        yield line

def extract_and_update(line):
    """Extract RSRP from line and update Prometheus metric"""
    match = rsrp_regex.search(line)
    if match:
        rsrp_val = int(match.group(1))
        rsrp_gauge.set(rsrp_val)

if __name__ == '__main__':
    # Start Prometheus HTTP server on port 9200
    start_http_server(9200)
    print("Prometheus exporter started on port 9200")

    try:
        with open(log_file, 'r') as f:
            for line in follow(f):
                extract_and_update(line)
    except FileNotFoundError:
        print(f"Log file {log_file} not found. Exiting.")
        exit(1)