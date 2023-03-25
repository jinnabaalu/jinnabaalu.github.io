---
layout: post
title:  "Elasticsearch - Dumping documents from multi-node to single node"
author: jinna
categories: [ Storage ]
image: assets/images/elasticsearch.svg
description: "Elasticsearch is running as three node cluster, task is to copy and restore the multi-node to single node cluster"
---


## Elasticsearch three node cluster:

Elasticsearch is running as three node cluster, task is to copy and restore the multi-node to single node cluster. 
 
```json
node 1 : "http://node1:9300, http://node1:9200"
node 2 : "http://node2:9300, http://node2:9200"
node 3 : "http://node2:9300, http://node3:9200"
```
As the shards getting distributed between nodes so no single node will have the complete data. When we manually copy and restore to single node instance there will be an unassigned shards of each node. Follow these steps to restore from multi node to single node.

- Create the single node cluster using the `docker-compose` file

```yml
cluster.name: vibhuvi_cluster
#node.name: "node-one"
#index.number_of_shards: 1
#index.number_of_replicas: 0
network.bind_host: 0.0.0.0
#network.host: 0.0.0.0
#discovery.zen.ping.multicast.enabled: false
cluster.routing.allocation.disk.threshold_enabled: true 
cluster.routing.allocation.disk.watermark.flood_stage: 200mb
cluster.routing.allocation.disk.watermark.low: 500mb 
cluster.routing.allocation.disk.watermark.high: 300mb
```

```yml
version: '2'
services:
    vibhuvi_cluster-elasticsearch:
        container_name: vibhuvi_cluster-elasticsearch
        image: elasticsearch:2.4.1
        environment:
            - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
        volumes:
            - /var/db/elasticsearch/data:/usr/share/elasticsearch/data
            - ./elasticsearch-conf.yml:/usr/share/elasticsearch/config/elasticsearch.yml
        ports:
            - 9200:9200
            - 9300:9300

```
- Copy the folder from `node 1`, with the `scp -r /var/db/node1/elasticsearch/** /var/db/cassandra`
- Start the cluster using `docker-compose up -d`
- By default, Elasticsearch will re-assign shards to nodes dynamically. with unassigned shards.
- Check with the shards with `curl -X GET "localhost:9200/_cat/shards"`
- Number of nodes in the cluster was three so there was no extra node to create the replica, and restore the unassigned indexes, So the health was turning to `red`. Created the index with settings property and set the number_of_replicas as 0.

```curl
curl -X PUT "localhost:9200/_settings?pretty" -H 'Content-Type: application/json' -d'
{
  "index" : {
    "number_of_replicas" : 0
  }
}
'
```
- Check with shards again and note down the number of unassigned node shards
- Manually copy the shards which are unassigned from `node 2` or `node 3`
- Example, copy index `client` shards 2, 4

```bash
scp -r <path_multinode_data_folder>/<cluster_name>/nodes/0/indices/client/2 <path_multinode_data_folder>/<cluster_name>/nodes/0/indices/client/

scp -r <path_multinode_data_folder>/<cluster_name>/nodes/0/indices/client/4 <path_multinode_data_folder>/<cluster_name>/nodes/0/indices/client/
```
- Restart the elasticsearch `docker-compose down` and `docker-compose up -d`
- Check with the shards and see if any unassigned shards exist and repeat the same as above.
- When we are done with restoring the shards, node health will be turned into the `green`


Missing shards can be copied manually to the folder. However, if you've disabled shard allocation (perhaps you did a rolling restart and forgot to re-enable it), you can re-enable shard allocation.

```bash
# v0.90.x and earlier
curl -X PUT "localhost:9200/_settings?pretty" -H 'Content-Type: application/json' -d'
    "index.routing.allocation.disable_allocation": false
}'

# v1.0+
curl -X PUT "localhost:9200/_settings?pretty" -H 'Content-Type: application/json' -d'
    "transient" : {
        "cluster.routing.allocation.enable" : "all"
    }
}'

```
Elasticsearch will then reassign shards as normal. This can be slow, consider raising indices.recovery.max_bytes_per_sec and cluster.routing.allocation.node_concurrent_recoveries to speed it up.

If you're still seeing issues, something else is probably wrong, so look in your Elasticsearch logs for errors. If you see EsRejectedExecutionException your thread pools may be too small.

Finally, you can explicitly reassign a shard to a node with the reroute API.

```bash
# Suppose shard 4 of index "my-index" is unassigned, so you want to
# assign it to node search03:
curl -XPOST "localhost:9200/_cluster/reroute" -H 'Content-Type: application/json' -d'
    "commands": [{
        "allocate": {
            "index": "my-index",
            "shard": 4,
            "node": "search03",
            "allow_primary": 1
        }
    }]
}'
```