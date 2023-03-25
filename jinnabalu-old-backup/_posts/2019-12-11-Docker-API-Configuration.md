---
title:  "Docker API Configuration"
metadate: "hide"
categories: [ DockerAPI ]
tags: [ Jenkins ]
image: "assets/images/docker-engine-components-flow.png"
---


- Engine API is an HTTP API served by Docker Engine, How to enable docker API on docker host?
- Controlling the Docker Engine from any SDK.
- Is everything the Docker client can do can be done with the API?

To answer the above, Docker provides an API for interacting with the Docker daemon (called the Docker Engine API). The Engine API is an HTTP API served by Docker Engine. It is the API the Docker client uses to communicate with the Engine, so everything the Docker client can do can be done with the API.

### Docker service configuration 

```bash
nano /lib/systemd/system/docker.service
```

- Find the line which starts with ExecStart and adds -H=tcp://0.0.0.0:2375 to make it look like

```bash
.....
...
ExecStart=/usr/bin/dockerd -H=fd:// -H=tcp://0.0.0.0:2375
....
..
```

- Reload the docker daemon and restart the service

```bash
systemctl daemon-reload
sudo service docker restart
```

### Test the configuration 

```bash
curl http://localhost:2375/images/json
```

Replace `localhost` with the respective `IP` if we need to connect to a remote docker deamon. 