import logging

from models.models import VehicleEventSummary, CounterEvent, DoorEvent, database


def create_tables():
    logging.info("creating tables...")
    try:
        with database:
            database.create_tables([VehicleEventSummary, CounterEvent, DoorEvent])
    except Exception as e:
        logging.error(e)