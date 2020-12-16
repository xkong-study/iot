# CS7NS1 Scalable Computing Project 3: Vehicular Networking

Group 5 is:
- Basil Contovounesios
- Hasan Erbilen
- Shreya Jacobs
- David Kilroy
- Sneha Konoth

# Overview

Each Pi runs a single vehicle instance (`code/peerTry.py`) with any number of
coupled sensors of certain predefined types (`code/sensor.py`).  Each sensor
type is associated with a range of possible values, and broadcasts random values
in that range to its associated vehicle via sockets.  The following sensor types
with corresponding ranges are defined:

- `speed` (km/h): [40, 90]
- `proximity` (m): [1, 50]
- `pressure` (PSI): [20, 40]
- `heartrate` (BPM): [40, 120]

Each Pi can additionally run a single infrastructure instance (`code/infra.py`)
which acts as both a peer (via sockets) to other vehicles and a HTTP server for
other pods.  Inter-pod communication takes place via HTTP requests at the
well-known endpoint `/sensor` on port `33033`.  At minimum, conformant endpoints
serve a JSON object with speed, wiper speed, tyre pressure and fuel data, as
well as a list of other known peers.  We augment this object by also including
the latest intra-pod alert received.

# Dependencies

All of the nodes are implemented in Python 3.  Vehicle and sensors nodes use
only the standard library.  Infrastructure nodes additionally depend on
[Flask](https://flask.palletsprojects.com/) for serving the inter-pod API and
the [`requests`](https://requests.readthedocs.io/) library for querying other
pods, although this functionality is currently not used.

# Automation

You're probably looking for the `launch-tmux.sh` convenience script, which
automatically activates a Python virtual environment, installs the
aforementioned PyPI packages (running the script more than once should™ be
idempotent in this regard), and proceeds with spawning several network nodes,
each in its own `tmux` pane.  (It assumes that `bash`, `tmux`, and `python3`
executables are present in your `$PATH`.)

Running the script with no arguments should create the following view:

```
----------------------------------------------
|               Vehicle                      |
|--------------------------------------------|
| Speed sensor     | Tyre pressure sensor    |
|------------------|-------------------------|
| Proximity sensor | Driver heartrate sensor |
----------------------------------------------
```

Running the script with an argument `-i` additionally spawns an infrastructure
node:

```
----------------------------------------------
| Infrastructure          | Vehicle          |
|--------------------------------------------|
| Driver heartrate sensor | Speed sensor     |
|-------------------------|------------------|
| Tyre pressure sensor    | Proximity sensor |
----------------------------------------------
```

The intention is that `launch-tmux.sh` is launched once on each Pi/host, but the
script can be augmented to launch an abritrary number of sensors per host.

To exit the script, just close `tmux`, e.g. by typing its prefix (`Ctrl+b` by
default) followed by `&`.
