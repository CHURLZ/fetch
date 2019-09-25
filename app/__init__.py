import configparser
import logging
import os

# read config from file
config = configparser.ConfigParser()
config.read('./app/config.ini')


def get_config(path):
    try:
        config.read(path)
        return config
    except:
        raise
