from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


class FilmSearch:

    rag_chain = None

    def __init__(self):
        load_dotenv('.env', override=True)
        NEO4J_URI = os.getenv('NEO4J_URI')
        NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
        NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

        # self.model = ChatOpenAI(model='gpt-4-0125-preview', temperature=0.5)
        self.model = ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0.5)

        retrieval_query = """
        WITH 
            node, score
        RETURN "Title: " + node.title + "\n" + 
                "Overview: " + node.overview  + "\n" + 
                "Release Date: " + node.release_date  + "\n" + 
                "Runtime: " + node.runtime + " minutes" + "\n" + 
                "Language: " + node.language  + "\n" + 
                "Keywords: " + node.keywords  + "\n" + 
                "Genres: " + node.genres + "\n" +
                "Actors: " + node.actors + "\n" +
                "Directors: " + node.directors + "\n" +
                "Production Companies: " + node.production_companies + "\n" +
                "Source: " + node.source  + "\n"
                as text, score, node {.source} AS metadata
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    """
                    Your goal is to recommend films to users based on their
                    query and the retrieved context. Only recommend films
                    shown in your context. If a film doesn't seem relevant, 
                    omit it from your response. You should recommend no more 
                    than five films. Your recommendation should be original, 
                    insightful, and at least two to three sentences long. 
                    Determine whether the query would best be answered using 
                    full text search or semantic search before picking your 
                    tool.

                    # TEMPLATE FOR OUTPUT
                    - [Title of Film](link to source):
                        - Runtime:
                        - Release Date:
                        - (Your reasoning for recommending this film)
                    
                    Question: {question} 
                    Context: {context} 
                    """
                ),
            ]
        )

        vector_store = Neo4jVector.from_existing_graph(
            embedding=OpenAIEmbeddings(),
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            index_name="film_index",
            node_label="Film",
            text_node_properties=["overview", "keywords", "language",
                                  "release_date", "runtime", "actors",
                                  "directors", "genres", "production_companies"
                                  ],
            embedding_node_property="embedding",
            search_type="hybrid",
            retrieval_query=retrieval_query
        )

        # Create a retriever from the vector store
        retriever = vector_store.as_retriever(search_kwargs={"k": 10})

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        chat_model = ChatOpenAI(
            model='gpt-3.5-turbo-0125',
            # model='gpt-4-0125-preview',
            temperature=0,
            streaming=True,
        )

        # Create a chatbot Question & Answer chain from the retriever
        rag_chain_from_docs = (
            RunnablePassthrough.assign(
                context=(lambda x: format_docs(x["context"])))
            | prompt
            | chat_model
            | StrOutputParser()
        )

        self.rag_chain = RunnableParallel(
            {"context": retriever, "question": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)

    def ask(self, query: str):
        for chunk in self.rag_chain.stream(query):
            for key in chunk:
                if key == 'answer':
                    yield chunk[key]
