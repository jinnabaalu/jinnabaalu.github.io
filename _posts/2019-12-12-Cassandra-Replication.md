---
categories: [ Cassandra, NoSQL, Database ]
tags: [ Cassandra ]
---


# Data Replication

Cassandra provide a backup when the problem has occurred - **no single point of failure**

Data is placed on nodes based on

**Replication Strategy**, determines where to place next replica

**Replication Factor**, determines the total number of replicas placed on different nodes. One Replication factor means that there is only a single copy of data while three replication factor means that there are three copies of the data on three different nodes.

For ensuring there is no single point of failure, **replication factor must be three**.

### Replication strategies in Cassandra

**SimpleStrategy**

SimpleStrategy is used when you have just one data center. SimpleStrategy places the first replica on the node selected by the partitioner. After that, remaining replicas are placed in clockwise direction in the Node ring.

![Replication Strategy - SimpleStrategy](https://platform-ops.tech/assets/img/replication_strategy_simple_strategy.png)

**NetworkTopologyStrategy**

NetworkTopologyStrategy is used when you have more than two data centers.

In NetworkTopologyStrategy, replicas are set for each data center separately. NetworkTopologyStrategy places replicas in the clockwise direction in the ring until reaches the first node in another rack.

This strategy tries to place replicas on different racks in the same data center. This is due to the reason that sometimes failure or problem can occur in the rack. Then replicas on other nodes can provide data.

![Replication Strategy - NetworkTopologyStrategy](./replication_strategy_network_topology_strategy.png)