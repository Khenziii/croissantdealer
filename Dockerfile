FROM python:3.11-alpine AS base

# set this arg to true, if you want
# to build the app with a speciffic
# port (8080) exposed.
ARG WEB_SERVER=false
ENV WEB_SERVER=$WEB_SERVER

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# AFAIK, there's no way to expose
# a port condtionally. The container
# has to expose this, even if it
# won't run in the WEB_SERVER mode.
EXPOSE 8080

RUN if [ "$WEB_SERVER" = "false" ]; then \ 
		rm docker-entrypoint.py; \
	else \
		pip3 install flask; \
	fi

CMD if [ "$WEB_SERVER" = "false" ]; then \
		exec python3 main.py; \
	else \
		exec python3 docker-entrypoint.py; \
	fi

