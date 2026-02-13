# Smart Home Project

Проект для управления компонентами "умного дома" на базе Raspberry Pi. Состоит из двух основных компонентов:

1. **Flask-сервер**, запущенный из `local_flask_server/`, обрабатывающий локальные API-запросы (например, от камеры).
2. **Docker-приложения**, запускаемые через `docker-compose` из корня `smart_home`.

Проект состоит из двух  компонентов:

1. **Flask-сервер** – запущен из каталога `local_flask_server/` и отвечает за управление камерой через локальные API-запросы.
2. **Docker-приложение** – запускается через `docker-compose` из корневого каталога `smart_home` и включает в себя:
   - **Django-сервер** – основной сервер для управления умным домом.
   - **Celery** – для выполнения фоновых задач.
   - **Celery Beat** – для планирования периодических задач.
   - **Redis** – в качестве брокера для Celery.

Проект автоматически запускается при включении Raspberry Pi с помощью `systemd` сервиса.

---

## Автозапуск

Автозапуск реализован с помощью `systemd`. После включения Raspberry Pi:

- Flask-сервер запускается из `local_flask_server/`
- Далее запускается `docker-compose` с параметром `--build -d`

Сервис настроен в файле:

```bash
/etc/systemd/system/smart_home.service
```

### Пример содержимого `smart_home.service`:

```ini
[Unit]
Description=Smart Home Startup Service
After=network.target docker.service

[Service]
Type=simple
ExecStart=/home/nikita/autostart/start_smart_home.sh
Restart=on-failure
User=nikita
WorkingDirectory=/home/nikita/smart_home
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Скрипт запуска `/home/nikita/autostart/start_smart_home.sh`:

```bash
#!/bin/bash
cd /home/nikita/smart_home/local_flask_server || exit
nohup /usr/bin/python3 camera_api.py >> /home/nikita/logs/flask.log 2>&1 &

cd /home/nikita/smart_home || exit
/usr/bin/docker-compose up --build -d >> /home/nikita/logs/docker.log 2>&1
```

---

## Установка

```bash
sudo systemctl daemon-reload
sudo systemctl enable smart_home.service
sudo systemctl start smart_home.service
```

---

## Ручной запуск

Если нужно запустить вручную:

```bash
cd ~/smart_home/local_flask_server
python3 camera_api.py &

cd ~/smart_home
docker-compose up --build -d
```
