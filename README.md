# Google-cloud-data-eng

Collect and stream data to ksql db and notify user on Telegram. Google Cloud, YouTube API, python, Control Center, Schema Registry, KStrams App, ksqlDB, REST Proxy, Sink connector, Confluent Server, ZooKeeper, Telegram, Docker.

## Requirements

- Python 3.11
- Kafka
- Docker
- Confluent Containers (Zookeeper, Kafka, Schema Registry, Connect, ksqlDB, Control Center)
- Google Cloud YouTube playlist API
- Confluent Kafka cluster
- ksql datbase
- Telegram BOT API

# Docker Compose Configuration Overview

This Docker Compose file sets up a multi-container environment for running Apache Kafka and related services using Confluent Platform version 7.4.0.

## Services

### Zookeeper

- **Image**: confluentinc/cp-zookeeper:7.4.0
- **Purpose**: Manages coordination and metadata for Kafka brokers.
- **Ports Exposed**: 2181 (for client connections)
- **Health Check**: Checks if Zookeeper is healthy by sending the command `ruok` to port 2181.
- **Environment Variables**:
  - `ZOOKEEPER_CLIENT_PORT`: Set to 2181.
  - `ZOOKEEPER_TICK_TIME`: Set to 2000.

### Broker

- **Image**: confluentinc/cp-server:7.4.0
- **Purpose**: Apache Kafka broker.
- **Ports Exposed**:
  - 9092 (for client connections)
  - 9101 (for JMX monitoring)
- **Health Check**: Checks if the Kafka broker is healthy by attempting to establish a connection to port 9092.
- **Environment Variables**:
  - Various Kafka configuration properties: broker ID, advertised listeners, etc.
  - JMX configuration for monitoring.

### Schema Registry

- **Image**: confluentinc/cp-schema-registry:7.4.0
- **Purpose**: Centralized schema management for Kafka topics.
- **Ports Exposed**: 8081 (for REST API)
- **Health Check**: Checks if the Schema Registry is healthy by sending a request to `http://localhost:8081/`.
- **Environment Variables**:
  - `SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS`: Set to 'broker:29092'.

### Control Center

- **Image**: confluentinc/cp-enterprise-control-center:7.4.0
- **Purpose**: Provides monitoring and management capabilities for Kafka clusters.
- **Ports Exposed**: 9021 (for web interface)
- **Health Check**: Checks if Control Center is healthy by sending a request to `http://localhost:9021/health`.
- **Environment Variables**:
  - Configuration properties for connecting to Kafka, Schema Registry, and other services.

### Kafka Connect

- **Image**: cnfldemos/cp-server-connect-datagen:0.6.0-7.3.0
- **Purpose**: Kafka Connect service for integrating Kafka with external systems.
- **Ports Exposed**: 8083 (for REST API)
- **Health Check**: Checks if Kafka Connect is healthy by sending a request to `http://localhost:8083/`.
- **Environment Variables**:
  - Configuration for connecting to Kafka, Schema Registry, etc.

### ksqlDB Server

- **Image**: confluentinc/cp-ksqldb-server:7.4.0
- **Purpose**: Provides a streaming SQL engine for Kafka.
- **Ports Exposed**: 8088 (for REST API)
- **Health Check**: Checks if ksqlDB Server is healthy by sending a request to `http://localhost:8088/healthcheck`.
- **Environment Variables**:
  - Configuration for connecting to Kafka, Schema Registry, etc.

## Networks

- **Name**: confluent
- **Purpose**: Defines a custom Docker network for connecting the containers.

## TG Bot

Create bot in telegram and get its API_KEY

Use endpoint https://api.telegram.org/YOUR_BOT_API_KEY/getUpdates

## Set up

run `pip install -r requirements.txt`

set up variables in config.local

run `docker compose up`

run `python YoutubeAnalytics.py`

## Control Center

- localhost:9092

## Control Center > ksqlDB

```
CREATE STREAM telegram_output_stream (
  `chat_id` VARCHAR,
  `text` VARCHAR
) WITH (
  KAFKA_TOPIC = 'telegram_output_stream',
  PARTITIONS = 1,
  VALUE_FORMAT = 'avro'
);
```

- Connect
- connect-default
- Add connector
- HttpSinkConnector

```
{
  "name": "Telegram_Box_Sink",
  "config": {
    "name": "Telegram_Box_Sink",
    "connector.class": "io.confluent.connect.http.HttpSinkConnector",
    "topics": "telegram_output_stream",
    "errors.deadletterqueue.topic.replication.factor": "1",
    "http.api.url": "https://api.telegram.org/YOUR_BOTS_API_KEY/sendMessage",
    "request.method": "post",
    "headers": "Content-Type: application/json",
    "request.body.format": "json",
    "batch.json.as.array": "false",
    "batch.max.size": "1",
    "reporter.result.topic.replication.factor": "1",
    "reporter.error.topic.replication.factor": "1",
    "reporter.bootstrap.servers": "broker:29092"
  }
}
```

## ksqlDB

```
CREATE STREAM youtube_videos1 (
video_id VARCHAR KEY,
title VARCHAR,
likes INTEGER,
comments INTEGER,
views INTEGER,
favorites INTEGER,
thumbnail VARCHAR
) WITH (
KAFKA_TOPIC = 'youtube_videos',
PARTITIONS = 1,
VALUE_FORMAT = 'json'
);
```

```
CREATE TABLE youtube_analytics_changes1 WITH(KAFKA_TOPIC='youtube_analytics_changes') AS
SELECT
video_id,
latest_by_offset(title) AS title,
latest_by_offset(comments, 2)[1] AS comments_prev,
latest_by_offset(comments, 2)[2] AS comments_curr,
latest_by_offset(likes, 2)[1] AS likes_prev,
latest_by_offset(likes, 2)[2] AS likes_curr,
latest_by_offset(views, 2)[1] AS views_prev,
latest_by_offset(views, 2)[2] AS views_curr,
latest_by_offset(favorites, 2)[1] AS favorites_prev,
latest_by_offset(favorites, 2)[2] AS favorites_curr
FROM
youtube_videos1
GROUP BY
video_id;
```

```
SELECT \* FROM youtube_analytics_changes1 EMIT CHANGES;
```

```
CREATE STREAM youtube_changes_stream (TITLE VARCHAR, COMMENTS_PREV INT, COMMENTS_CURR INT, LIKES_PREV INT, LIKES_CURR INT, VIEWS_PREV INT, VIEWS_CURR INT, FAVORITES_PREV INT, FAVORITES_CURR INT)
WITH (KAFKA_TOPIC='youtube_analytics_changes', VALUE_FORMAT='json');
```

```
INSERT INTO telegram_output_stream
SELECT
'7168186738' as `chat_id`,
CONCAT('Likes changed for *****: ',
title,
' ***** From: ',
cast(likes_prev AS STRING),
' To: ',
cast(likes_curr AS STRING)) AS `text`
FROM YOUTUBE_CHANGES_STREAM
WHERE LIKES_CURR <> LIKES_PREV;
```

![likes](/img/likes.PNG)

![bot](/img/bot.PNG)

Now after you run `python YouTubeAnalytics.py` you get message to Telegram regarding the likes at the playlist.

![liked](/img/liked.PNG)

![bot](/img/bot1.PNG)
