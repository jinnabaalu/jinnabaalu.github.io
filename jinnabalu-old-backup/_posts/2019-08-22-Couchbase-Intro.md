---
layout: post
title:  "Couchbase Introduction"
description: "Couchbase is an open-source, distributed multi-model NoSQL document-oriented database, multinode cluster. Couchbase Server is designed to provide easy-to-scale key-value or JSON document access with low latency and high sustained throughput"
author: jinna
categories: [ Storage ]
image: assets/images/couchbase_main.png
---
 
### What is Couchbase Server? 

I won’t spend the time to explain the intro material here but wanted to correctly identify brief explanation about the basics and we will work on running the couchbase as a container.

Couchbase is an open-source distributed multi-node-model NoSQL document-oriented database Multinode cluster. Features that are provided by the Couchbase at any scale are

- Elastic Scalability
- Consistent High Performance
- Always-On Availability
- Multi-Data Center Deployment
- Simple and Powerful Administration
- Enterprise-grade Security

Couchbase Server is designed to provide easy-to-scale key-value or JSON document access with low latency and high sustained throughput

In Multi node cluster every Couchbase node consists of a data service, index service, query service, and cluster manager component.

Couchbase is normally a CP type system meaning it provides [Consistency](https://en.wikipedia.org/wiki/Consistency_(database_systems)) and [partition tolerance](https://en.wikipedia.org/wiki/Network_partitioning), or it can be set up as an AP system with multiple clusters,  of Eric Brewer’s [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem)

Now the question, how do we run Couchbase as a container, Following are the Articles related to the containerisation of couchbase.

1. [Run Single Node Couchbase Container]({{ site.baseurl }}/Single-Node-Couchbase-Container/)

