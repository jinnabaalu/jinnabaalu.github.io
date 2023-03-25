---
layout: post
title: "Git - Reset Commits"
description: "Git - Reset Commits"
author: jinnabalu
categories: [ Devops, git ]
image: assets/images/git_reset_commit.png
featured: false
hidden: true
---

# Remove the last commit/commits using Reset

## Steps to remove the last commit/commits

#### **Step 1** Checkout to master

```bash
git checkout master
```

> Note : This could be done in any branch. For this example, *master* branch is used.

#### **Step 2** -  Get the commits history

```bash
git log
```

You will end up with list of commits that you made as follows.

![logs](https://user-images.githubusercontent.com/22785263/47548190-d2dc6580-d915-11e8-8591-c470511ddae0.PNG)

#### Step 3 - Reset

**Step 3.1** - Copy the commit-hash that you want to reset

All the commits that top of the selected commit-hash (not including the entered commit-hash), will be deleted.

**Step 3.2** - Hard reset to go back to early stage

```bash
git reset <commit-hash> --hard
```

Options to reset 

1. Soft Reset

```bash
git reset <commit_hash> --soft
```

2. Mixed Reset

```bash
git reset <commit_hash>

#OR

git reset <commit_hash> --mixed
```

3. Hard Reset

```bash
git reset <commit_hash> --hard
```


#### Step 3 - Force push to the repository

```bash
git push <remote> master --force
```

`<remote>` can be any remote, `origin` is the default.

> NOTE : Be careful when removing the previous commits, there is no going back once you did these changes.


#### Rebase

We can also re-write history commits in a different place

```bash
git rebase <commit-hash>
```

#### Revert

Inverse the changes from history and create a new commit 

```bash
git revert <commit-hash>
```

