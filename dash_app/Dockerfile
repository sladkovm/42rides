FROM python:3.6.7

RUN mkdir -p /home/project/dash_app
WORKDIR /home/project/dash_app
COPY requirements-dash-app.txt /home/project/dash_app
RUN pip install --no-cache-dir -r requirements-dash-app.txt

COPY . /home/project/dash_app

