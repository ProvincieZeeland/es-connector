#
# BUILDER
#
FROM nginx:1.23.3-alpine

ARG NGINX_VERSION=1.23.3
ARG HEADERS_MORE_VERSION=v0.34

RUN apk --update --no-cache add \
        gcc \
        make \
        libc-dev \
        g++ \
        openssl-dev \
        linux-headers \
        pcre-dev \
        zlib-dev \
        libtool \
        automake \
        autoconf \
        git

RUN cd /opt \
    && git clone --depth 1 -b $HEADERS_MORE_VERSION --single-branch https://github.com/openresty/headers-more-nginx-module.git \
    && cd /opt/headers-more-nginx-module \
    && git submodule update --init \
    && cd /opt \
    && wget -O - http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz | tar zxfv - \
    && mv /opt/nginx-$NGINX_VERSION /opt/nginx \
    && cd /opt/nginx \
    && ./configure --with-compat --add-dynamic-module=/opt/headers-more-nginx-module \
    && make modules 

#
# FINAL
#
FROM nginx:1.23.3-alpine

RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir /etc/nginx/nginxconfig.io
RUN mkdir /etc/nginx/sites-enabled/

COPY nginx.conf /etc/nginx/
COPY certs-enabled/* /etc/ssl/
COPY nginxconfig.io/* /etc/nginx/nginxconfig.io/
COPY sites-enabled/* /etc/nginx/sites-enabled/

COPY --from=0 /opt/nginx/objs/ngx_http_headers_more_filter_module.so /usr/lib/nginx/modules
RUN chmod -R 644 /usr/lib/nginx/modules/ngx_http_headers_more_filter_module.so \
    && sed -i '1iload_module \/usr\/lib\/nginx\/modules\/ngx_http_headers_more_filter_module.so;' /etc/nginx/nginx.conf 

# Set ownerships
RUN chown -R nginx:nginx /etc/nginx/ && chown -R nginx:nginx /etc/ssl/ && chown -R nginx:nginx /var/cache/nginx && chown -R nginx:nginx /var/log/nginx
RUN touch /var/run/nginx.pid && chown -R nginx:nginx /var/run/nginx.pid

# Change user
USER nginx

