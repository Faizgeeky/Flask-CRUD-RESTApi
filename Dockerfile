# Use an official Python runtime as a parent image
FROM python:3-alpine3.15
WORKDIR /app

COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0

CMD ["flask", "run", "--host=0.0.0.0"]
