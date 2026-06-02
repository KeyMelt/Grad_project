#!/bin/sh
set -eu

domain="${RL_IDE_TLS_DOMAIN:-}"
cert_dir="/etc/letsencrypt/live/${domain}"

if [ -n "${domain}" ] \
  && [ -f "${cert_dir}/fullchain.pem" ] \
  && [ -f "${cert_dir}/privkey.pem" ]; then
  sed "s|/etc/letsencrypt/live/DOMAIN|${cert_dir}|g" \
    /etc/nginx/default-ssl.conf > /etc/nginx/conf.d/default.conf
else
  cp /etc/nginx/default-http.conf /etc/nginx/conf.d/default.conf
fi
