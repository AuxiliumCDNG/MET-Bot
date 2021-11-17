import binascii
import json
import os
import pathlib
import time
from io import BytesIO

import requests

from interactions.create import headers


def formdata(text, filename, data):
    boundary = binascii.hexlify(os.urandom(16)).decode('ascii')

    payload = {
        "content": "%s" % text,
        "embeds": [
            {"image": {"url": "attachment://[filename]"}}
        ]
    }
    """
    body = '--[boundary]\n' \
           'Content-Disposition: form-data; name="payload_json"\n' \
           'Content-Type: application/json\n\n' \
           '[payload]\n' \
           '--[boundary]\n' \
           'Content-Disposition: form-data; name="file"; filename="[filename]"\n' \
           'Content-Type: image/png\n\n' \
           '%s\n' \
           '--[boundary]--'.replace("[payload]", json.dumps(payload)).replace("[boundary]", boundary).replace("[text]", text).replace("[filename]", filename) % data
    """
    body = {
        "payload_json": ("", json.dumps(payload), "application/json"),
        "file": (filename, data, "image/png")
    }

    print(body)

    return body


def run(req, res_url=None, **kwargs):
    data = requests.get("https://api.sped-v.de/v1/spedition/targets",
                        headers={
                            "X-Api-Key": "oHkxbJSRe5-42HcxBzikFEXHuOjBXsyY7oYTFmORkbG4bOIo26J1s3ab0YfiQqP-gVG7aegiLVuZGkKzGUUwSQ--"}).json()

    progress = BytesIO()
    r = requests.get(
        "https://quickchart.io/chart?w=300&h=50&c={ type: 'progressBar', data: { datasets: [{ data: [%s] }] } }" % (
                    int(float(data[0]["alrreached"] / data[0]["moneyamount"]) * 100)))

    progress.write(r.content)
    progress.seek(0)
    pathlib.Path('test.png').write_bytes(progress.getbuffer())
    time.sleep(1)

    multipart_header = dict(headers)
    multipart_header["Content-Type"] = "multipart/form-data"

    r = requests.patch(res_url, json={"content": "Erledigt...", "embeds": [], "allowed_mentions": []}, headers=headers)
    print(res_url)
    print(multipart_header)
    r = requests.post("/".join(res_url.split("/")[:-2]), headers=multipart_header, files=formdata("Hier die Daten:", "progress.png", progress.read()))  # , json={"payload_json": formdata("Hier die Daten:", "progress.png", progress.read())}, )
    print("\n\n", r.json())

    progress.close()
    return
