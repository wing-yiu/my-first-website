FROM ubuntu:18.04

COPY . /app
WORKDIR /app

# Default run configuration
ENV FLASK_APP=flaskapp \
    FLASK_ENV=development \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    GOOGLE_APPLICATION_CREDENTIALS="/app/passportocr-key.json"

# Set timezone to Singapore to use Google API
RUN apt-get update && apt-get -y install tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Singapore /etc/localtime

# Install OpenCV
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-opencv

# Install python 3.6
RUN apt-get update && apt-get install -y python3-pip python3.6-dev build-essential

# Install tesseract 4.0.0-beta.1
RUN apt-get update && apt-get install -y tesseract-ocr 
RUN apt-get -y install libtesseract-dev

# Install Python requirements
RUN pip3 install --no-cache-dir pipenv && \
    pipenv install --system --ignore-pipfile && \
    pip3 uninstall pipenv -y

# Run the app
EXPOSE 5000
ENTRYPOINT flask run --host=0.0.0.0
