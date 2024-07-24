FROM python:3.11-slim

WORKDIR /app

ADD https://github.com/franklin050187/cosmoteer-com/archive/refs/heads/api_patch.zip /app

RUN unzip api_patch.zip && rm api_patch.zip && mv cosmoteer-com-api_patch cosmoteer-com

WORKDIR /app/cosmoteer-com

RUN pip install --no-cache-dir -r requirements.txt

RUN find /venv -type d -name "__pycache__" -exec rm -r {} + && \
    find /venv -type f -name "*.pyc" -exec rm -r {} + && \
    find /app -type d -name "__pycache__" -exec rm -r {} + && \
    find /app -type f -name "*.pyc" -exec rm -r {} + && \
    rm -rf /root/.cache/pip

CMD ["python", "bot.py"]