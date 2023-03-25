---
layout: post
title:  "Dockerise HTML"
description: "Running the Static HTML webpages as container on docker"
author: jinna
categories: [ Dockerization ]
image: assets/images/html-5.svg
---

{% include docker-prerequisites.md %}

## Create a sample static app

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <title>Platform Ops</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js"></script>

</head>
<body>

<div class="jumbotron">
  <h1>Platform Ops</h1> 
  <p>Anything and Everything as container</p> 
</div>
</body>
</html>
```

## Option #1

## Deploy Static app as container with nginx image

Create a `docker-compose.yml`

```yml
version: "3"
services:
  static-app:
    image: nginx:1.17
    container_name: platform-ops
    volume:
      - . /usr/share/nginx/html
    deploy:
      replicas: 1
    ports:
      - 80:80
```

- RUN the container

```bash
docker-compose up -d
```

## Option #2

## Create a Dockerfile to create a custom image

Create a Dockerfile with `NGINX` as base image, copying the static content of the website.

```Dockerfile
FROM nginx:1.17
COPY . /usr/share/nginx/html
```

1. `FROM nginx:1.17` - Base image of the container, with the version `1.17`
2. `COPY . /usr/share/nginx/html` - Copying the content of the current directory `.` to `/usr/share/nginx/html` location of the container.


## Create a docker image

`Docker CLI` will use the Dockerfile, to create the docker image. Here is the docker build command to create the image

```bash
docker build -t platform-ops-static .
```

By default it create a image with latest tag.

OR 

To create the docker image with tag as follows

```bash
docker build -t platform-ops-static:v1 .
```

1. `platform-ops-static` - image name
2. `v1` - tag to maintain the version between the images

## Deploy Static app as container

Create a `docker-compose.yaml`

```yaml
version: "3"
services:
  static-app:
    image: platform-ops-static
    container_name: platform-ops
    deploy:
      replicas: 1
    ports:
      - 80:80
```
- RUN the container

```bash
docker-compose up -d
```