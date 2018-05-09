from requests import get, post, patch
from os import path
from settings import *
from api_token import authenticate, get_header

authenticate()
head = get_header()

'''
files = {'upload_file': open('file.txt','rb')}
values = {'DB': 'photcat', 'OUT': 'csv', 'SHORT': 'short'}

r = requests.post(url, files=files, data=values)

curl -X POST \
-H "Content-Type: multipart/form-data" \
-H "Authorization: Bearer ${AUTH_TOKEN}" \
-F attached_file=@test.png \
-F from_comment=False \
-F object_id=1 \
-F project=1 \
-s http://localhost:8000/api/v1/userstories/attachments

'''


def upload():
    desc = 13
    files = {"attached_file": open("downloads/testupload.png", 'rb')}
    values = {"from_comment": "False",
             "object_id": "117",
             "project": "6",
             "description": str(desc)}

    attachUrl = SERVER_NAME + "api/v1/userstories/attachments"
    attachmentResponse = post(attachUrl, headers=head, files=files, data=values)
    # attachmentResponse = post(attachUrl, headers=head, data=values, files=files)

    print (attachUrl)
    print (attachmentResponse.text)
    print (attachmentResponse.json())
    print (attachmentResponse)


def change_status(userstory_id):
    values = {"version": "4",
              "status": "35"}
    us_url = SERVER_NAME + "api/v1/userstories/" + str(userstory_id)
    usResponse = patch(us_url, headers=head, data=values)
    print(usResponse.text)
    print(usResponse.json())


# upload()
change_status(117)
