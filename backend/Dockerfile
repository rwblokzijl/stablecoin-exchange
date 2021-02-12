FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache pcre-dev
RUN apk add --update --no-cache --virtual .tmp python3-dev build-base linux-headers pcre-dev

RUN pip install -r /requirements.txt

RUN apk del .tmp

RUN mkdir -p /vol/database
RUN adduser -D user
RUN chown -R user:user /vol

# COPY ./scripts /scripts
# RUN chmod +x /scripts/*

COPY ./run_coin.py /scripts/run_coin.py
RUN chmod +x /scripts/*

RUN mkdir /eurotoken
COPY ./backend /eurotoken
WORKDIR /eurotoken
RUN chmod -R 755 /eurotoken

USER user

CMD ["run_coin.py"]


