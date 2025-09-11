FROM python:3.12-slim

WORKDIR /server

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

EXPOSE 8000
CMD ["python","app/main.py"]