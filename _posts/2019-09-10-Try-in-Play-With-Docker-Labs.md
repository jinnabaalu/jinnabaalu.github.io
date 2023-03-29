---
layout: post
title:  "Adding Try in PWD button to README file"
description: "Adding Try in PWD button to README file to click and play with services in play with docker"
categories: [ Docker ]
author: jinna
image: assets/img/play-with-docker.png
---


The "Try in PWD" actually supports to deploy any stack file that's available on the web. In the stack parameter you can either add a relative path of a stack in the stacks repo or a URL. 

#### Create the button with the following script

```bash
[![Try in PWD](https://cdn.rawgit.com/play-with-docker/stacks/cff22438/assets/img/button.png)](http://play-with-docker.com?stack=https://<my_stack_url>)
```

- Example to run wordpress as a container with the following

This is how the script looks like

```bash
[![Try in PWD](https://cdn.rawgit.com/play-with-docker/stacks/cff22438/assets/img/button.png)](http://play-with-docker.com?stack=https://raw.githubusercontent.com/JinnaBalu/wordpress/master/docker-compose-wordpress-mysql.yml) 
```
This is how the button look like

[![Try in PWD](https://cdn.rawgit.com/play-with-docker/stacks/cff22438/assets/img/button.png)](http://play-with-docker.com?stack=https://raw.githubusercontent.com/JinnaBalu/wordpress/master/docker-compose-wordpress-mysql.yml)


Additionally we wanted to have everything in one place (button + stacks) so users can click on the button and go to the [Play with Docker](https://labs.play-with-docker.com/)
