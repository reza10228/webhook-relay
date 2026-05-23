FROM repo.asax.ir/python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY formatter.py .

EXPOSE 8686

CMD ["python", "app.py"]

