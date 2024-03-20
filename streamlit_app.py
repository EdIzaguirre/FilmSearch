import streamlit as st
from chat_app import FilmSearch
import pandas as pd

st.title('🎥 Film Search')
st.subheader('The better way to search for films.')
"""
This film search bot has been given a database of roughly the 100 most popular
films from the years 2022-2023. It will only recommend films from this
database.
"""


def generate_response(input_text):
    agent = FilmSearch()
    response = agent.ask({"input": input_text})
    st.info(response['output'])


with st.form('my_form'):
    text = st.text_area(
        'Query:',
        'I enjoy Wes Anderson movies. Give me some film recommendations.')
    submitted = st.form_submit_button('Submit')
    if submitted:
        generate_response(text)

st.divider()

YEARS = [2022, 2023]

df2022 = pd.read_csv('data/2022_movie_collection_data.csv')
df2023 = pd.read_csv('data/2023_movie_collection_data.csv')

# Combine the dataframes
combined_df = pd.concat([df2022, df2023])
st.header("Data Source")
st.write("""
         All data was pulled from the The Movie Database (TMDB) and compiled
         into a CSV file, provided here. Watch providers were pulled from
         JustWatch.
         """)
st.dataframe(combined_df, hide_index=True)
