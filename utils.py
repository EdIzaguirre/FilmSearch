import requests
import csv
import time


def get_id_list(api_key, year, max_retries=5):
    """
    Function to get list of IDs for all films made in {year}.

    parameters:
    api_key (str): API key for TMDB
    year (int): Year of interest

    returns:
    list of str: List of all movie ids in {year}
    """
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={
        api_key}&primary_release_year={
            year}&include_video=false&language=en-US&sort_by=popularity.desc'

    movie_ids = []

    total_pages = 5  # 5 pages of ids = 100 movies
    for page in range(1, total_pages + 1):
        response = requests.get(url + f'&page={page}')
        for i in range(max_retries):
            if response.status_code == 429:
                # If the response was a 429, wait and then try again
                print(
                    f"Request limit reached. Waiting and retrying ({i+1}/{
                        max_retries})")
                time.sleep(2 ** i)  # Exponential backoff

            else:
                # If the response was not a 429, continue
                dict = response.json()
                for film in dict['results']:
                    movie_ids.append(str(film['id']))
                break

    return movie_ids


def get_data(API_key, Movie_ID, max_retries=5):
    """
    Function to pull details of your film of interest in JSON format.
    Assumes desired language is in US-Engish.

    parameters:
    API_key (str): Your API key for TMBD
    Movie_ID (str): TMDB id for film of interest

    returns:
    dict: JSON formatted dictionary containing all details of your film of
    interest
    """
    query = 'https://api.themoviedb.org/3/movie/' + \
        Movie_ID+'?api_key='+API_key+'&language=en-US' + \
        '&append_to_response=keywords'
    response = requests.get(query)
    for i in range(max_retries):
        if response.status_code == 429:
            # If the response was a 429, wait and then try again
            print(
                f"Request limit reached. Waiting and retrying ({i+1}/{
                    max_retries})")
            time.sleep(2 ** i)  # Exponential backoff
        else:
            dict = response.json()
            return dict


def write_file(filename, dict):
    """
    Appends a row to a csv file titled 'filename', if the
    movie belongs to a collection. The row contains the name of the
    movie in the first column and the name of the collection in the
    second column. Adds nothing if the film is not part of the collection.

    parameters:
    filename (str): Name of file you desire for the csv
    dict (dict): Python dictionary with JSON formatted details of film

    returns:
    None
    """
    csvFile = open(filename, 'a')
    csvwriter = csv.writer(csvFile)
    # unpack the result to access the "collection name" element
    title = dict['title']
    runtime = dict['runtime']
    language = dict['original_language']
    release_date = dict['release_date']
    overview = dict['overview']
    all_genres = dict['genres']

    genre_str = ""
    for genre in all_genres:
        genre_str += genre['name'] + ", "
    genre_str = genre_str[:-2]

    all_keywords = dict['keywords']['keywords']
    keyword_str = ""
    for keyword in all_keywords:
        keyword_str += keyword['name'] + ", "

    keyword_str = keyword_str[:-2]

    result = [title, runtime, language, overview,
              release_date, genre_str, keyword_str]
    # write data
    csvwriter.writerow(result)
    csvFile.close()
