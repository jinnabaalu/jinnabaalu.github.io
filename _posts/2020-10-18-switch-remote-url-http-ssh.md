---
layout: post
title: "Git - Switch Remote URL"
description: "Git - Switch Remote URL | HTTPS | SSH"
author: jinnabalu
categories: [ git ]
image: assets/img/git_remote_url.png
featured: false
hidden: true
---

# Switching remote URLs from HTTPS to SSH

## List existing URLs

- List your existing remotes in order to get the name of the remote you want to change.


```code
git remote -v

# Output

origin	https://github.com/JinnaBalu/jinnabalu.github.io.git (fetch)
origin	https://github.com/JinnaBalu/jinnabalu.github.io.git (push)

```
## Change your remote's URL

- Change your remote's URL from SSH to HTTPS with the `git remote set-url` command.

```bash
git remote set-url origin https://github.com/USERNAME/REPOSITORY.git
```
