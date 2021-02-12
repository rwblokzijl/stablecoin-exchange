FROM python3.7-nodejs12-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache libsodium libressl
RUN apk add --update --no-cache --virtual .tmp python3-dev build-base linux-headers libffi-dev libressl-dev musl-dev

RUN pip install -r /requirements.txt

RUN apk del .tmp

RUN mkdir -p /vol/database

RUN mkdir /eurotoken
WORKDIR /eurotoken
RUN chmod -R 755 /eurotoken

WORKDIR /usr/app
COPY package.json .
RUN npm install --quiet
COPY . .

CMD ["python", "run_coin.py"]
