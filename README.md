A Web App for uploading File to Salesforce
==========================================


Nginx Configuration
-------------------

upstream uwsgiserver {
    server 127.0.0.1:3031;
}

# HTTPS server
#
server {
    listen       443 ssl;
    server_name  app.360casb.com;
    client_max_body_size 10M;

    ssl on;
    ssl_certificate      /path/to/ssl.crt;
    ssl_certificate_key  /path/to/ssl.key;

    location / {
      include            uwsgi_params;
      uwsgi_pass         uwsgiserver;
      proxy_redirect     off;
      proxy_set_header   Host $host;
      proxy_set_header   X-Real-IP $remote_addr;
      proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header   X-Forwarded-Host $server_name;
   }
}
