#!/bin/bash

# Start the Python exporter in the background and log output
python3 /opt/oai-gnb/gnb_metrics_exporter.py > /var/log/gnb_metrics_exporter.log 2>&1 &

# Start the nr-softmodem process
exec /opt/oai-gnb/bin/nr-softmodem "$@"