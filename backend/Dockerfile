FROM python:3.11

ENV PYTHONUNBUFFERED=1

ARG UID=1000
ARG GID=1000

RUN groupadd -g $GID appgroup && \
    useradd -m -u $UID -g appgroup appuser

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP="app.py:initialize_app()"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R appuser:appgroup /app

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]