# INSTALACIÓN FASTAPI
pip install fastapi

# INSTALACIÓN DEL SERVIDOR PARA PYTHON
pip install uvicorn[standard]
python -m uvicorn main:app --reload

# Install library peewee:
pip install peewee

# Librerías requests and scrap tool
pip install requests
pip install requests-html
pip install beautifulsoup4

# mySQL Driver (opcional)
pip install pymysql


pip install beautifulsoup4
pip3 install lxml
pip3 install html5lib
pip install selenium
pip install webdriver-manager 
-------------------------------

# Correr la app definida en el main.py:
uvicorn main:app --reload

- correr la app en un puerto distinto cuando tenemos ocupado el 8080, 80:
uvicorn main:app --port 8001 --reload









instalación de librerías en el entorno virtual .env python:
fast-api
pip install requests-html


- realizar solicitudes http de manera asíncrona:
pip install aiohttp


- saber que imports no se usan:
pip install flake8
- ejecutar en consola:
flake8 main.py --select=F401


