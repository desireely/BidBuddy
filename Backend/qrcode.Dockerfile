FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY qr_code.py firebasekey.json key.txt ./
CMD [ "python", "./qr_code.py"]