import pytest
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED


@pytest.mark.parametrize("question__type", ["files"])
def test_minio_callback_view(transactional_db, client, answer, minio_mock, settings):
    file = answer.files.first()
    data = {
        "EventName": "s3:ObjectCreated:Put",
        "Key": "caluma-media/218b2504-1736-476e-9975-dc5215ef4f01_test.png",
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "minio:s3",
                "awsRegion": "",
                "eventTime": "2020-07-17T06:38:23.221Z",
                "eventName": "s3:ObjectCreated:Put",
                "userIdentity": {"principalId": "minio"},
                "requestParameters": {
                    "accessKey": "minio",
                    "region": "",
                    "sourceIPAddress": "172.20.0.1",
                },
                "responseElements": {
                    "x-amz-request-id": "162276DB8350E531",
                    "x-minio-deployment-id": "5db7c8da-79cb-4d3a-8d40-189b51ca7aa6",
                    "x-minio-origin-endpoint": "http://172.20.0.2:9000",
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "Config",
                    "bucket": {
                        "name": "caluma-media",
                        "ownerIdentity": {"principalId": "minio"},
                        "arn": "arn:aws:s3:::caluma-media",
                    },
                    "object": {
                        "key": "{file_id}_name".format(file_id=file.id),
                        "size": 299758,
                        "eTag": "af1421c17294eed533ec99eb82b468fb",
                        "contentType": "application/pdf",
                        "userMetadata": {"content-variant": "application/pdf"},
                        "versionId": "1",
                        "sequencer": "162276DB83A9F895",
                    },
                },
                "source": {
                    "host": "172.20.0.1",
                    "port": "",
                    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.15.0 Chrome/80.0.3987.163 Safari/537.36",
                },
            }
        ],
    }

    assert file.is_draft is True
    response = client.post(
        reverse("minio-callback"), data=data, content_type="application/json"
    )
    file.refresh_from_db()
    assert file.is_draft is False
    assert response.status_code == HTTP_201_CREATED
