FROM python:3.12

WORKDIR /app

ENV PYTHONPATH="${PYTHONPATH}:/app"
RUN echo $PYTHONPATH

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "/app/cmd/service/main.py"]
