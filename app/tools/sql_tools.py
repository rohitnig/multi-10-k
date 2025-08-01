from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

def get_sql_database_tool():
    """Creates a LangChain SQL tool that can handle natural language queries."""
    db = SQLDatabase.from_uri("sqlite:///financials.db")
    
    sql_tool = QuerySQLDataBaseTool(
        db=db,
        name="sql_database_query",
        description=(
            "Use this tool to query a SQLite database containing QUARTERLY financial data for 2023-2024. "
            "Contains table 'quarterly_financials' with columns: year, quarter, revenue_millions, profit_millions. "
            "BEST for: total profit calculations, revenue trends, quarterly comparisons. "
            "Input: SQL query to execute against the database. "
            "Example: SELECT SUM(profit_millions) FROM quarterly_financials WHERE year = 2023"
        )
    )
    return sql_tool

# Instantiate the tool
sql_database_tool = get_sql_database_tool()
