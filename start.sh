# start nginx, with rtmp forwarding
sudo /usr/local/nginx/sbin/nginx

# start shadowsocks
sudo systemctl restart shadowsocks-libev-redir@config

# setup iptables
sudo shadowsocks.sh
