from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
import os
from langchain_together import Together
from langchain_openai import ChatOpenAI







def create_agent(db_uri,model="gpt-4"):
    db = SQLDatabase.from_uri(db_uri)
    return create_sql_agent(
        llm=ChatOpenAI(model=model),
        db=db
    )


def database_read_write_agent(query):
    """
    SQL agent able read and wrtie into the table
    """
    db_uri = "sqlite:///l-hackathondb_new.sqlite"
    agent = create_agent(db_uri)
    result = agent.invoke(query)
    return(result)


