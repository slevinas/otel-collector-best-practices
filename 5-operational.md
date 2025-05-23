# OTel Collector Best Practices (with mTLS & Tagging)

**This repo demonstrates production-grade OpenTelemetry Collector configuration for secure, robust, and extensible telemetry pipelines at XPLG.**

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Security (TLS/mTLS)](#security-tlsmtls)
- [Tagging/Attribute Processors](#taggingattribute-processors)
- [Collector Configuration Examples](#collector-configuration-examples)
- [Testing & Validation](#testing--validation)
- [Operational Hardening](#operational-hardening)
- [References](#references)

---

## Overview

This project shows:

- How to configure the OTel Collector with **TLS and mTLS** for encrypted, authenticated telemetry transport.
- How to add custom tags/attributes to incoming metrics using the Collector’s processor pipeline.
- How to test your configuration end-to-end using `curl` and sample metrics.
- Best practices for running the Collector securely in a Docker environment.

## Architecture

+-------------+ (TLS/mTLS) +---------------------+
| API Service |-------------------> | OTel Collector |
| (admin-api) | OTLP/gRPC+HTTP | [processors] |
+-------------+ +---------------------+
|
v
+----------------------+
| Exporters: |
| - File/JSON |
| - Debug |
+----------------------+

```pgsql


- All connections to the collector are **encrypted** and **client-authenticated**.
- Tagging and transformation processors add business-relevant context.
```

## Security (TLS/mTLS)

- Enforces **server-side TLS** (all clients must trust the collector).
- Optionally enforces **mutual TLS (mTLS)** (collector only accepts telemetry from clients with valid certs).
- [Cert generation and full config instructions in `/certs`](./certs/).

### Certificate Generation (Quick Start)

```bash
# From project root
cd certs
# 1. Generate Root CA
openssl genrsa -out ca.key 4096
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/CN=MyRootCA"
# 2. Generate Server Cert/Key (SAN: otel-collector, localhost)
# 3. Generate Client Cert/Key (CN: client, optional SAN)
# (See README or scripts in /certs for step-by-step)
```

Collector Config (mTLS Example)

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
        tls:
          cert_file: /etc/otel/certs/server.crt
          key_file: /etc/otel/certs/server.key
          client_ca_file: /etc/otel/certs/ca.crt # enables mTLS
      grpc:
        endpoint: 0.0.0.0:4317
        tls:
          cert_file: /etc/otel/certs/server.crt
          key_file: /etc/otel/certs/server.key
          client_ca_file: /etc/otel/certs/ca.crt
```

### Tagging/Attribute Processors

Add static or dynamic attributes to telemetry (useful for multi-tenant, environment tagging, or audit context).

```yaml
processors:
  attributes/add_org_name:
    actions:
      - key: org_name
        value: XPLG
        action: insert
  transform/tag_client_id:
    metric_statements:
      - context: datapoint
        statements:
          - set(datapoint.attributes["client_id"], resource.attributes["service.name"])
```

### Collector Configuration Examples

See [collector/otel-collector-mtls.yaml]()

See [collector/otel-collector-tagging.yaml]()

### Testing & Validation

#### Start Collector

```bash

docker-compose up -d
```

- Submit a Test Metric (with mTLS)

```bash

curl -X POST https://localhost:4318/v1/metrics \
  --cert certs/client.crt \
  --key certs/client.key \
  --cacert certs/ca.crt \
  -H "Content-Type: application/json" \
  --data-binary @testdata/test-metric.json

```

#### Inspect Output

- Output written to collector/logs/tagged_metrics.json

- Use jq to validate tags and structure

#### Sample Metric (testdata/test-metric.json)

```json
{
  "resource_metrics": [
    {
      "resource": { "attributes": { "service.name": "admin-api" } },
      "scope_metrics": [ ... ]
    }
  ]
}


```

### Operational Hardening

- Run as non-root

- Minimal capabilities

- Monitor Collector health

- Use separate pipelines for internal/3rd-party telemetry as needed

### References

[OpenTelemetry Collector Docs](https://opentelemetry.io/docs/collector/)

[OTel Collector Security Configuration Best Practices](https://opentelemetry.io/docs/security/config-best-practices/)

[OTel Collector Configuration](https://opentelemetry.io/docs/collector/configuration/)

Maintained by the XPLG ODD Platform Engineering Team.

---
