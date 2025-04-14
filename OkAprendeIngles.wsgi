# /var/www/OkAprendeIngles/OkAprendeIngles.wsgi
import sys
import os

# Agrega la ruta de tu aplicación
sys.path.insert(0, '/var/www/OkAprendeIngles')


from run import app as application

