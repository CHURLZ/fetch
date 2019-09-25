import datetime

from app import config
from peewee import Model, CharField, IntegerField, DateTimeField, ForeignKeyField, AutoField, UUIDField
from peewee import PostgresqlDatabase, SqliteDatabase

database = SqliteDatabase('vehicle_stats.db', 'Pooling=true')

host = config.get("default", "POSTGRES_HOST")
port = config.get("default", "POSTGRES_PORT")
user = config.get("default", "POSTGRES_USER")
passw = config.get("default", "POSTGRES_PASSW")
db = config.get("default", "POSTGRES_DB")
database = PostgresqlDatabase(db, user=user, password=passw, host=host, port=port)


class BaseModel(Model):
    class Meta:
        database = database


class VehicleEventSummary(BaseModel):
    id = UUIDField(primary_key=True)
    vehicle = CharField()
    filename = CharField()
    report_datetime = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        indexes = (
            (('vehicle', 'filename', 'report_datetime'), True),
        )


class CounterEvent(BaseModel):
    id = AutoField()
    counter = IntegerField()
    boarding = IntegerField()
    departing = IntegerField()
    status = IntegerField()


class DoorEvent(BaseModel):
    id = AutoField()
    door = IntegerField()
    open = CharField()
    close = CharField()
    duration = IntegerField()
    status = IntegerField()

    vehicle_event = ForeignKeyField(VehicleEventSummary)
    counter = ForeignKeyField(CounterEvent)
