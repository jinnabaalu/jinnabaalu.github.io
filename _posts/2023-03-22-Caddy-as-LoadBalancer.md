---
layout: blog
title: "Caddy as Load Balancer and Reverse Proxy with Docker Compose"
description: "Run Caddy as a load balancer and reverse proxy using Docker Compose — with SSL, logging, redirects, and multi-site configurations."
categories: [ Caddy, LoadBalancer, Docker, ReverseProxy ]
tags: [ Caddy, Load Balancer, Reverse Proxy, Docker, SSL ]
image: ""
githublink: "https://github.com/jinnabaalu/caddy-operations"
---

## Why Caddy?

Caddy is a production-ready web server with **automatic HTTPS**, built-in reverse proxy, and load balancing — all configured through a simple `Caddyfile`. No Nginx conf files, no certbot crons, no manual SSL renewal.

This post covers the Caddy use cases I have tested and run in production, all available in the [caddy-operations](https://github.com/jinnabaalu/caddy-operations) repository.

## Use Cases

1. [Load Balancer](#1-load-balancer)
2. [Reverse Proxy](#2-reverse-proxy)
3. [SSL Configuration](#3-ssl-configuration)
4. [HTTP to HTTPS Redirects](#4-http-to-https-redirects)
5. [Disabling SSL for Specific Domains](#5-disabling-ssl-for-specific-domains)
6. [Logging (Global + Per-Route)](#6-logging-global--per-route)
7. [Remove Server Response Header](#7-remove-server-response-header)
8. [Serve Multiple Static Sites](#8-serve-multiple-static-sites)
9. [Graceful Reload](#9-graceful-reload)

---

## 1. Load Balancer

Distribute traffic across multiple backend servers with a single `Caddyfile` directive.

**Caddyfile**

```bash
:80 {
	reverse_proxy 192.168.0.28:8001  192.168.0.27:8001  192.168.0.26:8001
}
```

**docker-compose.yml**

```yaml
version: "3"
services:
  caddy:
    restart: always
    image: caddy:2.4.6
    container_name: caddy
    ports:
      - "80:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
```

Caddy round-robins across the three backends. If a backend is down, Caddy automatically retries the next one.

---

## 2. Reverse Proxy

Route different ports to different backends.

**Caddyfile**

```bash
:80 {
	reverse_proxy 192.168.0.28:8001
}

:8080 {
	reverse_proxy 192.168.0.28:8002
}
```

**docker-compose.yml**

```yaml
version: "3"
services:
  caddy:
    restart: always
    image: caddy:2.4.6
    container_name: caddy
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
```

---

## 3. SSL Configuration

Caddy handles SSL automatically — just add a `tls` directive with your email.

**Default (Auto) SSL**

```bash
vibhuvi.com {
  tls hello@vibhuvi.com
  reverse_proxy localhost:2022
}
```

Caddy issues certificates via ACME, redirects HTTP→HTTPS, and renews automatically. Test with [SSL Labs](https://www.ssllabs.com/ssltest).

**Custom SSL (bring your own cert)**

```bash
https://xyz.example {
    tls /ssl/certs/fullchain.pem /ssl/certs/key.pem
}

https://api.xyz.example {
    tls /ssl/certs/fullchain.pem /ssl/certs/key.pem
}

http://xyz.example, http://api.xyz.example {
    redir https://{host}{uri}
}
```

---

## 4. HTTP to HTTPS Redirects

**Automatic (just use a domain name)**

```bash
example.com {
    # Caddy auto-redirects HTTP to HTTPS
}
```

**Manual redirect with subdomains**

```bash
www.example.com {
  redir https://example.com{uri} permanent
}

http://www.example.com {
  redir https://example.com{uri} permanent
}
```

**Redirect all domains/IPs to one domain**

```bash
http://, https:// {
    redir https://example.com{uri}
}
```

---

## 5. Disabling SSL for Specific Domains

Prefix with `http://` or use port `:80` to force HTTP-only.

```bash
pipeline.example.com {
    reverse_proxy 192.2.2.2:9000
}

# HTTP-only
http://app.example.com {
    reverse_proxy app:80
}

# Port-based
staging.example.com:80 {
    reverse_proxy app:80
}
```

---

## 6. Logging (Global + Per-Route)

```bash
:8080 {
    log {
        level  ERROR
        output file /var/log/error.log {
            roll_size   1gb
            roll_keep   5
            roll_keep_for 72h
        }
        format filter {
            wrap console
            fields {
                request>headers>Authorization delete
            }
        }
    }
    handle /api* {
        log {
            level  INFO
            output file /var/log/api-access.log {
                roll_size 10mb
                roll_keep 20
                roll_keep_for 72h
            }
        }
        reverse_proxy localhost:7022
    }
    handle {
        log {
            level  INFO
            output file /var/log/srv-access.log {
                roll_size 10mb
                roll_keep 20
                roll_keep_for 72h
            }
        }
        root * /srv
        file_server browse
    }
}
```

- Global error logs → `/var/log/error.log`
- API access logs → `/var/log/api-access.log`
- Default route logs → `/var/log/srv-access.log`
- Sensitive headers (Authorization) are stripped from logs.

---

## 7. Remove Server Response Header

Hide `Server: Caddy` from response headers for security.

```bash
(common) {
    header /* {
        -Server
    }
}

example.com {
    reverse_proxy localhost:3000
    import common
}
```

---

## 8. Serve Multiple Static Sites

```bash
:9001 {
    root * /var/www/app-one
    file_server
}
:9002 {
    root * /var/www/app-two
    file_server
}
```

**docker-compose.yml**

```yaml
version: "3"
services:
  caddy:
    restart: always
    image: caddy:latest
    container_name: caddy
    ports:
      - "80:80"
      - "443:443"
      - 9001:9001
      - 9002:9002
    volumes:
      - ./app-one:/var/www/app-one
      - ./app-two:/var/www/app-two
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
volumes:
  caddy_data:
  caddy_config:
```

---

## 9. Graceful Reload

Reload the Caddyfile without downtime:

```bash
caddy_container_id=$(docker ps | grep caddy | awk '{print $1;}')
docker exec $caddy_container_id -w /etc/caddy caddy reload
```

---

## Source

All configurations and examples are available in the [caddy-operations](https://github.com/jinnabaalu/caddy-operations) repository.
