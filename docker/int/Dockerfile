FROM ubuntu:18.04
WORKDIR /app
RUN apt-get update -y 
RUN apt-get install -y python3-pip python3-dev build-essential libcurl4-openssl-dev libssl-dev
RUN apt-get install -y net-tools curl
RUN apt-get install -y procps
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils
RUN apt-get install -y libnss3 wget

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent
RUN pip3 install pycurl pymysql flask selenium 
ENTRYPOINT /app/entrypoint.sh && /bin/bash
CMD ["true"]