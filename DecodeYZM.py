# encoding: utf-8
import re
import base64
import requests
api_url = "http://op.juhe.cn/vercode/index"
# appkey = "eccb4bbdab6cf0bd30bcd274bec6136a"
appkey = "39d7f17a1edceace45ab6caaacc2b87a"


def decodeyzm(imagepath):
    img = open(imagepath, 'rb')
    bimg = base64.b64encode(img.read())
    img.close()
    params = {
        "codeType": "1004",
        "base64Str": bimg,
        "key": appkey,
    }

    lamborghini = requests.session()
    result = lamborghini.post(api_url, params)
    text = result.text
    code_pattern = re.compile('result\":\"(.*?)\"')
    try:
        code = re.findall(code_pattern, text)[0]
        code = code.upper()
    except Exception as e:
        code = '94NB'
        print("exception")
    return code
