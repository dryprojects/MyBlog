import json

from django.http import HttpResponse
from django.views.generic import View
from django.contrib.sites.models import Site

from kindeditor.forms import ImageFileForm


class ImageFileUpload(View):
    def post(self, request):
        """
        POST参数
            imgFile: 文件form名称
            dir: 上传类型，分别为image、flash、media、file
        :param request:
        :return:
        """
        form = ImageFileForm(request.POST, request.FILES)
        current_site = Site.objects.get_current(request)
        http = 'https://' if request.is_secure() else 'http://'

        if form.is_valid():
            instance = form.save()
            img_url = "%s%s%s" % (http, current_site.domain, instance.imgFile.url)
            return HttpResponse(json.dumps({'error': 0, 'url': img_url}), content_type='application/json', status=201)
        else:
            return HttpResponse(json.dumps({'error': 1, 'message': ','.join(form.errors['imgFile'])}),
                                content_type='application/json', status=400)
