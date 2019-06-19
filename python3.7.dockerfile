FROM python:3.7

COPY dev-requirements.txt /var/validate_it/dev-requirements.txt
RUN pip install -r /var/validate_it/dev-requirements.txt
WORKDIR /var/validate_it
ENV PYTHONPATH "${PYTHONPATH}:/var/validate_it/validate_it"
