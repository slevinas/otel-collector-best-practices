# OpenTelemetry Collector – TLS/mTLS Best Practices & Example

---

## Overview

This repo demonstrates **secure OpenTelemetry data collection** using TLS/mTLS and shows how to tag telemetry for organization-wide observability. It’s designed for XPLG developers deploying the OTel Collector in Docker (or K8s) with instrumented services using the Python SDK.

---

## Table of Contents

- [Why Use TLS/mTLS?](#why-use-tlsmtls)
- [Best Practices Table](#best-practices-table)
- [Certificate Lifecycle & File Layout](#certificate-lifecycle--file-layout)
- [Collector Configuration (TLS/mTLS)](#collector-configuration-tlsmtls)
- [Docker Compose Example](#docker-compose-example)
- [Enriching Metrics (Transform/Attributes)](#enriching-metrics-transformattributes)
- [Testing TLS/mTLS Connectivity](#testing-tlsmtls-connectivity)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)

---

## Why Use TLS/mTLS?

- **TLS** encrypts telemetry in transit, preventing data leaks, tampering, and impersonation.
- **mTLS** (mutual TLS) ensures _both_ client and collector verify each other’s identity, blocking rogue senders.

---

## Best Practices Table

| Category          | Recommendation                                                      |
| ----------------- | ------------------------------------------------------------------- |
| TLS Everywhere    | Use TLS for all receivers/exporters (gRPC, HTTP, etc.)              |
| Use mTLS          | Enforce client cert verification for mutual trust                   |
| Cert Rotation     | Automate cert issuance/renewal with Vault or cert-manager           |
| File Permissions  | Use `600` for key files; never world-readable                       |
| Secure File Paths | Mount secrets/keys via Docker/K8s volumes (never bake into image)   |
| Network Isolation | Expose only needed ports; use firewalls, mesh, or K8s networkpol    |
| CN/SAN Validity   | Server certs must match collector’s hostname/IP _as used by client_ |
| TLS Version       | Use TLS 1.2+ only (disable legacy protocols)                        |

---

#### Certificate Lifecycle & File Layout

**Certs needed:**

- CA cert/key (one per cluster/env)
- Server cert/key (for Collector; CN/SAN matches container/service name or load-balancer hostname)
- Client cert/key (for instrumented apps; signed by the same CA)

**Directory (Docker/K8s):**

```
/etc/otel/certs/
├── ca.crt
├── server.crt
├── server.key
├── client.crt
├── client.key
```

- Set file permissions before mounting:

```bash
chmod 600 server.key client.key
chmod 644 ca.crt server.crt client.crt

Tip: For dev, SAN should include both otel-collector (container DNS) and localhost.
```

---

#### Collector Configuration (TLS/mTLS)

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        tls:
          cert_file: /etc/otel/certs/server.crt
          key_file: /etc/otel/certs/server.key
          client_ca_file: /etc/otel/certs/ca.crt # enables mTLS
      http:
        endpoint: 0.0.0.0:4318
        tls:
          cert_file: /etc/otel/certs/server.crt
          key_file: /etc/otel/certs/server.key
          client_ca_file: /etc/otel/certs/ca.crt # enables mTLS

processors:
  batch:
    timeout: 5s
    send_batch_size: 1024
  attributes/add_client_tag:
    actions:
      - key: org_name
        value: XPLG
        action: insert
  transform/tag_metrics:
    metric_statements:
      - context: datapoint
        statements:
          - set(datapoint.attributes["client_id"], resource.attributes["service.name"])

exporters:
  file/tagged_metrics:
    path: /otel-logs/tagged_metrics.json

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch, attributes/add_client_tag, transform/tag_metrics]
      exporters: [file/tagged_metrics]
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [file/tagged_metrics]
```

- **Note:**

- client_ca_file enables and enforces mTLS for both HTTP and gRPC.

- file/tagged_metrics writes metrics to local disk for inspection.

---

### Docker Compose Example

```yaml
version: "3.9"
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    container_name: otel-collector
    command: ["--config=/etc/otel/config.yaml"]
    ports:
      - "4317:4317" # gRPC
      - "4318:4318" # HTTP
    volumes:
      - ./collector/otel-collector-config.yaml:/etc/otel/config.yaml:ro
      - ./collector/logs:/otel-logs:rw
      - ./certs:/etc/otel/certs:ro
    restart: unless-stopped
```

---

### Enriching Metrics (Transform/Attributes)

##### Static attribute:

- **Add org_name with the attributes processor (for all metrics):**

```yaml
processors:
  attributes/add_client_tag:
    actions:
      - key: org_name
        value: XPLG
        action: insert
```

#### Dynamic tag:

- **Copy resource attr to each datapoint with the transform processor:**

```yaml
processors:
  transform/tag_metrics:
    metric_statements:
      - context: datapoint
        statements:
          - set(datapoint.attributes["client_id"], resource.attributes["service.name"])
```

---

### Testing TLS/mTLS Connectivity

#### Manual test with curl:

```bash

curl -v https://localhost:4318/v1/metrics \
  --cert certs/client.crt \
  --key certs/client.key \
  --cacert certs/ca.crt \
  -H "Content-Type: application/json" \
  --data-binary @test-metric.json
```

- Fails if missing any cert or if CN/SAN mismatch.

- Collector logs show handshake errors if TLS config is wrong.

---

### Troubleshooting

Symptom Diagnosis Solution

“Client sent an HTTP request to an HTTPS…” Mismatch between endpoint protocol and config Use correct https/http
“TLS handshake failed” Wrong cert, CN/SAN, or CA on either side Recheck certs
“connection refused” Wrong port, IP, or container not running Check docker-compose
“no data in exporter” Pipeline or file path misconfigured Check config/logs

---

#### Critical checks:

- Always test handshake with curl/openssl before real workloads.

- File permissions on .key must be 600.

- SANs must match actual connection hostname (prod & dev).

- Practice cert renewal before certs expire.

---

### Further Reading

[OpenTelemetry Collector TLS/mTLS Authentication (official docs)](https://opentelemetry.io/docs/collector/configuration/#authentication)

[OpenTelemetry Python SDK: OTLP Exporter](https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html)

[Collector Processors: transform](https://github.com/open-telemetry/opentelemetry-collector/tree/main/processor)

## OpenTelemetry Security Best Practices (blog) --> [Hardening the Collector Episode 1: A new default bind address](https://opentelemetry.io/blog/2024/hardening-the-collector-one/)

### FAQ

**Q**: Should we use OIDC/JWT in addition to mTLS?

**A**: For internal/sidecar Collector deployments, mTLS is usually sufficient and simpler. For multi-tenant/Internet-facing endpoints, consider auth extensions as a next step.

**Q**: How should I generate the certs?

**A**: See /docs/GEN-CERTS.md or use Vault/cert-manager in prod. Key is to ensure SANs match what clients actually use.

---

## Live Example

See [this demo branch](https://github.com/slevinas/otel-collector-mtls-demo/blob/main/README.md#2-clone--setup) for a runnable project using the configs and best practices described here.

---

**Maintained by the Observability/QA team – see /docs/ for more in-depth scenarios and config examples.**

---
