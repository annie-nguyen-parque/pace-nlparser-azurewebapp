# Basic flask container

FROM tiangolo/uwsgi-nginx-flask:latest

ADD ./app /home/app/
WORKDIR /home/app/
EXPOSE 5000
RUN pip install Flask-SQLAlchemy
RUN pip install spacy
RUN pip install psycopg2
ENTRYPOINT ["python3", "app.py"]
