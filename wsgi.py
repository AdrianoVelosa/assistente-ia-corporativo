# wsgi.py
# Ponto de entrada para servidores WSGI como Gunicorn

from app import app

if __name__ == "__main__":
    app.run()