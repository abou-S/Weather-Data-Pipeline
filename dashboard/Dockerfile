FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY dashboard.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8502

CMD ["streamlit", "run", "dashboard.py", "--server.port=8502", "--server.address=0.0.0.0"]