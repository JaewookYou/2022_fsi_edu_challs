#!/bin/bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y /app/bot/google-chrome-stable_current_amd64.deb
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -d 172.22.0.3 -j ACCEPT
iptables -A OUTPUT -s 172.22.0.4 -d 172.22.0.4 -j ACCEPT
iptables -A OUTPUT -s localhost -d localhost -j ACCEPT
iptables -A OUTPUT -p tcp --dport 3306 -d 172.22.0.5 -j ACCEPT
iptables -P OUTPUT DROP
iptables -P INPUT ACCEPT
python3 /app/app.py&
python3 /app/bot/bot.py&