from peewee import *

# TODO: tener de referencia para posible conexión con BD
database = MySQLDatabase(
    'tipsterbyte_main_memodevs',
    user='tipsterbyte_main_memodevs',
    password='--',
    host='127.0.0.1',
    port=3306
)

# DB_CONNECTION=mysql
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_DATABASE=laravel_survey
# DB_USERNAME=root
# DB_PASSWORD=