FROM python:3.9
RUN apt-get update && apt-get install -y redis-server
COPY requirements_new.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements_new.txt
RUN pip3 install supervisor
COPY . /app
WORKDIR /app/src
EXPOSE 8000
ENV TH_DEPLOY True
CMD ["gunicorn", "--worker-tmp-dir", "/dev/shm", "--timeout", "120", "app:server"]
