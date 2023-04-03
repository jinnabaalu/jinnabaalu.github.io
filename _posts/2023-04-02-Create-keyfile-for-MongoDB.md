---
layout: post
title:  "Create the keyfile for Internal Authentication"
categories: [ MongoDB, NoSQL ]
image: assets/img/mongodb/3.png
featured: false
githublink: https://github.com/JinnaBalu/docker-mongo
githubreponame: docker-mongo
---

### Enabling Auth for Security

Generate keyfile for the machine you are working with

#### Mac

Create the file if you are on mac and running as a container

    $ openssl rand -base64 741 >> mongoKeyFileMac

    $ chmod 600 mongoKeyFileMac

#### Linux

Create the file if you are on linux and running as a container

    $ openssl rand -base64 756 > mongoKeyFileLinux

    $ chmod 600 mongoKeyFileLinux

    $ sudo chown 999 mongoKeyFileLinux

    $ sudo chgrp 999 mongoKeyFileLinux



#### Reference

- [Deploy New Replica Set with Keyfile Access Control](https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-with-keyfile-access-control/#deploy-new-replica-set-with-keyfile-access-control)