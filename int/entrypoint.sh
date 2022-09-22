#!/bin/bash
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -d 172.22.0.3 -j ACCEPT
iptables -A OUTPUT -d 172.22.0.5 -j ACCEPT
iptables -P OUTPUT DROP
python3 /app/app.py&
python3 /app/bot/bot.py&