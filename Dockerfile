# Basic flask container

FROM tiangolo/uwsgi-nginx-flask:latest

ADD ./app /home/app/
WORKDIR /home/app/
EXPOSE 5000
RUN pip install spacy
RUN python -m spacy download en_core_web_sm
RUN pip install Flask-SQLAlchemy
RUN pip install psycopg2
RUN pip install pandas
RUN pip install numpy

ENTRYPOINT ["python3", "app.py"]