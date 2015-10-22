# Roles

---

该目录用于保存 Roles


+ common

```
该role用于 初始化整个 MariaDB Galera Cluster 环境，
主要是做一些 每个集群节点都需要做的通用操作
```

+ galera

```
整个galera集群没有主从概念，整体的被看做一个副本集，所有节点 关系对等。
该role用于 执行安装 MariaDB Galera Cluster
主要是做 集群安装、集群配置、集群启动 等操作


---
