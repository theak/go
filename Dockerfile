FROM python:3.11-alpine
WORKDIR /go
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
COPY . .
RUN python app.py init_db
ENV PATH=/root/.local/bin:$PATH
EXPOSE 9999
CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "9999", "app:app"]
