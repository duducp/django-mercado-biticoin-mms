# -*- coding: utf-8 -*-
import socket

from cid.locals import get_cid
from simple_settings import settings


def hostname(logger, log_method, event_dict):
    """
    Adds the application hostname to the log. Useful when the application has
    many pods scaled.
    """
    event_dict['host'] = socket.gethostname()
    return event_dict


def version(logger, log_method, event_dict):
    """
    Adds the application version to the logs.
    """
    event_dict['version'] = settings.VERSION
    return event_dict


def correlation(logger, log_method, event_dict):
    """
    Adds the application correlation id to the logs.
    """
    event_dict['correlation'] = get_cid()
    return event_dict
