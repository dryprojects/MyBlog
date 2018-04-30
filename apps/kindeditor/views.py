import json
import shutil
import os

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.contrib.sites.models import Site

from kindeditor.forms import ImageFileForm


class ImageFileUpload(View):
    def post(self, request):
        form = ImageFileForm(request.POST, request.FILES)
        current_site = Site.objects.get_current(request)
        http = 'https://' if request.is_secure() else 'http://'

        if form.is_valid():
            instance = form.save()
            img_url = "%s%s%s"%(http, current_site.domain, instance.imgFile.url)
            return HttpResponse(json.dumps({'error':0, 'message':img_url}), content_type='application/json', status=201)
        else:
            return HttpResponse(json.dumps({'error':1, 'message':','.join(form.errors['imgFile'])}), content_type='application/json', status=400)