import requests
import mimetypes
import cgi
import pathlib
import uuid

file_url = 'http://www.prienai.lt/get_file.php?file=WVdSbW5aZlFaZEdTeTJpVGFLUm96bVNhYmFTYnFNYmJuWjZkbFdTVmtkbHBySmFzWjQ2VHlKblBtOWFjWUpyUmFhdWNtNXVaeWRLZm1wbWNaSlZoejVWa2FhS1Z3R1hLeE0lMkJaMEcyV2FOUnBhR2lwbUpxV3padWx5cGhrMldDUllwdHRubW5OWmNuRWwyaVVtV2h4a21Sbm1aeklwSjNMeDNTWmRHaktZYyUyQlVsR3FvWk5WcDFwTGJiTTl3cFduV2thdHRrNXVUeTVhWGFjbGpZSjFna3BKcm1tZG5rV0dTbE5CdzFKMlliWnhwZEcwJTNE'

file = requests.get(file_url, timeout=10)

# params = cgi.parse_header(file.headers.get('Content-Disposition'))
# print(uuid.uuid4().hex + str(pathlib.Path(params[1]['filename']).suffix))



print(file.headers)



# import re
# p = re.compile( '(?!<a )(?!<\/a>)<[^>]+>')
# test = p.sub('', '<span>TEST1</span> <span>TEST2</span> <a href="#">TEST3</a>')
# print(test)
