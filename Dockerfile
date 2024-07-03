# syntax=docker/dockerfile:1.4
FROM savesumocluster/sumo:1.12.0
WORKDIR /app
COPY requirements.txt /app
ENV PORT=8080
ENV HOST="0.0.0.0"
RUN apt-get update && apt-get install -y python3-pip
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app

CMD flask --app start.py run --host $HOST --port $PORT
