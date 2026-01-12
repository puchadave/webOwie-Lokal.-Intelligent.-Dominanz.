# Dockerfile for OSINT Marketing Tool (production)
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV PORT=8000

# Expose the port Gunicorn will run on
EXPOSE 8000

# Initialize the database (optional, can be run manually)
# RUN python -c 'from app import initialize_database; initialize_database()'

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
