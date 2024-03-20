from langchain.agents import AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.prompts.prompt import PromptTemplate


class FilmSearch:

    agent_executor = None
    retriever = None

    def __init__(self):
        load_dotenv('.env', override=True)
        NEO4J_URI = os.getenv('NEO4J_URI')
        NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
        NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

        self.model = ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0.5)

        retrieval_query_window = """
            MATCH (node:Film)-[:HAS_GENRE]->(genre:Genre)
            MATCH (actor:Actor)-[:STARRED_IN]->(node)
            MATCH (director:Director)-[:HAS_DIRECTED]->(node)
            MATCH (prod_co:Production_Company)-[:PRODUCED]->(node)
            WITH 
                node, collect(distinct genre.type) as genres, 
                collect(distinct actor.name) as actors, 
                collect(distinct director.name) as directors, 
                collect(distinct prod_co.name) as companies, 
                score
            RETURN "Title: " + node.title + "\n" + 
                    "Overview: " + node.overview  + "\n" + 
                    "Release Date: " + node.release_date  + "\n" + 
                    "Runtime: " + node.runtime + " minutes" + "\n" + 
                    "Language: " + node.language  + "\n" + 
                    "Keywords: " + node.keywords  + "\n" + 
                    "Genres: " + apoc.text.join(genres, ', ') + "\n" +
                    "Actors: " + apoc.text.join(actors, ', ') + "\n" +
                    "Directors: " + apoc.text.join(directors, ', ') + "\n" +
                    "Production Companies: " + apoc.text.join(companies, ', ') + "\n" +
                    "Source: " + node.source  + "\n"
                    as text, score, node {.source} AS metadata
            """

        vector_store_window = Neo4jVector.from_existing_graph(
            embedding=OpenAIEmbeddings(),
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
            index_name="film_index",
            node_label="Film",
            text_node_properties=["overview", "keywords",
                                  "language", "release_date", "runtime"],
            embedding_node_property="embedding",
            search_type="hybrid",
            retrieval_query=retrieval_query_window
        )

        # Create a retriever from the vector store
        retriever_window = vector_store_window.as_retriever()

        # Create tool from retriever
        retriever_tool = create_retriever_tool(
            retriever_window,
            "movie_data",
            """
            Use this tool to get films to recommend to the user.
            """
        )

        tools = [retriever_tool]

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    """
                    Your goal is to recommend films to users based on their
                    query and the retrieved context. If a film doesn't seem
                    relevant, omit it from your response. You should recommend
                    no more than five films. Your recommendation should be
                    original, insightful, and at least two to three sentences
                    long. Only recommend films shown in your context.

                    # TEMPLATE FOR OUTPUT
                    - [Title of Film]:
                        - Runtime:
                        - Release Date:
                        - Recommendation:
                        - Source:
                    ...
                    
                    """
                ),
                MessagesPlaceholder(
                    variable_name='chat_history', optional=True),
                HumanMessagePromptTemplate(prompt=PromptTemplate(
                    input_variables=['input'], template='{input}')),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_tools_agent(self.model, tools, prompt_template)

        self.agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True)

    def ask(self, query: str):
        return self.agent_executor.invoke(query)
