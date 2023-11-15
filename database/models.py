from peewee import *
from data.config import DB_PORT, DB_PASSWORD, DB_HOST, DB_USER, DB_NAME


db = PostgresqlDatabase(DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD, port=DB_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    user_id = BigIntegerField(unique=True, primary_key=True)

    class Meta:
        db_table = 'users'


class Movies(BaseModel):
    movie_code = IntegerField()
    movie_title = CharField(max_length=500)
    movie_id = CharField(max_length=300, primary_key=True)
    views = BigIntegerField(default=0)

    class Meta:
        db_table = 'movies'


class Channels(BaseModel):
    channel_name = CharField(max_length=150)
    channel_id = BigIntegerField(primary_key=True)
    channel_link = CharField(max_length=200)

    class Meta:
        db_table = 'channels'


class Admins(BaseModel):
    admin_id = BigIntegerField(primary_key=True)
    admin_name = CharField(max_length=100)

    class Meta:
        db_table = 'admins'
