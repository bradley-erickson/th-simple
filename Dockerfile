FROM python:3.9
RUN apt-get update && apt-get install -y redis-server celery
COPY requirements_new.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements_new.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
ENV TH_DEPLOY True
CMD ["./deploy.sh"]
