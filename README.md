# passportocr

[![Python version](https://img.shields.io/badge/python-3.6-blue.svg)](https://shields.io/)
[![Tesseract version](https://img.shields.io/badge/tesseract-4.0-orange.svg)](https://shields.io/)
[![OpenCV version](https://img.shields.io/badge/OpenCV-3.4.2-green.svg)](https://shields.io/)

Collection of utilities to extract text from passport images using OCR.

## 1. Demo
### Environment variables
Environment variables are stored in a `.env` file
```
FLASK_APP=main.py
FLASK_ENV=development
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8
GOOGLE_APPLICATION_CREDENTIALS="passportocr-key.json" # obtain this file from 1Password
```

### Docker
Before starting the application, make sure you have `.env` file 
and `passportocr-key.json` in root folder.
```bash
# Start application in docker container
docker-compose up

# Or manually build docker image and run container
docker build -t passportocr:latest .
docker run -it -p 5000:5000 passportocr:latest
```


## 2. Development
### Python
```bash
# Initialise Python 3.6 in working directory
pipenv --python 3.6

# Install Python libraries from Pipfile
pipenv install

# Activate Python environment
pipenv shell

```

### Others
[Tesseract 4.0](https://www.learnopencv.com/deep-learning-based-text-recognition-ocr-using-tesseract-and-opencv/)
```bash
sudo add-apt-repository ppa:alex-p/tesseract-ocr
sudo apt-get update
sudo apt-get install tesseract-ocr libtesseract-dev libleptonica-dev
```

### Local flask app

```bash
# Activate Python environment
pipenv shell

# Run flask app
flask run
```

### Endpoints
- /result_gcp: Performs OCR using google cloud vision python client
- /result_ctpn: Performs OCR using CTPN text detection


## 3. Methodology
### Text Detection
There are various methods for detecting text in an image, we use methods 1 and 2 in this demo.

Method 1:  
Text detection using pre-trained model from [CTPN library](https://github.com/eragonruan/text-detection-ctpn).

Method 2:  
Using [google cloud vision](https://cloud.google.com/vision/docs/) to do both text detection and recognition

Method 3:  
Using purely image preprocessing techniques in OpenCV to identify dark text on
light background. In particular for passport images, we try to [identify
the machine readable zone](https://docs.google.com/document/d/167g9Yy8DA3N18c-D7GTO3zw1_sZzUtrGf8Jm4oOgIOw/edit)
and other portions of text.

### OCR
We rely on PyTesseract to parse the image and return the text.
These are Python wrappers around the Tesseract library.
