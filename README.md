# CORS server with html parsing

## Server setup
### Python Environment
```bash
virtualenv --no-site-packages --distribute venv
source venv/bin/activate

pip install -r requirements.txt
```

### Upstart config
```bash
ln -s /opt/projects/cors/cors.conf /etc/init/cors.conf
initctl reload-configuration # to get upstart to see the new script
start cors

tail -f /var/log/upstart/cors.log # for errors
```

### nGinx config
```bash
ln -s /opt/projects/cors/cors.nginx /etc/nginx/sites-enabled/cors
start cors

tail -f /var/log/nginx/error.log # for server errors
```
