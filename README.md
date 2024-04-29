# Prometheus Python Exporter for Mirth Connect

This Python script serves as a Prometheus exporter for Mirth Connect, allowing users to collect various metrics related to message processing and server health. Mirth Connect is an open-source integration engine that facilitates the exchange of healthcare information.

## Features
- **Metrics Collection**: Collects metrics such as messages received, sent, filtered, and errored per channel, as well as the current size of the Mirth server's storage.
- **Server Health Monitoring**: Monitors the state of the Mirth server and reports it as either up (0) or down (1).
- **Dynamic Configuration**: Configuration is read from a JSON file (`mirthConfig.json`), allowing users to specify the Mirth instance to monitor and authentication credentials.

## Requirements
- Python 3.x
- `prometheus_client` library (`pip install prometheus_client`)
- `mirthpy` library (`pip install mirthpy`)

## Configuration
The exporter requires a `mirthConfig.json` file in the same directory with the following structure:
```json
{
  "instance": "MIRTH_INSTANCE_URL",
  "username": "USERNAME",
  "password": "PASSWORD",
  "prometheusPort": PROMETHEUS_PORT_NUMBER
}
```

To specify a certain port to point at for Mirth, you can add `mirthPort` in the `mirthConfig.json` file. (Mirth's default port is 8443)
```json
{
  "instance": "MIRTH_INSTANCE_URL",
  "username": "USERNAME",
  "password": "PASSWORD",
  "mirthPort": MIRTH_PORT_NUMBER,
  "prometheusPort": PROMETHEUS_PORT_NUMBER
}
```

## Metrics
- **mirth_messages_received_total**: Number of messages received per channel.
- **mirth_messages_sent_total**: Number of messages sent per channel.
- **mirth_messages_filtered_total**: Number of messages filtered per channel.
- **mirth_messages_queued**: Number of messages currently queued per channel.
- **mirth_messages_errored_total**: Number of messages that encountered errors per channel.
- **mirth_server_size**: Size of the Mirth server's storage in bytes.
- **mirth_server_state**: State of the Mirth server (0 for up, 1 for down).
## Usage
1. Configure mirthConfig.json with the appropriate values.
2. Run the script (python mirth_exporter.py).
3. Access the metrics via Prometheus at the specified port (http://localhost:{prometheusPort} by default).

## Important Note
Ensure that the Mirth Connect server is reachable from the machine running the exporter, and the specified credentials have appropriate permissions for accessing Mirth's APIs.