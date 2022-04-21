FROM nginx:mainline-alpine

RUN rm -rf /etc/nginx/conf.d
COPY deploy/nginx/app.conf /etc/nginx/conf.d/default.conf
COPY deploy/nginx/options-ssl-nginx.conf /etc/nginx/conf.d/options-ssl-nginx.conf