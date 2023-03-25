---
layout: post
title: "SSL - Create CSR, CRT, Secure Sockets Layer"
description: "SSL - Create CSR, CRT, Secure Sockets Layer"
author: jinnabalu
categories: [ Security, SSL, Godaddy ]
image: assets/images/ssl.png
featured: false
hidden: true
---

#### Step 1. Buy the SSL from the provider,

  In current docs I explain about godaddy, follow 

#### Step 2. Generate CSR

How you generate a `.csr` depends on the type of certificate you're requesting and your operating system. 

- SSH into your server
- Generate crt using openssl with following command
```bash
openssl req -new -newkey rsa:2048 -nodes -keyout example.key -out example.csr
```
- Here is the godaddy [docs](https://in.godaddy.com/help/nginx-generate-csrs-certificate-signing-requests-3601)

#### Step 3. Generate `.crt` file from the SSL Provider

Above step will generate the csr file copy that into the ssl provider and get the `.crt` file which can be used for the SSL management of the website.

#### Here is how we can generate `.crt` file
- Next go to the SSL management section of your GoDaddy account and click "Manage" next to the certificate you want to use.  Click on the "Re-Key" and cut and paste the results of the CSR above into the re-key request. Finish the process completely.

- Steps for godaddy SSL certificate configuration [here](https://in.godaddy.com/help/generate-a-csr-certificate-signing-request-5343)

- After generating the `.crt` file, you will download a zipfile contrains the

#### Step 4. Concatenate the intermediate and bundle .crt files to generate 

A common practice, then, is to bundle these all up into one file -- your certificate, then the signing certificates. But since they aren't easily distinguished, it sometimes happens that someone accidentally puts them in the other order -- signing certs, then the final cert -- without noticing. In that case, your cert will not match your key.

```bash
cat certificate.crt ca_bundle.crt > bundle_chained.crt
```

Here is the related issues with `X509_check_private_key:key values mismatch`, [stackoverflow answer](https://stackoverflow.com/questions/26191463/ssl-error0b080074x509-certificate-routinesx509-check-private-keykey-values)

Here is the example for nginx ssl certificate conf

```bash
server {
    listen              443 ssl;
    server_name         www.example.com;
    ssl_certificate     bundle_chained.crt;
    ssl_certificate_key example.key;
    ...
}
```

