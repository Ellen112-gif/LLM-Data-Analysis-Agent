import pandas as pd


class DataProfiler:
    """
    Generate basic metadata and statistics for a pandas DataFrame.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_shape(self) -> dict:
        """
        Return the number of rows and columns.
        """
        return {
            "rows": self.df.shape[0],
            "columns": self.df.shape[1]
        }

    def get_column_types(self) -> dict:
        """
        Return data types for each column.
        """
        return {
            column: str(dtype)
            for column, dtype in self.df.dtypes.items()
        }

    def get_missing_values(self) -> dict:
        """
        Return the number of missing values for each column.
        """
        return self.df.isnull().sum().to_dict()

    def get_duplicate_count(self) -> int:
        """
        Return the number of duplicated rows.
        """
        return int(self.df.duplicated().sum())

    def get_numeric_summary(self) -> dict:
        """
        Return descriptive statistics for numeric columns.
        """
        numeric_df = self.df.select_dtypes(include="number")

        if numeric_df.empty:
            return {}

        return numeric_df.describe().to_dict()

    def profile(self) -> dict:
        """
        Generate the complete dataset profile.
        """
        return {
            "shape": self.get_shape(),
            "column_types": self.get_column_types(),
            "missing_values": self.get_missing_values(),
            "duplicate_rows": self.get_duplicate_count(),
            "numeric_summary": self.get_numeric_summary()
        }