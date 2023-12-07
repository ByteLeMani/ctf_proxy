FROM nginx:latest

COPY ./nginxreloader.sh /nginxreloader.sh
RUN chmod +x /nginxreloader.sh

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

RUN apt-get update && apt-get install inotify-tools -y

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]