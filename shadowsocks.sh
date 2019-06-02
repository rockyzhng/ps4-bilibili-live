#!/bin/sh

# flush current rules
iptables -A SHADOWSOCKS -F

# enable forwarding
sysctl -w net.ipv4.ip_forward=1
sysctl -p

# setup UDP forward
ip route add local default dev lo table 100
ip rule add fwmark 1 lookup 100

# Create a new chain called SHADOWSOCKS
iptables -t nat -N SHADOWSOCKS

# Rules BEGIN
# if object is shadowsocks server, return
#    -- by port
# * port for directly tcp connection, disable in kcptun mode
iptables -t nat -A SHADOWSOCKS -p tcp --dport 56229 -j RETURN
# * port for udp2raw forwarding
# iptables -t nat -A SHADOWSOCKS -p tcp --dport 7680 -j RETURN
# iptables -t nat -A SHADOWSOCKS -p tcp --dport 8877 -j RETURN
#    -- by ip
# iptables -t nat -A SHADOWSOCKS -d 185.225.13.5 -j RETURN

# -- for UDP RAW MODE
# filter out tcp traffic and redirect
#    -- using kcptun and udp2raw
#       TODO: should filter out local net
# iptables -t nat -A SHADOWSOCKS -p tcp --dport 4000 -j REDIRECT --to-ports 1754
#    -- using tcp directly connect
#       for server will reject connection from many locations, we do not use this route. or we can use other ss-redir instance
# iptables -t nat -A SHADOWSOCKS -p tcp --dport 4000 -j DNAT --to 89.31.126.137:56229

# leave alone special ports
iptables -t nat -A SHADOWSOCKS -p tcp --dport 53 -j RETURN # DNS
iptables -t nat -A SHADOWSOCKS -p tcp --dport 1935 -j RETURN # LIVE STREAM PORT
# iptables -t nat -A SHADOWSOCKS -p tcp -s 192.168/16 --dport 6667 -j REDIRECT --to-port 6667 # IRC PORT

# filter out local traffic
iptables -t nat -A SHADOWSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A SHADOWSOCKS -d 240.0.0.0/4 -j RETURN

# other traffic, we redirect it to local ss server listening on port 7777
iptables -t nat -A SHADOWSOCKS -p tcp -j REDIRECT --to-ports 7777

# Rules END

# special rules for local rtmp traffic
# according to ports
# REDIRECT HERE works like DNAT to 127.0.0.1

iptables -t nat -A PREROUTING -p tcp --dport 1935 -j REDIRECT --to-ports 1935

# deal with UDP forwarding from ps4
# UDP traffic is considered to forward to localhost:4000
ip route add local default dev lo table 100
ip rule add fwmark 1 lookup 100
# Must allow this to reach Twitch
# iptables -t mangle -A PREROUTING -p udp --dport 53 -j RETURN
iptables -t mangle -A PREROUTING -p udp -s 192.168.0.0/16 -j TPROXY --on-port 7777 --tproxy-mark 0x01/0x01

# for netgates, insert this chain before PREROUTING chain
iptables -t nat -A PREROUTING -p tcp -j SHADOWSOCKS

# for local traffic, filter it before out
iptables -t nat -A OUTPUT -p tcp -j SHADOWSOCKS 

