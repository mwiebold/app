FROM php:8.5-apache

RUN docker-php-ext-install mysqli
COPY apache.conf /etc/apache2/conf-enabled/beestat-dev.conf
WORKDIR /var/www/html
