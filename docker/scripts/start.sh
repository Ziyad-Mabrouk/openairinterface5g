#!/bin/bash

# Start the Python exporter in the background
python3 /opt/oai-gnb/gnb_metrics_exporter.py &

# Start the nr-softmodem process
exec /opt/oai-gnb/bin/nr-softmodem "$@"