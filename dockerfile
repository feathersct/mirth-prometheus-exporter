FROM python:3.12
LABEL MAINTAINER="clayton.feathers"

ADD mirth_exporter.py .
ADD mirthConfig.json .

RUN pip install mirthpy prometheus_client
EXPOSE 9001

CMD ["python", "./mirth_exporter.py"]