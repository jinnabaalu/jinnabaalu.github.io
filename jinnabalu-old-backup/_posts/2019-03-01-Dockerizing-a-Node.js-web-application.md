---
layout: post
title:  "Docker - dockerize the nodejs application"
author: jinnabalu
categories: [ Application, NodeJs, Container ]
image: assets/images/docker_nodejs.jpeg
description: "Create a nodejs application | Dockerize nodejs application"
featured: false
hidden: true
---

The main goal of this story is to dockerize the nodejs application. Assuming that you have come here after installing nodejs and docker.

Here is the [Github repo](https://github.com/JinnaBalu/dockerise-nodejs)

Check with the installations of nodejs and docker version

```bash
nodejs -v
docker version
```

1. Create a nodejs application (Skip this if you have running app)
2. Dockerize nodejs application

## Create a folder name app and use the same folder to create the nodejs application.

```bash
mkdir app
cd app/
```

Use the `npm init` command to create a `package.json` file for your application. For more information on how `package.json` works, see Specifics of npm’s package.json handling.

```bash
npm init # Will ask you basic questions about your app
```

This command prompts you for a number of things, such as the name and version of your application. For now, you can simply hit RETURN to accept the defaults for most of them, with the following exception:

```json
package.json
{
"name": "dockerise-nodejs",
"version": "1.0.0",
"description": "Dockerising NodeJS application",
"main": "index.js",
"scripts": {
"test": "echo \"Error: no test specified\" && exit 1"
},
"repository": {
"type": "git",
"url": "git+https://github.com/JinnaBalu/dockerise-nodejs.git"
},
"keywords": [],
"author": "",
"license": "ISC",
"bugs": {
"url": "https://github.com/JinnaBalu/dockerise-nodejs/issues"
},
"homepage": "https://github.com/JinnaBalu/dockerise-nodejs#readme",
"dependencies": {
"express": "^4.16.2"
}
}
```

Now install Express in the app directory and save it in the dependencies list.

```bash
npm install express --save
```

Then, create a `index.js` file that defines a web app using the `Express.js` framework and copy the following code into the file

```js
'use strict';
const express = require('express');
// Constants
const PORT = 8080;
const HOST = '0.0.0.0';
// App
const app = express();
app.get('/', (req, res) => {
 res.send('Hello world\n');
});
app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);
Create empty file called Dockerfile, used for creating the docker image
```

`touch Dockerfile`

Open the Dockerfile in your favorite text editor and copy the following.

```
FROM node:boron
WORKDIR /usr/src/app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 8080
CMD [ "npm", "start" ]
```

Create a `.dockerignore` file in the same directory as your Dockerfile with following content

```
node_modules
npm-debug.log
```

Go to the directory that has your Dockerfile and run the following command to build the Docker image. The `-t` flag lets you tag your image so it's easier to find later using the docker images command

```bash

docker build -t <image_name> .

# example : docker build -t nodejssample .
```

List the docker images

`docker images`

Create a docker-compose.yml file

```yaml

version: '2'
services:
 nodejs:
 image: nodejssample
 ports:
 - '8080:8080'
```

```bash
docker-compose up -d
```