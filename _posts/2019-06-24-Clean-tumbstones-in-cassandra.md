---
layout: post
title:  "Tombstones in Cassandra - Clean"
description: "Cleaning the tomb_stones in cassandra with GC_GRACE_SECONDS for the table"
categories: [ Cassandra, NoSQL, Storage ]
tags: [red, yellow]
image: assets/img/Cassandra_gc_grace_seconds.png
featured: false
hidden: true
---

Tombstones costs disk utilization and increased query time. Monitoring the amount of tomb_stones data is an important part of monitoring the health of a Cassandra cluster. We can use the SSTablemetadata command to get information on a particular table’s tombstone ratio. We can simply clear the tomb_stones data in Cassandra by altering the `GC_GRACE_SECONDS`


The number of seconds after data is marked with a tombstone (deletion marker) before it is eligible for garbage-collection. Cassandra will not execute hints or batched mutations on a tomb_stones record within its GC_GRACE_SECONDS. The default value allows a great deal of time for Cassandra to maximize consistency prior to deletion. Default value 864000 [10 days]. To learn more about [GC_GRACE_SECONDS](https://docs.datastax.com/en/archived/cql/3.1/cql/cql_reference/tabProp.html#tabProp__tab_prop_gc)

Let's understand how to decreasing GC_GRACE_SECONDS and garbage collection.
### Clean tombstones in Cassandra

- Get the GC_GRACE_SECONDS value of the table, store it in some file.

- Alter to reduce the GC_GRACE_SECONDS to 30 

    `alter table [universe_table] with GC_GRACE_SECONDS = 30;`

Wait for 30-60 seconds to cleanup the tombstones and continue to alter to the last value.

- Replace it back with actual value

`alter table [universe_table] with GC_GRACE_SECONDS = 86400;`


### In Cassandra 3.10+

This cleans up all the garbage from whole keyspace or a specific table. 

```bash
nodetool garbagecollect [jinnabalu_keyspace] [universe_table]
```


```yml
    Question: Can I force cleanup of old tombstones?
    Ans: Yes, you can clean the tomb_stones by decreasing GC_GRACE_SECONDS value to as minimum as possible. and reset back GC_GRACE_SECONDS value to the previous values, once cleaning the tomb_stones.
```