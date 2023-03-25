---
title:  "Update Jenkins on Ubuntu"
metadate: "hide"
categories: [ Devops ]
tags: [ Jenkins ]
image: "assets/images/jenkins.svg"
---

```bash
#on ubuntu, in /usr/share/jenkins:

sudo service jenkins stop
sudo mv jenkins.war jenkins.war.old
sudo wget https://updates.jenkins-ci.org/latest/jenkins.war
sudo service jenkins start
```