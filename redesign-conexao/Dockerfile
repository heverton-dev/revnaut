FROM nginx:1.27-alpine

ARG NOINDEX=yes
RUN rm /etc/nginx/conf.d/default.conf \
 && if [ "$NOINDEX" = "yes" ]; then echo 'add_header X-Robots-Tag "noindex, nofollow" always;' > /etc/nginx/robots.conf; \
    else echo '' > /etc/nginx/robots.conf; fi

COPY nginx.conf /etc/nginx/conf.d/site.conf
COPY *.html *.css site.js /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1:8080/health || exit 1
