---
layout: post
title:  "Steps to install a Go Daddy SSL Certificate with NGINX"
author: jinna
categories: [ Devops ]
---

### Step1: Generate a CSR and Private Key

Before purchasing the certificate we have to generate the CSR(Certificate Signing Request) and key files. You can generate `CSR` and `.key` with `openssl`. Here is the example commad with sample domain. 

```bash
openssl req -newkey rsa:2048 -nodes -keyout [KEY_FILE_NAME].key -out [CSR_FILE_NAME].csr
```

`KEY_FILE_NAME`, this is a private key file used in nginx configuration.

`CSR_FILE_NAME`, CSR file used for generating the crt file from Godaddy.

#### Following is the example of the `platform-ops.key` and `platform-ops.csr`

```bash
openssl req -newkey rsa:2048 -nodes -keyout platform-ops.key -out platform-ops.csr
```

> `platform-ops.key` - KEY_FILE_NAME

> `platform-ops.csr` - CSR_FILE_NAME

- Here is the terminal sample output

```bash
balu@master-node:~/work/Courses/platformops.github.io$ openssl req -newkey rsa:2048 -nodes -keyout platform-ops.key -out platform-ops.csr
Generating a 2048 bit RSA private key
.........+++
.............................................................................................................................................+++
writing new private key to 'platform-ops.key'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:IN
State or Province Name (full name) [Some-State]:Telangana
Locality Name (eg, city) []:Medak
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Platform Ops
Organizational Unit Name (eg, section) []:Medak
Common Name (e.g. server FQDN or YOUR name) []:Jinna Balu
Email Address []:jinna.balu@platform-ops.com

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:Platform Ops 
```

- This will generate two files, `platform-ops.key` and `platform-ops.csr`. you can copy the `.csr` file content to request for the SSL Certificate. To view the content of the `platform-ops.csr` use the following command.

Now you can purchase your certificate. You will need to copy and paste your `platform-ops.csr` certificate to send your request for a SSL Certificate. Use this command to print your file:

```bash
cat platform-ops.csr
```
### Steps 2: Get an SSL certificate

Buy SSL and show visitors you’re trustworthy and authentic. Godaddy provides the ssl certificate with the following types.

- Protect one website
- Protect multiple websites
- Protect all sub domains

Go for something that best suits your needs purchase the certificate. This tutorial is based on the first one but I’m sure you can use it for all of them. Clear steps defined for purchasing and activating the ssl in [SSL Certificates Help](https://in.godaddy.com/help/ssl-certificates-1000006) godaddy official docs.

### Step 3: Request an SSL certificate and download 

GoDaddy now verifies that you control the domain. You will receive an email as soon as your SSL certificate will be issued with a link to download it. Open that link.

Select Apache from the Server type dropdown menu and download the ZIP archive. It should contain two .crt files:

Your SSL Certificate with a random name (Ex. `93rfs8dhf834hts.crt`)
The GoDaddy intermediate certificate bundle (Ex. `gd_bundle-g2-g1.crt`)

The certificate is now ready to be installed on your `NGINX`

#### Generate single chained certificate

With Nginx, if your Certificate Authority (CA) included an intermediate certificate, you must create a single chained certificate file that contains your certificate and the CA’s intermediate certificates.

##### Certificates

Ones you have generated, downloaded and extracted the certificate zip, you will find 2 files in it:
  - `gd_bundle-g2-g1.crt` Intermediate Certificate
  - `RANDOM_NUM.crt` Your SSL Certificate

##### Creating single chained certificate

Create a single "chained" certificate file that contains your certificate and the CA's intermediate certificates.

```bash
cat <RANDAM_NAME_SSL CERTIFICAT>.crt <GD_BUNDLE_OR_SSL_CERTIFICATE>.crt > <NEW_FILE_NAME>.crt

# Example

cat 93rfs8dhf834hts.crt gd_bundle-g2-g1.crt > platform-ops.crt
```

##### OPTIONAL

You can validate your certificates using your key file.

  - Check a certificate and return information about it(Signing authority, expiration date, etc.)
    
    `openssl x509 -in server.crt -text -noout`
    
  - Check the SSL key and verify the consistency.
    
    `openssl rsa -in server.key -check`
    
  - Verify the CSR and print CSR data filled in when generating the CSR.
    
    `openssl req -text -noout -verify -in server.csr`
    
  - The following two commands will print out md5 sums of the certificate and key. These sums can be compared to verify that the certificate and key match.
    
    `openssl x509 -noout -modulus -in server.crt| openssl md5`
    
    `openssl rsa -noout -modulus -in server.key| openssl md5

### Step 4: Run NGINX with SSL

- Create a isolated directory for runing the nginx to do run the following 

```bash
mkdir nginx-configuration/

cd nginx-configuration/

```
- - Generate the basic `.conf` for ssl configuration

```bash
cat <<\EOF >> nginx.conf
user root;

events {
    worker_connections  1024;
}

http {
    include            mime.types;
    .........
    ..........
    server {
      listen 80;
      server_name platform-ops.tech;
      return 301 https://$host$request_uri;

      access_log off;
      error_log  /var/log/nginx/error.log error;
    }

    server {
        listen 443 ssl;
        server_name platform-ops.tech;
        root /usr/share/nginx/html;
        ssl_certificate    /etc/nginx/ssl/platform-ops.crt;
        ssl_certificate_key    /etc/nginx/ssl/ platform-ops.key;
        ......
        ......
        location / {
            .....
            ...
        }
    }
}

```

- Generate the docker-compose files for nginx

```bash
cd nginx-configuration/


cat <<\EOF >> docker-compose.yml
version: '3'
services:
  proxy:
    image: nginx:latest
    container_name: nginx_proxy
    volumes:
      - "./nginx.conf:/etc/nginx/nginx.conf:ro"
      - "./certs:/etc/nginx/ssl:ro"
      - "./html:/usr/share/nginx/html:ro"
      - "$PWD/logs/nginx:/var/log/nginx"
    restart: always
    ports:
      - "80:80"
      - "443:443"
EOF
```

- Run nginx docker container

```bash
docker-compose up -d
```




