## The Movie Database API

### API Docs
https://developers.themoviedb.org/3


### Search
https://developers.themoviedb.org/3/search/search-movies

- required
  - api_key
  - query
- optional
  - language, default: en-US
  - year

year information can help distinguishing movie with the same name in different year
e.g. Total Recall, which has 1990 and 2012 version

https://api.themoviedb.org/3/search/movie?api_key=${APIKEY}&query=total%20recall
https://api.themoviedb.org/3/search/movie?api_key=${APIKEY}&query=total%20recall&language=zh-TW
https://api.themoviedb.org/3/search/movie?api_key=${APIKEY}&query=total%20recall&year=1990


### Movie
https://developers.themoviedb.org/3/movies/get-movie-details

- optional
  - append_to_response, get credits (actor, director, writer) and releases (certificate) in one request

https://api.themoviedb.org/3/movie/861?api_key=${APIKEY}&append_to_response=credits,releases&language=zh-TW


### Translation
https://developers.themoviedb.org/3/movies/get-movie-translations

https://api.themoviedb.org/3/movie/861/translations?api_key=${APIKEY}


### Image
https://developers.themoviedb.org/3/movies/get-movie-images

Movie detail has poster_path and backdrop_path.
Image API can get more images and specify language using include_image_language parameter.

Using `append_to_response` is also possible to append images result in movie detail request.


### Language
ISO-639-1 and ISO 3166-1

https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

