# Инструкция

## Запуск

1. Создать виртуальное окружение:

         py -3.12 -m venv venv
         python -m venv venv

2. Запустить виртуальное окружение:

         .\venv\Scripts\activate

4. Запустить приложение:

   Стандартный запуск:

         mitmproxy --listen-port 8080 -s save_clicks.py

## Дополнительно:

Создаёт requirements.txt:

      python -m pip freeze > requirements.txt

Установить requirements.txt:

      python -m pip install -r requirements.txt

PowerShell:

      python -m pip freeze | ForEach-Object { python -m pip uninstall -y $_ }

Nuitka:
      python -m nuitka --onefile --windows-disable-console --mingw64 --lto=yes main.py
      python -m nuitka --onefile --windows-console-mode=disable main.py
