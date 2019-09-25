import uuid

from celery import Celery

from app.event_csv.utils import *
from app.ftp import FTPClient
from app.utils.index import build_index, in_index
from app.utils.log import get_logger, fatal
from celery import Celery

from app.event_csv.utils import *
from app.ftp import FTPClient
from app.utils.index import build_index, in_index
from app.utils.log import get_logger, fatal

logging = get_logger(__name__)
from models.models import VehicleEventSummary, CounterEvent, DoorEvent, database

celery_app = Celery('fetcherWorker', backend='rpc://', broker='pyamqp://guest@localhost//')


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(43200, store_data_from_ftp.s())


@celery_app.task
def store_data_from_ftp():
    qs = VehicleEventSummary.select(VehicleEventSummary.filename, VehicleEventSummary.vehicle).distinct().dicts()
    file_index = build_index(qs, 'filename', 'vehicle')
    with FTPClient() as ftp:
        dirs = ftp.ls_by_pattern('logging', pattern=r"([12]\d{3}_(0[1-9]|1[0-2])_(0[1-9]|[12]\d|3[01]))")
        for d in dirs[:1]:
            logging.info('{}'.format(d))
            vehicles = ftp.ls_by_pattern('logging', d, pattern=r"\d{4,}", )
            for v in vehicles:
                logging.info('- {}'.format(v))
                reports = ftp.ls_by_pattern('logging', d, v, 'count', pattern=r"[\w\s]*\.csv")
                filtered_reports = [fname for fname in reports if not in_index(file_index, fname, v)]
                for filename in filtered_reports:
                    content = ftp.read('logging', d, v, 'count', filename)
                    read_and_store_data(v, filename, content)


def read_and_store_data(vehicle_name, filename, content):
    logging.info('  - {}'.format(filename))
    headers, rows = get_header_and_body(content)
    vehicles_and_stats = get_vehicles_and_headers(headers)
    event_dict = {"vehicle_events": [], "door_events": [], "counter_events": []}
    for row in rows:
        row_dict = row_to_dict(row, headers)
        try:
            event_dict = create_vehicle_data(filename, row_dict, vehicles_and_stats, vehicle_name, event_dict)
        except Exception as e:
            fatal('ERROR in file {}'.format(filename))
            raise e

    with database.atomic():
        VehicleEventSummary.insert_many(event_dict["vehicle_events"]).execute()

    with database.atomic():
        DoorEvent.insert_many(event_dict["door_events"]).execute()

    with database.atomic():
        CounterEvent.insert_many(event_dict["counter_events"]).execute()


# this section is terrible
def create_vehicle_data(filename, row_dict, vehicles_dict, vehicle_name, event_dict):
    try:
        date = row_dict["Date"] if "Date" in row_dict else datetime.now().date()
        time = row_dict["Time"] if "Time" in row_dict else datetime.now().time()
        dt = parse_date_and_time_with_fallback(date, time, filename)
        v = VehicleEventSummary(id=uuid.uuid4(), filename=filename, vehicle=vehicle_name, report_datetime=dt.strftime("%Y-%m-%d %H:%M:%S"))
        event_dict["vehicle_events"].append(v)

        # extracting values for each vehicle/counter pair
        for key in vehicles_dict.keys():
            counter_columns = [BOARDING, DEPARTING, COUNTER_STATUS]
            boarding, departing, counter_status = list(map(lambda x: row_dict[re.sub("N", key, x)], counter_columns))

            door_columns = [DOOR_STATUS, DOOR_DURATION, DOOR_OPEN, DOOR_CLOSE]
            door_status, door_duration_string, door_open, door_close = list(
                map(lambda x: row_dict[re.sub("N", key, x)], door_columns))

            duration = duration_to_int(door_duration_string)
            c = CounterEvent(counter=key, boarding=boarding, departing=departing, status=counter_status)
            d = DoorEvent(door=key, status=door_status, duration=duration, open=door_open,
                             close=door_close, counter=c, vehicle_event=v)
            event_dict["door_events"].append(d)
            event_dict["counter_events"].append(c)
        return event_dict
    except Exception as e:
        logging.error(e)
        raise e
