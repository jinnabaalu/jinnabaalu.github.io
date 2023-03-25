---
layout: post
title: "Kafka - Ops"
description: "Kafka - Ops"
author: jinnabalu
categories: [ Devops, Kafka, Docker ]
image: assets/images/kafka.svg
featured: false
hidden: true
---

#  Kafka Operations

- Create a topic 

```bash
docker run \
  --net=host \
  --rm \
  confluentinc/cp-kafka:4.0.0 \
  kafka-topics --create --topic test_topic_name --partitions 3 --replication-factor 2 --if-not-exists --zookeeper  localhost:22181
```

- List the Topics

```bash
docker run \
  --net=host \
  --rm \
  confluentinc/cp-kafka:4.0.0 \
  kafka-topics --list --zookeeper  localhost:22181
```

- Delete the topic

```bash
docker run --net=host --rm confluentinc/cp-kafka:4.0.0 kafka-topics --zookeeper localhost:22181 --delete --topic test_topic_name
```


### Modify the Replicas

To increase the number of replicas for a given topic you have to:

1. Specify the extra replicas in a custom reassignment json file

For example, you could create `increase-replication-factor.json` and put this content in it:


```json
{"version":1,
  "partitions":[
     {"topic":"signals","partition":0,"replicas":[0,1,2]},
     {"topic":"signals","partition":1,"replicas":[0,1,2]},
     {"topic":"signals","partition":2,"replicas":[0,1,2]}
]}
```

2. Use the file with the --execute option of the `kafka-reassign-partitions` tool or `kafka-reassign-partitions.sh` depending on the kafka package

For example:

```bash
docker run -v $PWD:/home/   --net=host   --rm   confluentinc/cp-kafka:4.0.0 kafka-reassign-partitions --zookeeper localhost:22181 --reassignment-json-file /home/increase-replica.json --execute
```

3. Verify the replication factor with the `kafka-topics` tool or `kafka-topics.sh` - depending on the kafka package

```bash
docker run \
  --net=host \
  --rm \
  confluentinc/cp-kafka:4.0.0 \
  kafka-topics --zookeeper localhost:22181 --topic <TOPC_NAME> --describe



docker run --net=host --rm confluentinc/cp-kafka:4.0.0 kafka-consumer-groups --bootstrap-server 172.168.2.5:19092,172.168.0.1:29092,172.168.0.1:39092 --group <CONSUMER_GROUP_NAME> --describe
  
  
## expected sample output

Topic:signals   PartitionCount:3    ReplicationFactor:3 Configs:retention.ms=1000000000
Topic: signals  Partition: 0    Leader: 2   Replicas: 0,1,2 Isr: 2,0,1
Topic: signals  Partition: 1    Leader: 2   Replicas: 0,1,2 Isr: 2,0,1
Topic: signals  Partition: 2    Leader: 2   Replicas: 0,1,2 Isr: 2,0,1
```

## reset-offsets

```bash
docker run --net=host --rm confluentinc/cp-kafka:4.0.0 kafka-consumer-groups --bootstrap-server 172.168.0.0:19092,172.168.0.1:29092,172.168.0.1:39092 --group <CONSUMER_GROUP_NAME> --reset-offsets --to-earliest --topic <TOPIC_NAME> --execute

docker run --net=host --rm confluentinc/cp-kafka:4.0.0 kafka-consumer-groups --bootstrap-server 172.168.0.0:19092,172.168.0.1:29092,172.168.0.1:39092 --group <CONSUMER_GROUP_NAME> --reset-offsets --to-earliest --topic <TOPIC_NAME> --execute
```



### Describe the Topic/Group

```bash
docker run --net=host --rm confluentinc/cp-kafka:4.0.0 kafka-consumer-groups --bootstrap-server 172.168.0.0:19092,172.168.0.1:29092,172.168.0.1:39092 --group <CONSUMER_GROUP_NAME> --describe
```