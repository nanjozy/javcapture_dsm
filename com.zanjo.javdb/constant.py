ERROR_PLUGIN_QUERY_FAIL = 1003
ERROR_PLUGIN_PARSE_RESULT_FAIL = 1004

PLUGINID = 'com.zanjo.javdb'
THEMOVIEDB_URL = 'https://javdb.com/'
BANNER_URL = 'https://image.tmdb.org/t/p/w500'
BACKDROP_URL = 'https://image.tmdb.org/t/p/original'

# TODO: you should assign your own APIKEY here
APIKEY = "http://127.0.0.1:5004"

DEV = True

MOVIE_DATA_TEMPLATE = {
    'title': '',
    'tagline': '',
    'original_available': '',
    'original_title': '',
    'summary': '',
    'certificate': '',
    'genre': [],
    'actor': [],
    'director': [],
    'writer': [],
    'extra': {}
}


def trace():
    if DEV:
        import traceback
        traceback.print_exc()
