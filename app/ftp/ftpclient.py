from ftplib import FTP
import re
from io import BytesIO
from app import config
import logging


class FTPClient:
    def __init__(self):
        self.host = config.get("default", "FTP_HOST")
        self.user = config.get("default", "FTP_USER")
        passw = config.get("default", "FTP_PASSWORD")
        logging.info("setting up FTPClient for {}@{}".format(self.user, self.host))
        try:
            self.client = FTP(self.host, timeout=10)
            self.client.login(user=self.user, passwd=passw)
        except Exception as e:
            logging.error(e)

    def close(self):
        logging.info("closing connection to {}".format(self.host))
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return True

    def read(self, *path):
        reader = BytesIO()
        try:
            self.client.retrbinary('RETR {}'.format('/'.join(path)), reader.write)
            reader.seek(0)
        except Exception as e:
            logging.error(e)
        finally:
            return reader.getvalue()

    def ls(self, *path):
        try:
            return self.client.nlst('/'.join(path))
        except Exception as e:
            logging.error(e)
            return None

    def ls_by_pattern(self, *path, pattern=""):
        try:
            path = '/'.join(path)
            p = re.compile(pattern)
            return [x for x in self.client.nlst('{}'.format(path)) if p.match(x)]
        except Exception as e:
            logging.error(e)
            return None
