# Инструкция

## Запуск

1. Создать виртуальное окружение:

         python -m venv venv

2. Запустить виртуальное окружение:

         .\venv\Scripts\activate

4. Запустить приложение:

   Стандартный запуск:

         py main.py

## Дополнительно:

Создаёт requirements.txt:

      python -m pip freeze > requirements.txt

Установить requirements.txt:

      python -m pip install -r requirements.txt

PowerShell:

      python -m pip freeze | ForEach-Object { python -m pip uninstall -y $_ }

Необходимое расширение для Chrome:

      Click&Clean - https://chromewebstore.google.com/detail/clickclean/ghgabhipcejejjmhhchfonmamedcbeod?hl=ru

pyinstaller:

      pyinstaller --noconsole --onefile main.py

User:

      Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
