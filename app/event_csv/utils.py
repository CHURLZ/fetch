import logging
import re

# column names
from datetime import datetime

COUNTER_STATUS = 'Counter status(N)'
BOARDING = 'Boarding door(N)'
DEPARTING = 'Departing door(N)'

DOOR_STATUS = 'Door status(N)'
DOOR_DURATION = 'Door duration(N)'
DOOR_OPEN = 'Door open(N)'
DOOR_CLOSE = 'Door close(N)'


def get_header_and_body(content):
    lines = content.decode('UTF-8').strip().split('\n')
    headers = lines[0].split(';')
    rows = [x.split(';') for x in lines[1:]]
    logging.debug('got {} columns and {} rows'.format(len(headers), len(rows)))
    return headers, rows


def row_to_dict(row, headers):
    # construct a dict from the row of values so that we don't have to remember the header order
    row_dict = {}
    for i, v in enumerate(row):
        row_dict[headers[i]] = v
    return row_dict


def get_vehicles_and_headers(headers):
    columns_by_vehicle = {}
    for h in headers:
        # regex to find two groups: the stat, like "door close" and the vehicle id, like "(1)"
        m = re.match(r"(?P<stat>[\w\s]+)\((?P<number>\d)\)", h)
        if m:
            # build up a dictionary with key: vehicle and values:list of columns.
            md = m.groupdict()
            if md["number"] in columns_by_vehicle:
                columns_by_vehicle[md["number"]] += [md["stat"]]
            else:
                columns_by_vehicle[md["number"]] = [md["stat"]]
    return columns_by_vehicle


def duration_to_int(duration):
    try:
        _time = datetime.strptime(duration, '%H:%M:%S')
        return int(_time.hour * 3600 + _time.minute * 60 + _time.second)
    except:
        pass

    try:
        _time = datetime.strptime(duration, '%M:%S')
        return int(_time.hour * 3600 + _time.minute * 60 + _time.second)
    except:
        logging.debug('could not parse duration, default: 0')
        return 0


def parse_date_and_time_with_fallback(date, time, filename):
    try:
        return datetime.strptime('{} {}'.format(date, time), '%Y.%m.%d %H:%M:%S')
    except Exception as e:
        logging.warning('could not parse datetime for {} {}, replacing with filename. {}'.format(date, time, e))
        try:
            _date = datetime.strptime(filename[:10], '%Y_%m_%d')
            return _date
        except:
            raise SyntaxError('Cannot parse {} into datetime with format {}'.format(filename, '%Y_%m_%d'))
