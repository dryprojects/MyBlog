import sys
import os


project_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

sys.path.append(project_base)

os.environ['DJANGO_SETTINGS_MODULE'] = 'MyBlog.settings'

import django
django.setup()