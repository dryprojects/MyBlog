import os
import sys

from django.test import TestCase


project_base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(project_base)

os.environ['DJANGO_SETTINGS_MODULE'] = 'MyBlog.settings'

import django

django.setup()

# Create your tests here.
from raven.contrib.django.raven_compat.models import client

try:
    a = 1/0
except ZeroDivisionError:
    client.captureException()