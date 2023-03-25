---
layout: post
title:  "Elasticsearch - Basics of Elasticsearch"
author: jinna
categories: [ Storage, Elasticsearch ]
image: assets/img/elasticsearch.svg
description: "Elasticsearch is the distributed search and analytics engine at the heart of the Elastic Stack. Logstash and Beats facilitate collecting, aggregating, and enriching your data and storing it in Elasticsearch. "
rating: 4.5
---

Elasticsearch is the distributed search and analytics engine at the heart of the Elastic Stack. Logstash and Beats facilitate collecting, aggregating, and enriching your data and storing it in Elasticsearch.

## Features include:

-  Distributed and Highly Available Search Engine.
-  Each index is fully sharded with a configurable number of shards.
-  Each shard can have one or more replicas.
-  Read / Search operations performed on either one of the replica shard.
-  Multi Tenant with Multi Types.
-  Support for more than one index.
-  Support for more than one type per index before 2.4.1
-  Index level configuration (number of shards, index storage, ...).
-  Various set of APIs
-  HTTP RESTful API
-  Native Java API.
-  All APIs perform automatic node operation rerouting.
-  Document oriented
-  No need for upfront schema definition.
-  Schema can be defined per type for customization of the indexing process.
-  Reliable, Asynchronous Write Behind for long term persistency.
-  (Near) Real Time Search.
-  Built on top of Lucene
-  Each shard is a fully functional Lucene index
-  All the power of Lucene easily exposed through simple configuration / plugins.
-  Per operation consistency
-  Single document level operations are atomic, consistent, isolated and durable.
-  Open Source under the Apache License, version 2 ("ALv2")

## Requirements

You need to have a recent version of Java installed. See the "Setup":http://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html#jvm-version page for more information.
