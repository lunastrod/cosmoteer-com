FROM python:3.11

WORKDIR /app

ADD https://github.com/franklin050187/cosmoteer-com/archive/refs/heads/api_patch.zip /app

RUN unzip api_patch.zip && rm api_patch.zip && mv cosmoteer-com-api_patch cosmoteer-com

WORKDIR /app/cosmoteer-com

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]