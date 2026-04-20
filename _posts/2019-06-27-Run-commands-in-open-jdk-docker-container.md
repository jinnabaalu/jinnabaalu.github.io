---
layout: post
title: "Running Commands Inside an OpenJDK Docker Container"
description: "How to access the shell, run commands, debug, and inspect an OpenJDK Docker container"
author: jinnabalu
categories: [ Devops, Docker ]
image: assets/img/logo.png
featured: false
hidden: true
---

When you run a Java application inside a Docker container, you often need shell access to debug, inspect logs, or verify the runtime environment. This guide covers the common ways to interact with an OpenJDK container.

## Start an OpenJDK Container

```bash
# Run an OpenJDK container in detached mode
docker run -d --name jinnabaluops openjdk:17-slim

# Verify it is running
docker ps
```

## Shell Access into the Container

Most OpenJDK images are based on Debian/Alpine, so the available shell differs:

```bash
# Debian-based images (openjdk:17, openjdk:17-slim)
docker exec -it jinnabaluops /bin/bash

# Alpine-based images (openjdk:17-alpine)
docker exec -it jinnabaluops /bin/sh
```

## Run One-Off Commands

You don't always need an interactive shell. Run a single command directly:

```bash
# Check Java version
docker exec jinnabaluops java -version

# Check environment variables
docker exec jinnabaluops env

# Check the current user
docker exec jinnabaluops whoami

# List files in the working directory
docker exec jinnabaluops ls -la /app
```

## Inspect the Java Runtime

```bash
# JVM default settings
docker exec jinnabaluops java -XX:+PrintFlagsFinal -version 2>&1 | grep -i heap

# Check available memory seen by the JVM
docker exec jinnabaluops java -XX:+PrintFlagsFinal -version 2>&1 | grep MaxHeapSize

# List running Java processes
docker exec jinnabaluops jps -lv
```

## View Logs

```bash
# Container stdout/stderr logs
docker logs jinnabaluops

# Follow logs in real time
docker logs -f jinnabaluops

# Tail the last 100 lines
docker logs --tail 100 jinnabaluops
```

## Copy Files In and Out

```bash
# Copy a JAR into the container
docker cp myapp.jar jinnabaluops:/app/myapp.jar

# Copy a log file out of the container
docker cp jinnabaluops:/app/logs/app.log ./app.log
```

## Inspect Container Details

```bash
# Full container metadata
docker inspect jinnabaluops

# Just the IP address
docker inspect -f '{{"{{.NetworkSettings.IPAddress}}"}}' jinnabaluops

# Mounted volumes
docker inspect -f '{{"{{json .Mounts}}"}}' jinnabaluops | python3 -m json.tool
```

## Troubleshooting Tips

| Problem | Command |
|---------|---------|
| Container exits immediately | `docker logs jinnabaluops` |
| Can't find `bash` | Use `/bin/sh` instead (Alpine images) |
| Need to install a tool | `docker exec jinnabaluops apt-get update && apt-get install -y curl` |
| Out of memory errors | Check `docker stats jinnabaluops` and adjust `--memory` flag |

## Cleanup

```bash
# Stop and remove the container
docker stop jinnabaluops && docker rm jinnabaluops
```

