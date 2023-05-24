FROM python:3.8.16

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY ./libs ./libs
COPY ./api.py ./
COPY ./stop_checker.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD waitress-serve --host 0.0.0.0 api:app | python ./stop_checker.py
