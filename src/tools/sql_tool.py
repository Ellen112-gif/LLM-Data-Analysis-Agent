import sqlite3

import pandas as pd


class SQLTool:
    """
    Execute read-only SQL queries against a Pandas DataFrame.

    The DataFrame is loaded into an in-memory SQLite database.
    """

    def __init__(self, df, table_name="data"):
        self.table_name = table_name

        # Create an in-memory SQLite database.
        # It disappears when the program ends.
        self.connection = sqlite3.connect(":memory:",
    check_same_thread=False)

        # Load DataFrame into SQLite.
        df.to_sql(
            self.table_name,
            self.connection,
            index=False,
            if_exists="replace"
        )

    def validate_query(self, query):
        """
        Only allow read-only SELECT queries.
        """

        cleaned_query = query.strip().lower()

        # Query must start with SELECT.
        if not cleaned_query.startswith("select"):
            raise ValueError(
                "Only SELECT queries are allowed."
            )

        # Block dangerous SQL keywords.
        blocked_keywords = [
            "insert",
            "update",
            "delete",
            "drop",
            "alter",
            "create",
            "replace",
            "truncate",
            "attach",
            "detach"
        ]

        for keyword in blocked_keywords:
            if keyword in cleaned_query:
                raise ValueError(
                    f"Blocked SQL keyword detected: {keyword}"
                )

        return True

    def run(self, query):
        """
        Validate and execute SQL query.
        """

        self.validate_query(query)

        try:
            result = pd.read_sql_query(
                query,
                self.connection
            )

            return {
                "success": True,
                "row_count": len(result),
                "columns": result.columns.tolist(),
                "data": result.to_dict(
                    orient="records"
                )
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }

    def close(self):
        """Close SQLite connection."""

        self.connection.close()