#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from dotenv import load_dotenv


def main():
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            'available on your PYTHONPATH environment variable? Did you '
            'forget to activate a virtual environment?'
        ) from exc
    execute_from_command_line(sys.argv)


def set_settings_module():
    load_dotenv()

    _settings = (
        os.getenv('SIMPLE_SETTINGS') or
        os.getenv('DJANGO_SETTINGS_MODULE')
    )
    if not _settings:
        _settings = 'project.core.settings.development'

    os.environ.setdefault('SIMPLE_SETTINGS', _settings)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', _settings)
    print(f'Using settings "{_settings}"')


if __name__ == '__main__':
    set_settings_module()
    main()
