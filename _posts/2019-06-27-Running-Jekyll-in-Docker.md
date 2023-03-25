---
layout: post
title:  "Jekyll - Running Jekyll in Docker"
author: jinna
categories: [ jekyll, Dev ]
image: assets/img/jekyll.png
---
# Running Jekyll in Docker

According to the official documentation og jekyll, Jekyll is a blog-aware, static site generator in Ruby and in order to install it you need to ensure that you have the

* correct version of Ruby installed
* RubyGems installed
* GCC / Make installed

If you’re not familiar with these tools (ruby , gem, bundle, ….) then getting up and running can be time consuming. But if you are familiar with `docker run` command is the only pre requisite to make app up and running with the `jekyll/jekyll` docker image.

##Prerequisites

* docker
* docker-compose

## Create the jekyll app

```bash
export JEKYLL_VERSION=3.8
mkdir -p $PWD/path/of/new/app; cd $PWD/path/of/new/app
docker run --rm --volume="$PWD:/srv/jekyll" -it jekyll/jekyll:$JEKYLL_VERSION jekyll new .
```
#### What happened here ?

* We’ve started a docker jekyll container
* We’ve mounted the current folder as /srv/jekyll in the container
* We’ve passed the jekyll new command
* A new site was created in the current folder by the container

## Build the app

```bash
docker run --rm --volume="$PWD:/srv/jekyll" -it jekyll/jekyll:$JEKYLL_VERSION jekyll build
```

## RUN
- create a docker-compose file for the application

```bash
cat << EOF > docker-compose.yaml

version: '3'
services:
  site:
    container_name: jinnabalu
    command: jekyll serve --watch --drafts
    image: jekyll/jekyll:latest
    volumes:
      - $PWD:/srv/jekyll
    ports:
      - 4000:4000
EOF
```

- run


```bash
docker-ompose up -d
```

Application will be running on [http://localhost:4000](http://localhost:4000) or [http://127.0.0.1:4000](http://127.0.0.1:4000)

## Install Gems

#### Option #1 : Post running, if we want to install anything manually 

`docker exec -ti jinnabalu gem install "jekyll-theme-hydeout"`

#### Oprion #2 : If you want to deploy automatically, update `Gemfile'

```bash
group :jekyll_plugins do
   gem "jekyll-feed", "~> 0.6"
   gem "jekyll-gist", "~> 1.4"
   gem "jekyll-paginate", "~> 1.1"
   gem "jekyll-theme-hydeout", "~> 3.4"   
end
```

Next, in our `_config.yml` file, we’ll enable pagination, set the theme to `jekyll-theme-hydeout` add add some plugins

```bash
paginate:5

# Build settings
markdown: kramdown
theme: jekyll-theme-hydeout
plugins:
  - jekyll-feed
  - jekyll-gist
  - jekyll-paginate  
```

restart the service

```bash
docker-compose down

docker-compose up -d
```