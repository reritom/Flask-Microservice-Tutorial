FROM python:3.7-alpine
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY . /app
WORKDIR /app
RUN rm red.db -f
EXPOSE 5001
CMD [ "python", "main.py" ]
