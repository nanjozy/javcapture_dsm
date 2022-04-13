import argparse
import html
import json
import sys
import urllib.parse, urllib.request, urllib.error

import constant


def _plugin_run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help='json string')
    parser.add_argument("--lang", type=str, required=True, default=None, help='enu|cht|...')
    parser.add_argument("--type", type=str, required=True, default=None, help='movie|tvshow|...')
    parser.add_argument("--limit", type=int, default=1, help='result count')
    parser.add_argument("--allowguess", type=bool, default=True)

    # unknownPrm is useless, just for prevent error when unknow param inside
    args, unknownPrm = parser.parse_known_args()

    argv_input = json.loads(args.input)
    argv_lang = args.lang
    argv_type = args.type
    argv_limit = args.limit
    argv_allowguess = args.allowguess

    result = None
    success = True
    error_code = 0
    try:
        result = _process(argv_input, )
        success = result.get("success")
        result = result.get("result")
        result = result[:argv_limit]
        for i, v in enumerate(result):
            if not v.get("original_available"):
                v["original_available"] = "2012-09-27"
            if not v.get("director"):
                v["director"] = [""]
            result[i] = v
    except SystemExit as query_e:
        constant.trace()
        error_code = constant.ERROR_PLUGIN_QUERY_FAIL
        success = False
        result = []

    except Exception as e:
        constant.trace()
        error_code = constant.ERROR_PLUGIN_PARSE_RESULT_FAIL
        success = False
        result = []

    _process_output(success, error_code, result)


def _process(input_obj, ):
    title = input_obj['title']
    query_data = search_media(title, )
    return query_data


def _process_output(success, error_code, datas):
    if success:
        result_obj = {'success': True, 'result': datas}
    else:
        result_obj = {'success': False, 'error_code': error_code}

    json_string = json.dumps(result_obj, ensure_ascii=False, separators=(',', ':'))
    json_string = html.unescape(json_string)
    print(json_string)


def search_media(name, ):
    nameEncode = urllib.parse.quote_plus(name)
    url = constant.APIKEY + '/javdb/' + nameEncode
    result = http_get_download(url)
    result = json.loads(result)
    return result


def http_get_download(url):
    timeouts = 60
    header = {
        r'user-agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_1; de-de) AppleWebKit/527+ (KHTML, like Gecko) Version/3.1.1 Safari/525.20',
    }
    try:

        opener = urllib.request.build_opener()

        request = urllib.request.Request(url=url, headers=header, method='GET')

        response = opener.open(request, timeout=timeouts)
        result = response.read().decode('utf-8')

    except urllib.error.HTTPError as http_e:
        if http_e.code == 404:
            response_obj = json.loads(http_e.read().decode())
            if response_obj.get('status_code') == 34:
                return None
        sys.exit()

    except Exception:
        sys.exit()

    return result


if __name__ == "__main__":
    _plugin_run()
