import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from caluma.caluma_form.models import File


@require_http_methods(["HEAD", "POST"])
def minio_callback_view(request):
    status = HTTP_200_OK
    if request.method == "HEAD":
        return HttpResponse(status=status)

    data = json.loads(request.body.decode("utf-8"))

    for record in data["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        if not bucket_name == settings.MINIO_STORAGE_MEDIA_BUCKET_NAME:
            continue

        file_pk = record["s3"]["object"]["key"].split("_")[0]
        try:
            file = File.objects.get(pk=file_pk)
        except File.DoesNotExist:
            return HttpResponse(status=HTTP_400_BAD_REQUEST)

        file.is_draft = False
        file.save()
        status = HTTP_201_CREATED

    return HttpResponse(status=status)
