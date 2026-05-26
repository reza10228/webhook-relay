# webhook-relay
A lightweight webhook relay service for forwarding Alertmanager notifications to Zulip, Mattermost, and other messaging platforms.

This service receives webhook payloads, formats them into readable Markdown messages, and sends them to:

- Zulip streams/topics
- Mattermost incoming webhooks

using a unified formatter.

---

# Features

- Receive Alertmanager webhooks
- Support custom JSON notifications
- Support login alert notifications
- Send formatted Markdown messages
- Support Zulip
- Support Mattermost
- Retry failed HTTP requests automatically
- SSL verification toggle (`ignore_ssl=true`)
- File and console logging
- Docker & Docker Compose support
- Smart filtering for empty/invalid fields
- Multi-alert support
- Runbook & dashboard links support

---

# Supported Payload Types

## 1. Alertmanager Payload

Supports standard Prometheus Alertmanager webhook payloads.

## 2. Simple Notification Payload

```json
{
  "text": "Backup completed successfully"
}
```

## 3. Login Alert Payload

```json
{
  "status": "firing",
  "alerts": [
    {
      "labels": {
        "type": "login",
        "user": "root",
        "instance": "server01"
      },
      "annotations": {
        "text": "User root logged into server01 from 10.10.10.10"
      }
    }
  ]
}
```

---

# Project Structure

```text
.
├── app.py
├── formatter.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── logs/
```

---

# Requirements

- Docker
- Docker Compose

or

- Python 3.12+

---

# Run With Docker Compose

## Build Image

```bash
docker build -t webhook-relay .
```

## Start Service

```bash
docker compose up -d
```

## View Logs

```bash
docker compose logs -f
```

---

# Run Without Docker

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Start Application

```bash
python app.py
```

---

# API Endpoints

| Endpoint | Description |
|---|---|
| `/zulip` | Send messages to Zulip |
| `/mattermost` | Send messages to Mattermost |

---

# Zulip Example

```bash
curl -X POST "http://localhost:8686/zulip?webhook_url=https://zulip.example.com&email=bot@example.com&token=YOUR_TOKEN&to=alerts&topic=monitoring" \
-H "Content-Type: application/json" \
-d '{
  "status": "firing",
  "alerts": [
    {
      "labels": {
        "alertname": "HighCPUUsage",
        "severity": "critical",
        "instance": "server01"
      },
      "annotations": {
        "summary": "CPU usage is high"
      }
    }
  ]
}'
```

---

# Mattermost Example

```bash
curl -X POST "http://localhost:8686/mattermost?webhook_url=https://mattermost.example.com/hooks/xxxxx" \
-H "Content-Type: application/json" \
-d '{
  "status": "firing",
  "alerts": [
    {
      "labels": {
        "alertname": "HighCPUUsage",
        "severity": "critical",
        "instance": "server01"
      },
      "annotations": {
        "summary": "CPU usage is high"
      }
    }
  ]
}'
```

---
# Alertmanager Integration

This section explains how to integrate the webhook relay service with Prometheus Alertmanager for both Zulip and Mattermost.

---

# Alertmanager → Zulip

## Example `alertmanager.yml`

```yaml
receivers:
  - name: zulip-webhook
    webhook_configs:
      - url: >-
          http://webhook-relay:8686/zulip
          ?webhook_url=https://zulip.example.com
          &email=bot@example.com
          &token=YOUR_ZULIP_BOT_TOKEN
          &to=alerts
          &topic=monitoring

route:
  receiver: zulip-webhook
```

---

## Example With `ignore_ssl=true`

```yaml
receivers:
  - name: zulip-webhook
    webhook_configs:
      - url: >-
          http://webhook-relay:8686/zulip
          ?webhook_url=https://zulip.example.com
          &email=bot@example.com
          &token=YOUR_ZULIP_BOT_TOKEN
          &to=alerts
          &topic=monitoring
          &ignore_ssl=true

route:
  receiver: zulip-webhook
```

---

# Alertmanager → Mattermost

## Example `alertmanager.yml`

```yaml
receivers:
  - name: mattermost-webhook
    webhook_configs:
      - url: >-
          http://webhook-relay:8686/mattermost
          ?webhook_url=https://mattermost.example.com/hooks/xxxxxxxxxxxxxxxx

route:
  receiver: mattermost-webhook
```

---

## Example With `ignore_ssl=true`

```yaml
receivers:
  - name: mattermost-webhook
    webhook_configs:
      - url: >-
          http://webhook-relay:8686/mattermost
          ?webhook_url=https://mattermost.example.com/hooks/xxxxxxxxxxxxxxxx
          &ignore_ssl=true

route:
  receiver: mattermost-webhook
```

---

# Recommended Alertmanager Configuration

Recommended options:

```yaml
webhook_configs:
  - send_resolved: true
    max_alerts: 10
```

Example:

```yaml
receivers:
  - name: mattermost-webhook
    webhook_configs:
      - url: >-
          http://webhook-relay:8686/mattermost
          ?webhook_url=https://mattermost.example.com/hooks/xxxxxxxx
        send_resolved: true
        max_alerts: 10
```

---

# Login Alert Example

Example alert rule for login notifications:

```yaml
groups:
  - name: login-alerts
    rules:
      - alert: UserLogin
        expr: vector(1)
        labels:
          type: login
          source: script
        annotations:
          summary: "User r.shoghi logged into beta-mon-lapp1 from IP 172.24.2.55"
```

Rendered output:

```text
ℹ️ Notification

User **r.shoghi** logged into **beta-mon-lapp1** from IP **172.24.2.55**
```

---

# Network Notes

Make sure Alertmanager can access the relay service:

```text
http://webhook-relay:8686
```

depending on your environment.

---

# Health Check Example

You can test connectivity manually:

## Zulip

```bash
curl -X POST "http://webhook-relay:8686/zulip?webhook_url=https://zulip.example.com&email=bot@example.com&token=TOKEN&to=alerts" -H "Content-Type: application/json" -d '{"text":"test"}'
```

## Mattermost

```bash
curl -X POST "http://webhook-relay:8686/mattermost?webhook_url=https://mattermost.example.com/hooks/xxxxx" -H "Content-Type: application/json" -d '{"text":"test"}'
```

---


# Logging

Logs are stored in:

```text
logs/webhook.log
```

---

# SSL Verification

```text
ignore_ssl=true
```

---

# Technologies

- Python 3.12
- Flask
- Requests
- Docker
- Docker Compose

---

# Default Port

```text
8686
```
