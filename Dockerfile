FROM python:3.6.7
#FROM ubuntu:latest

MAINTAINER EBI BioSamples <biosamples@ebi.ac.uk>

#RUN apt-get update -y && \
#    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
#COPY ./requirements.txt /app/requirements.txt



COPY . /app
WORKDIR /app
#RUN virtualenv venv
#RUN python3 -m venv ./venv
#RUN source ./venv/bin/activate
RUN pip install -r requirements.txt

#ENTRYPOINT [ "python" ]

#EXPOSE 5000


ENV FLASK_APP=curami/web/
CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]