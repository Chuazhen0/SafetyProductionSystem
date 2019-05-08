FROM python:3.6.5
ENV PYTHONUNBUFFERED 1
RUN apt-get update  && apt-get install apt-utils build-essential g++ flex bison gperf ruby perl \
  mysql-client \
  libfontconfig1-dev libicu-dev libfreetype6 libssl-dev \
  libpng-dev libjpeg-dev python libx11-dev libxext-dev -y

RUN apt-get update && apt-get -y install cron

RUN apt-get install fonts-liberation
RUN apt-get install graphviz-dev
RUN apt-get install graphviz-doc
RUN apt-get install libann0
RUN apt-get install libxmu6
RUN apt-get install libxaw7
RUN apt-get install libgraphviz-dev
RUN apt-get install pkg-config && apt --fix-broken install
RUN apt-get install graphviz

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
