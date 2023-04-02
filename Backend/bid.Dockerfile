FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY bid.py firebasekey.json ./
CMD [ "python", "./bid.py"]