# import requests
# response = requests.get("https://kvituzaidimas.vmi.lt/", timeout=10)
# print(response.headers)

import re
p = re.compile( '(?!<a )(?!<\/a>)<[^>]+>')
test = p.sub('', '<span>TEST1</span> <span>TEST2</span> <a href="#">TEST3</a>')
print(test)