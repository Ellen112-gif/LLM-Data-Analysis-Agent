from langchain_core.tools import tool


def create_agent_tools(sql_tool, statistics_tool):
    """
    Wrap existing data analysis tools
    as LangChain tools for the LLM.
    """

    @tool
    def run_sql(query: str) -> dict:
        """
        Execute a read-only SQL SELECT query on the dataset.

        The table name is 'data'.

        Use this tool for filtering, grouping, aggregation,
        sorting, and retrieving rows from the dataset.
        """

        return sql_tool.run(query)


    @tool
    def calculate_correlation(
        column_x: str,
        column_y: str
    ) -> dict:
        """
        Calculate the Pearson correlation between
        two numeric columns in the dataset.

        Use this tool when the user asks about
        correlation or linear relationship between
        two numeric variables.
        """

        return statistics_tool.correlation(
            column_x,
            column_y
        )


    return [
        run_sql,
        calculate_correlation
    ]