FROM python:3.9
COPY requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt
RUN pip3 install supervisor
COPY . /app
WORKDIR /app/src
EXPOSE 8000
ENV TH_DEPLOY True
CMD ["supervisord", "-c", "supervisord.conf"]
