from app.tasks import store_data_from_ftp

# this is only used to force trigger a sync.
if __name__ == "__main__":
    store_data_from_ftp.delay()