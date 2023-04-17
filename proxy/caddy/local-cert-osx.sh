#!/bin/sh

mkcert -install
mkdir -p certs
mkcert -cert-file certs/local.cert.pem -key-file certs/local.key.pem es-connector.local
