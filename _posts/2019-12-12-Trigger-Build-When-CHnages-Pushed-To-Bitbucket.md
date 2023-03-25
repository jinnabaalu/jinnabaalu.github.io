---
title:  "Trigger a Build in Jenkins using Bitbucket Hooks"
metadate: "hide"
categories: [ jenkins, bitbucket ]
tags: [ jenkins ]
image: "assets/img/jenkins_bibucket.jpg"
---


- How to build when a change is pushed to Bitbucket?
- Trigger a Build/Job in jenkins when chnages pushed to Bitbucket?
- How to Automate Build process when changes pushed to Bitbucket?


To answer the above, Jenkins provides a plugin, `Bitbucket plugin is designed to offer integration between Bitbucket and Jenkins`

### 1. Install “Bitbucket Plugin” at your Jenkins

- Jenkins Home ->  Manage Jenkins -> Plugin Manager -> Select Available Tab -> In searchbox enter  Bitbucket Plugin and enter

- Select the `Bitbucket Plugin` then Click on install and restart

### 2. Add Webhook to your Bitbucket repository (Repository Settings -> Webhooks -> Add Webhook)

![Bibucket Webhook](https://platform-ops.tech/assets/img/bitbucket_webhook.png)

Title: Test Webhook

URL: `http://cicd.platform-ops.tech/bitbucket-hook/` or `http://YOUR_JENKINS_SERVER:PORT/bitbucket-hook/`

SSL / TLS: [x] Skip certificate verification as we are using `http` in the URL

> NOTE: If we are seting up authentication on jenkins then URL must be like `https://USERNAME:PASSWORD@YOUR_JENKINS_SERVER:PORT/bitbucket-hook/`

Finally Click on Save


### 3. Configure Jenkins Job

Under Section build trigger enable Build when a change is pushed to BitBucket

Under Source Code Management select GIT; enter your credentials and define Branches to build