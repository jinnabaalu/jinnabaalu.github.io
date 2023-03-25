---
layout: post
title:  "CICD Jenkins - Send email with default content"
metadate: "hide"
categories: [ jenkins ]
image: assets/img/jenkins.svg
---

# Send email with default content as the build output

#### Prerequisite Plugins
-[Email-ext plugin](https://wiki.jenkins-ci.org/display/JENKINS/Email-ext+plugin)

#### Steps

- Create new job with freestyle
- [Optional]In Source Code Management section configure the git if required
- Configure the build section with type of build 
- Post-build Actions select Editable email notification configue the following properties

   Project Recipient List: `email@email.com,example@example.example`

   Project Reply-To List: `no-reply@domain.com`

   Content Type: Select as required

   Default Subject: Subject 

   Default Content: 
                    
          Option1: Content Type - Text -> `${BUILD_LOG_EXCERPT, start="^Start", end="^End"}`

          Option2: Content Type - html -> `<pre>${BUILD_LOG_EXCERPT, start="^Start", end="^End"}</pre>`

- Save and test

**Example:**

**How to send build output as email to the specific email?**

- Execute shell 

```bash
echo "Start"

git log --since="1 week ago" --pretty=format:'%cd %<(20)%an %s' --date=format:'%Y-%m-%d %H:%M:%S'

echo "End"
```

- Post-build Actions select Editable email notification configue the following properties

   Project Recipient List: `jinna.balu@platform-ops.com`

   Project Reply-To List: `admin@platform-ops.com`

   Content Type: Select as required

   Default Subject: Developers Weekly Progress 

   Default Content: 
```bash
Hi All,
<br>
Here is the feature and bug progress of the week<br>

<pre>${BUILD_LOG_EXCERPT, start="^Start", end="^End"}</pre>

Regards<br>
Platform Ops Admin
```

- Save

 
