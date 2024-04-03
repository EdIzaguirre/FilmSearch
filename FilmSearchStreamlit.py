import streamlit as st
from chat_app import FilmSearch
import pandas as pd
import json

st.set_page_config(
    page_title="Film Search",
    page_icon="🎥",
)

with open('./config.json') as f:
    config = json.load(f)

st.markdown("<h1 style='text-align: center;'>🎥 Film Search</h1>",
            unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>The better way to search for films.</h2>",
            unsafe_allow_html=True)

beginning_year = config["years"][0]
ending_year = config["years"][-1]

f"""
This film search bot has been given a database of roughly the 100 most popular
films from the years {beginning_year}-{ending_year}. It will only recommend films from this
database.
"""


def generate_response(input_text):
    chat = FilmSearch()
    st.write_stream(chat.ask(input_text))


st.markdown(
    "*Feel free to try one of these sample queries, or type your own below.*")

col1, col2, col3 = st.columns(3)

with col1:
    example = "Find me drama movies in English that are less than 2 hours long and feature pets."
    if st.button(example, key='button1'):
        st.session_state.query = example

with col2:
    example = "Films with very little dialogue made after 1950."
    if st.button(example, key='button2'):
        st.session_state.query = example

with col3:
    example = "Recommend some funny zombie movies that are streaming on Hulu."
    if st.button(example, key='button3'):
        st.session_state.query = example

with st.form('my_form'):
    text = st.text_area(
        label='Query:',
        placeholder='Type your query here.',
        value=st.session_state.query if 'query' in st.session_state else '',
        label_visibility='hidden')
    submitted = st.form_submit_button('Submit')
    if submitted:
        generate_response(text)

st.divider()

df = pd.read_csv('./data/full_movie_collection_data.csv')

# Prevent commas from appearing in release year
df['Release Year'] = df['Release Year'].astype(str)

# Reverse order
df = df.iloc[::-1]

st.header("Data Source")
st.write("""
         All data was pulled from the The Movie Database (TMDB) and compiled
         into a CSV file, provided here. Watch providers were pulled from
         JustWatch.
         """)
st.dataframe(df, hide_index=True)
