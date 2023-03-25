---
layout: post
title:  "Jenkins - Upgrade Jenkins"
author: jinna
categories: [ Devops ]
image: assets/images/jenkins.svg
---

# Upgrade jenkins latest version 

- when we see the upgrade availble notifier in jenkins

- Jenkins is installed on ubuntu, in `/usr/share/jenkins`, do the following steps to upgrade

```bash
cd /usr/share/jenkins
sudo service jenkins stop
sudo mv jenkins.war jenkins.war.old
sudo wget https://updates.jenkins-ci.org/latest/jenkins.war
sudo service jenkins start
```
> Jenkins URL `https://updates.jenkins-ci.org/latest/jenkins.war` vary between versions available 