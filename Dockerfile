FROM python:3.11

WORKDIR /app

COPY sampleWebApp/requirements.txt .

RUN pip install  --no-cache-dir -r requirements.txt

COPY sampleWebApp/ .

EXPOSE 8080 

CMD ["python", "app.py"]