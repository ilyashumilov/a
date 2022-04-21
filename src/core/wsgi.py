"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
# from django.db.backends.signals import connection_created
# from django.dispatch import receiver
#
#
# @receiver(connection_created)
# def setup_postgres(connection, **kwargs):
#     if connection.vendor != 'postgresql':
#         return
#
#     # Тайм-аут через 30 секунд.
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SET statement_timeout TO 5000;
#         """)
