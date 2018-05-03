from requests import *
from urllib.parse import urlparse
from os import path, getcwd, makedirs
from img_process import sign_invoice
from api_token import get_header
from local_settings import GL_AMT_CUSTOM_KEY, GL_CODE_CUSTOM_KEY, \
                PROJECT_NAME, SERVER_NAME, KANBAN_COLUMN_ID

# Get API Token and Header
head = get_header()
print(head)


def _parse_list(input_string):
    new_list = input_string.replace(" ", ""). \
        replace(";", ",").replace("|", ",").split(",")
    return new_list


def _format_gl_text(gl_list, amt_list):
    if len(gl_list) == len(amt_list):
        i = 0
        gltext = ""
        while i < len(gl_list):
            gltext += gl_list[i] + " - $" + amt_list[i] + "\n"
            i += 1
        print(gltext)
    else:
        gltext = "List Lengths do not match"
    return gltext


def download(url, download_dir=None):
    # open in binary mode
    if download_dir is None:
        download_dir = getcwd() + "/downloads/"
        if not path.isdir(download_dir):
            # Create Download Directory
            makedirs(download_dir)
    # Double check directory exists of path passed in
    else:
        if not path.isdir(download_dir):
            # Passed in path is invalid, fail gracefully
            return None
    a = urlparse(url)
    file_name = download_dir + path.basename(a.path)
    with open(file_name, "wb") as file:
        # get attachment
        response = get(url)
        # write to file
        file.write(response.content)
        return file_name

def upload_us_attach(userstory_id, filename, project):
    files = {"attached_file": open(filename, 'rb')}
    values = {"from_comment": "False",
             "object_id": str(userstory_id),
             "project": str(project),
             "description": "Signed Invoice"}

    attachUrl = SERVER_NAME + "api/v1/userstories/attachments"
    attachmentResponse = post(attachUrl, headers=head, files=files, data=values)


# Get Project ID
myUrl = SERVER_NAME + 'api/v1/projects'
response = get(myUrl, headers=head)
for i in response.json():
    if i['name'] == PROJECT_NAME:
        project = (i['id'])
print(response)
print(response.headers)
print('----------------')
# Get UserStories from Project
myUrl = SERVER_NAME + "api/v1/userstories?project=" + str(project) + \
                        "&status=" + str(KANBAN_COLUMN_ID)
print(myUrl)
response = get(myUrl, headers=head)
userstories = []
# print(response.json())
for i in response.json():
    # print(i)
    # append UserStory ID and Assigned To tuple
    userstories.append((i['id'],
                        i['assigned_to_extra_info']['full_name_display']))
print(userstories)

for u in userstories:
    attachUrl = SERVER_NAME + "api/v1/userstories/attachments?object_id=" + \
        str(u[0]) + "&project=" + str(project)
    attachmentResponse = get(attachUrl, headers=head)
    attrUrl = SERVER_NAME + "api/v1/userstories/custom-attributes-values/" \
        + str(u[0])
    glcodeResponse = get(attrUrl, headers=head)
    print(glcodeResponse.json())
    if GL_CODE_CUSTOM_KEY in glcodeResponse.json()['attributes_values']:
        gls = _parse_list((glcodeResponse.json()
                           ['attributes_values'][GL_CODE_CUSTOM_KEY]))
        amts = _parse_list((glcodeResponse.json()
                            ['attributes_values'][GL_AMT_CUSTOM_KEY]))
        gltext = _format_gl_text(gls, amts)
        # print(gltext)
        doc_signer = u[1]
        for i in attachmentResponse.json():
            print('url ' + i['url'])
            unsigned_inv = download(i['url'])
            signed_doc = sign_invoice(unsigned_inv, doc_signer, gltext)
            upload_us_attach(u[0], signed_doc, project)
    else:
        print("Amount or GL Code missing!")
