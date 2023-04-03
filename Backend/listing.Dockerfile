FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY listing.py firebasekey.json ./
CMD [ "python", "./listing.py"]