---
title:  "Basic Kafka Container commands"
metadate: "hide"
categories: [ Storage, Streaming ]
tags: [ Kafka ]
image: "assets/img/kafka.svg"
---


- Create Topic with container

```bash
docker run \
  --net=host \
  --rm \
  confluentinc/cp-kafka:4.0.0 \
  kafka-topics --create --topic 
test_topic_name --partitions 3 --replication-factor 2 --if-not-exists --zookeeper  localhost:22181
```

- List the popics with the container

```bash
docker run \
  --net=host \
  --rm \
  confluentinc/cp-kafka:4.0.0 \
  kafka-topics --list --zookeeper  localhost:22181
```

- Delete Topic

```bash
docker run --net=host --rm confluentinc/cp-kafka:4.0.0 kafka-topics --zookeeper localhost:22181 --delete --topic test_topic_name
```