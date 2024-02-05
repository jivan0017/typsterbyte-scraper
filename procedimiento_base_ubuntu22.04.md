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
sudo pip3 install beautifulsoup4 lxml html5lib selenium webdriver-manager
 -----
 ## en  caso de tener todo en un fichero txt (dependencias)
 pip install -r requirements.txt

-- dentro del directorio:
sudo nano gunicorn_conf.py 
sudo nano /etc/systemd/system/tipsterbyte_scraper.service
-------------
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

sudo systemctl start tipsterbyte_scraper
sudo systemctl enable tipsterbyte_scraper

sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn

sudo chmod 666 /var/www/api-scraper-tipsterbyte.memodevs.com/error.log