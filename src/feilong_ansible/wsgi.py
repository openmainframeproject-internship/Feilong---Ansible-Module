[uwsgi]
module = wsgi:app

master = true
processes = 5

socket = feilong_ansible.sock
logto = /var/log/uwsgi/%n.log
chmod-socket = 776
http-socket = 127.0.0.1:8000
vacuum = true


die-on-term =  true
