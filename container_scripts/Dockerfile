FROM python:3.10-alpine

# RUN apt-get -yqq update
# RUN apt-get -yqq install python3-pip python3-dev
RUN apk add gcc musl-dev linux-headers
RUN pip install parsl

ADD app /opt
WORKDIR /opt

# CMD [ "python3", "./app.py" ]
