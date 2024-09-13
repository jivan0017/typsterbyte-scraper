## INSTALACIÓN PY
sudo apt update
sudo apt upgrade -y
sudo reboot

## PY
sudo apt install python3 python3-pip -y
sudo apt install python3-venv

pip3 install wheel
sudo pip3 install fastapi[all]
sudo pip3 install uvicorn gunicorn

- dentro del directorio del proyecto: /var/www/api-scraper-tipsterbyte.memodevs.com
------
sudo python3 -m venv venv
source venv/bin/activate

------
sudo pip3 install requests requests-html beautifulsoup4

<!-- sudo pip install beautifulsoup4 -->
sudo pip3 install lxml html5lib selenium webdriver-manager
 -----
 ## en  caso de tener todo en un fichero txt (dependencias)
 pip install -r requirements.txt

-- dentro del directorio base raíz:
sudo nano gunicorn_conf.py 
sudo nano /etc/systemd/system/tipsterbyte_scraper.service
-------------


**********************************************************
- contenido del fichero gunicorn_conf.py:
**********************************************************
# gunicorn_conf.py
from multiprocessing import cpu_count

bind = "127.0.0.1:8000"

# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/var/www/api-scraper-tipsterbyte.memodevs.com/access_log'
errorlog =  '/var/www/api-scraper-tipsterbyte.memodevs.com/error_log'
-------------



**********************************************************
  contenido del fichero tipsterbyte_scraper.service:
**********************************************************
- en teoría:
[Unit]
Description=Gunicorn Daemon for FastAPI TipsterByte
After=network.target

[Service]
User=jdiaz
Group=www-data
WorkingDirectory=/var/www/api-scraper-tipsterbyte.memodevs.com
ExecStart=/var/www/api-scraper-tipsterbyte.memodevs.com/env/bin/gunicorn -c gunicorn_conf.py main:app

[Install]
WantedBy=multi-user.target
-------------
- en producción:
[Unit]
Description=Gunicorn Daemon for FastAPI TipsterByte
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/api-scraper-tipsterbyte.memodevs.com
ExecStart=/var/www/api-scraper-tipsterbyte.memodevs.com/venv/bin/gunicorn -c gunicorn_conf.py --timeout 3600  main:app

[Install]
WantedBy=multi-user.target
-------------

sudo systemctl start tipsterbyte_scraper
sudo systemctl enable tipsterbyte_scraper
sudo systemctl status tipsterbyte_scraper

sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn

sudo chmod 666 /var/www/api-scraper-tipsterbyte.memodevs.com/error_log


git:https://github.com