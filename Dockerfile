FROM python:3.8

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# RUN pip install -U "ray[default]" google-api-python-client
# RUN ray up -y cluster-config.yml

COPY ./app /code/app