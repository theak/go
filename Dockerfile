FROM python:3.11-slim
RUN apt-get update && apt-get install git -y
RUN git clone https://github.com/theak/go.git
ADD requirements.txt /go/
ADD app.py /go/
WORKDIR /go
RUN pip install -r requirements.txt
RUN python3.11 app.py init_db
CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "9999", "app:app"]
