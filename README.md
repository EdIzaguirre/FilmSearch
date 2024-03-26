# 🎥 FilmSearch

## The better way to search for films.

This film search bot has been given a database of roughly the 100 most popular films from the years 1920-2023. It will only recommend films from this database.

Bot was created using LangChain and Pinecone for the vector database. This application uses a variant of Retrieval Augmented Generation (RAG) that uses what is called a self-querying retriever in order to filter the films via metadata.

All data was pulled from the The Movie Database (TMDB) and compiled into CSV files, provided in the data folder. Watch providers were pulled from JustWatch.

Movies contain the following attributes:

- Title
- Runtime (minutes)
- Language
- Overview
- Release Year
- Genre
- Keywords
- Actors
- Directors
- Stream
- Buy
- Rent
- Production Companies
- Website
