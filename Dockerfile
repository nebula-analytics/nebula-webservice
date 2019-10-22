FROM tiangolo/uwsgi-nginx-flask:python3.7

RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt
USER appuser

COPY . /app
