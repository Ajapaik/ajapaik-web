FROM python:2-slim

MAINTAINER Lauri Elias <lauri@ajapaik.ee>

RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends supervisor nginx cmake build-essential

# RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
COPY nginx.nginx /etc/nginx/sites-available/default
COPY supervisor.conf /etc/supervisor/conf.d/ajapaik-web.conf

WORKDIR /home/docker/ajapaik

# So installing requirements would become a cached step
COPY requirements-old.txt ./
RUN pip install --no-cache-dir -r requirements-old.txt

COPY . .

#RUN django-admin.py startproject website /home/docker/ajapaik/
#COPY uwsgi.ini ./
#COPY uwsgi_params ./

RUN apt-get purge cmake build-essential && apt-get autoremove -y && apt-get autoclean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 80

CMD ["/bin/sh", "-c", "/usr/bin/supervisord -n"]