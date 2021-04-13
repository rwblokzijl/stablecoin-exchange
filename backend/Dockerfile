FROM python:3.7.7-alpine

ENV PATH="/scripts:${PATH}"

RUN apk add --update --no-cache libsodium libressl
RUN apk add --update --no-cache --virtual .tmp python3-dev build-base linux-headers libffi-dev libressl-dev musl-dev cargo

RUN pip install cryptography #cache install to avoid building each time requirements change

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN apk del .tmp

RUN mkdir -p /vol/database
RUN mkdir -p /vol/logs
RUN mkdir -p /vol/sync
RUN adduser -D user
RUN chown -R user:user /vol

RUN mkdir /eurotoken
COPY ./stablecoin /eurotoken
WORKDIR /eurotoken
RUN chmod -R 755 /eurotoken

USER user

# CMD ["python", "-u", "run_coin.py"]
CMD ["/bin/sh", "-c", "python -u run_coin.py >> /vol/logs/run.log 2>&1" ]
