FROM python:latest

WORKDIR /bot

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y gcc libpq-dev python3-pip

RUN pip install -r requirements.txt

COPY . /bot

CMD ["python", "bot.py"]
