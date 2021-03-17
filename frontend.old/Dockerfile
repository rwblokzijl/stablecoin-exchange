FROM nginxinc/nginx-unprivileged:1-alpine

COPY ./default.conf /etc/nginx/conf.d/default.conf

USER root

RUN mkdir -p /vol/static
COPY ./dist /vol/static
RUN chmod -R 755 /vol/static

USER nginx

