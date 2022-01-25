# Скачивание снимков Земли с API Nasa

### Описание

Программа обращается к ресурсу с изображениями Земли, сделанными Nasa и скачивает снимки в папку epic, после чего отправляет все снимки в ваш telegram канал

### Установка

Python должен быть установлен. Затем используйте pip (или pip3 если есть конфликт с Python2) для установки зависимостей. Затем создайте виртуальное окружение и в терминале выполните команду по установке зависимостей:

```
pip install -r requirements.txt
```

### Переменные окружения

Для доступа к ресурсу NASA, нужен токен авторизации, который нужно получить по [ссылке](https://api.nasa.gov/). После генерации токена, создайте в корневой директории файл с переменными окружения .env и добавьте в него ваш токен в формате

`AUTH_TOKEN=ваш_токен`

Для отправки изображений необходим бот, его можно создать по [инструкции](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram.html). Полученный токен добавить в файл .env в формате

`BOT_TOKEN=ваш_токен`

Нужно указать чат, в который бот будет сбрасывать снимки, если у вас нет чата, то создайте по [инструкции](https://smmplanner.com/blog/otlozhennyj-posting-v-telegram/). Затем скопируйте ID чата и создайте переменную окружения в формате

`CHAT_ID=@ваш_канал`

По умолчанию, бот опубликовывает снимки раз в 24 часа, чтобы изменить это значение, создайте переменную окружения с временным периодом

`SENDING_PERIOD=время_в_секундах`

### Пример работы

Сервис запускается из терминала командой 

```
python saving_images.py
```

### Цель проекта

Проект написан в образовательных целях для ресурса [Devman](https://dvmn.org/)
