FROM ubuntu:18.04
WORKDIR /app
RUN apt-get update -y 
RUN apt-get install -y python3-pip python3-dev build-essential libcurl4-openssl-dev libssl-dev
RUN apt-get install -y net-tools
RUN apt-get install -y procps
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent
RUN pip3 install pycurl pymysql flask selenium
ENTRYPOINT /app/entrypoint.sh && /bin/bash
CMD ["true"]