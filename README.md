# 2023-10-05-reksoft

## Описание проекта

CRUD сервис без использования фреймворков. 

## Установка и запуск проекта

В папке склонированного репозитория создайте виртуальное окружение и установите зависимости из `requirements.txt`
Далее выполните:
```bash
docker-compose up --build
```
И в соседней консоли:
```bash
uvicorn main:app --host=0.0.0.0 --port 8000 --reload --log-level=info
```
Во время инициализации, в БД создаются нужные таблицы и заполняются тестовыми данными.

## Эндпоинты
- /resources
- /resources/\<id>
- /resource_types
- /resource_types/\<id>

Для GET `/resources`, для фильтрации результата также принимаются аргументы вида `resources/?type=1,2`, где `1,2` - ID типов ресурсов.  
Для DELETE, для удаления нескольких записей БД, принимаются аргументы вида `resources/?id=1,2`, где `1,2` - ID записей к удалению. 


## Стек

gunicorn

## Автор

Семён Егоров  

[LinkedIn](https://www.linkedin.com/in/simonegorov/)  
[Email](rhinorofl@gmail.com)  
[Telegram](https://t.me/SamePersoon)



uvicorn main:app --host=0.0.0.0 --port 8000 --reload --log-level=info
