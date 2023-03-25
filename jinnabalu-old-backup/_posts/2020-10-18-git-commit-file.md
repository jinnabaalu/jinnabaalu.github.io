---
layout: post
title: "Git - Commit Files"
description: "Git - Commit Files"
author: jinnabalu
categories: [ Devops, git ]
image: assets/images/git_commit.png
featured: false
hidden: true
---
## Status

```bash
git status
```

## Git Add

```bash
git add .

# OR

git add --all

# OR

git add hello-world.js

# OR

git add dir/
```

## Check status

```bash
git status
```

## Commit

```bash
git commit -am "hello world changes"
```

`-am` : All commits with message

## Push

```bash
git push -u origin branchName

# OR

git push # pushes the current branch to the configured upstream
```