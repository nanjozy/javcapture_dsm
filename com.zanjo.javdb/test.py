import argparse
import shutil
import json
import os
import subprocess
import constant
import copy

SYNO_PLUGIN_DATA_DIRECTORY = '/var/packages/VideoStation/target/plugins/plugin_data/'
EXECUTE_EXE = '/bin/bash'


def _parse_argument():
    description = '\n \
    query and check parse result for custom plugin\n \
    argument list for each type:\n \
        movie: type, lang, input, [limit], [apikey], path, pluginid\n \
            input: title [original_available]\n \
        \n \
        tvshow: type, lang, input, [limit], [apikey], path, pluginid\n \
            input: title, [original_available]\n \
        \n \
        tvshow_episode: type, lang, input, [limit], [apikey], path, pluginid\n \
            input: title, [original_available], season, episode\n \
        \n \
    \n'

    parser = argparse.ArgumentParser(description)

    parser.add_argument('--type', type=str, required=True, choices=['movie', 'tvshow', 'tvshow_episode'],
                        help='test type: movie, tvshow, tvshow_episode')
    parser.add_argument('--lang', type=str, required=True, help='language of result')
    parser.add_argument('--input', type=str, required=True, help='input value which is different by type')
    parser.add_argument('--limit', type=int, required=False, default=1, help='language of result')
    parser.add_argument('--apikey', type=str, required=False, help='plugin apikey')
    parser.add_argument('--path', type=str, required=True,
                        help='plugin path, ex: "../syno_themoviedb/loader.sh"')
    parser.add_argument('--pluginid', type=str, required=True, help='plugin id, ex: "com.synology.TheMovieDb"')

    # unknownPrm is useless, just for prevent error when unknow param inside
    args, unknownPrm = parser.parse_known_args()
    return vars(args)


def _query_and_check():
    parameters = _parse_argument()

    if not os.path.exists(parameters['path']):
        return {'success': False, 'error_code': constant.ERROR_PLUGIN_PARSE_RESULT_FAIL, 'msg': 'plugin path not exist'}

    success, response = _query(parameters)
    print(success,response)
    if not success:
        return {'success': False, 'error_code': constant.ERROR_PLUGIN_PARSE_RESULT_FAIL, 'msg': 'execute plugin fail'}

    check_result_obj = True
    return check_result_obj


def _query(parameters):
    _remove_cache(parameters['pluginid'])
    execute_array = _compose_execute_array(parameters)
    success, response = _execute_cmd(execute_array)
    return success, response


def _remove_cache(pluginid):
    SYNO_PLUGIN_DATA_DIRECTORY_PLUGINID = SYNO_PLUGIN_DATA_DIRECTORY + pluginid
    if os.path.exists(SYNO_PLUGIN_DATA_DIRECTORY_PLUGINID):
        shutil.rmtree(SYNO_PLUGIN_DATA_DIRECTORY_PLUGINID)


def _compose_execute_array(parameters):
    execute_array = [EXECUTE_EXE, '-p', parameters['path']]

    execute_arguments = copy.deepcopy(parameters)
    execute_arguments.pop('path')
    execute_arguments.pop('pluginid')
    if not execute_arguments.get('apikey'):
        execute_arguments.pop('apikey')

    for key in execute_arguments:
        execute_array.append('--{0}'.format(key))

        if isinstance(execute_arguments[key], dict):
            execute_array.append(json.dumps(execute_arguments[key]))
        else:
            execute_array.append(str(execute_arguments[key]))
    return execute_array


def _execute_cmd(execute_array):
    p = subprocess.Popen(execute_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if err:
        return False, ''

    response_string = str(out, 'utf-8')
    return True, response_string


if __name__ == "__main__":
    result_obj = _query_and_check()
    check_result_string = json.dumps(result_obj)
    print(check_result_string)
