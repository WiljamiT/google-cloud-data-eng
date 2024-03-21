python 3.12 doesnt work with kafka. using python 3.11


# google-cloud-data-eng

https://developers.google.com/youtube/v3/docs

https://developers.google.com/youtube/v3/docs#PlaylistItems


# ksqlDB in CC
```
CREATE STREAM youtube_videos (
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
SELECT * FROM youtube_videos; 
```

``` SELECT
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
    youtube_videos
GROUP BY
    video_id
EMIT CHANGES;
```

```
CREATE TABLE youtube_analytics_changes WITH(KAFKA_TOPIC='youtube_analytics_changes') AS
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
    youtube_videos
GROUP BY
    video_id
EMIT CHANGES;

```

```
SELECT * FROM youtube_analytics_changes
WHERE likes_prev <> likes_curr
EMIT CHANGES;
```

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

## Kafka TG Bot
https://api.telegram.org/bot7101823978:AAGtHY3Jm2UjF8tCOfUrbTz5o_8aZVOmJPo/getUpdates

CC, add connector 

https://www.confluent.io/hub/confluentinc/kafka-connect-http

docker compose 121

CREATE STREAM telegram_output_stream (
  `chat_id` varchar,
  `text` varchar
  ) WITH (KAFKA_TOPIC='telegram_output_stream', PARTITIONS=1, VALUE_FORMAT='avro');

## add connector select topic
  ## telegram_output_stream
  ### Dead Letter Que...
    - 1
  ### HTTP URL
    - api/bot/url
  ### req method
    - POST
  ### headers
    - Content-Type: application/json
  ### Req Body Format
    - json
  ### Json as arrays
    - false
  ### Max batch size
    - 1
  ### Result (And Error) topic replication factor
    - 1
  ### Reported bootstrap servers
    - broker:29092
  ```
{
  "name": "Telegram_Box_Sink",
  "config": {
    "name": "Telegram_Box_Sink",
    "connector.class": "io.confluent.connect.http.HttpSinkConnector",
    "topics": "telegram_output_stream",
    "errors.deadletterqueue.topic.replication.factor": "1",
    "http.api.url": "https://api.telegram.org/bot7101823978:AAGtHY3Jm2UjF8tCOfUrbTz5o_8aZVOmJPo/sendMessages",
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


