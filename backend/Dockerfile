FROM python:3.7-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache libsodium libressl
RUN apk add --update --no-cache --virtual .tmp python3-dev build-base linux-headers libffi-dev libressl-dev musl-dev cargo

RUN pip install -r /requirements.txt

RUN apk del .tmp

RUN mkdir -p /vol/database
RUN adduser -D user
RUN chown -R user:user /vol

RUN mkdir /eurotoken
COPY ./stablecoin /eurotoken
WORKDIR /eurotoken
RUN chmod -R 755 /eurotoken

USER user

CMD ["python", "-u", "run_coin.py"]
