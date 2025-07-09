FROM python:3.11-alpine
WORKDIR /go
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 9999
CMD ["sh", "-c", "python app.py init_db && waitress-serve --host 0.0.0.0 --port 9999 app:app"]
