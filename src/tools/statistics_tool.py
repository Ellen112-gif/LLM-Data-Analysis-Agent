import pandas as pd


class StatisticsTool:
    """
    Perform deterministic statistical analysis
    on a Pandas DataFrame.

    The LLM decides which operation to use.
    This tool performs the actual calculation.
    """

    def __init__(self, df):
        self.df = df

    # =========================
    # Helper
    # =========================

    def _check_column(self, column):
        """Check whether a column exists."""

        if column not in self.df.columns:
            raise ValueError(
                f"Column '{column}' does not exist."
            )

    def _check_numeric_column(self, column):
        """Check whether a column is numeric."""

        self._check_column(column)

        if not pd.api.types.is_numeric_dtype(
            self.df[column]
        ):
            raise ValueError(
                f"Column '{column}' is not numeric."
            )

    # =========================
    # 1. Describe
    # =========================

    def describe(self, column):
        """
        Return descriptive statistics
        for a numeric column.
        """

        try:
            self._check_numeric_column(column)

            series = self.df[column].dropna()

            result = {
                "count": int(series.count()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()),
                "min": float(series.min()),
                "q1": float(series.quantile(0.25)),
                "q3": float(series.quantile(0.75)),
                "max": float(series.max())
            }

            return {
                "success": True,
                "operation": "describe",
                "column": column,
                "result": result
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }

    # =========================
    # 2. Mean
    # =========================

    def mean(self, column):
        """Calculate mean."""

        try:
            self._check_numeric_column(column)

            value = self.df[column].mean()

            return {
                "success": True,
                "operation": "mean",
                "column": column,
                "result": float(value)
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }

    # =========================
    # 3. Median
    # =========================

    def median(self, column):
        """Calculate median."""

        try:
            self._check_numeric_column(column)

            value = self.df[column].median()

            return {
                "success": True,
                "operation": "median",
                "column": column,
                "result": float(value)
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }

    # =========================
    # 4. Correlation
    # =========================

    def correlation(self, column_x, column_y):
        """
        Calculate Pearson correlation
        between two numeric columns.
        """

        try:
            self._check_numeric_column(column_x)
            self._check_numeric_column(column_y)

            value = self.df[
                [column_x, column_y]
            ].corr().iloc[0, 1]

            return {
                "success": True,
                "operation": "correlation",
                "columns": [
                    column_x,
                    column_y
                ],
                "result": float(value)
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }

    # =========================
    # 5. Group Statistics
    # =========================

    def group_stats(
        self,
        group_column,
        value_column,
        operation="mean",
        top_n=10
    ):
        """
        Calculate grouped statistics.

        Example:
        average UnitPrice by Country.
        """

        try:
            self._check_column(group_column)
            self._check_numeric_column(value_column)

            allowed_operations = [
                "mean",
                "median",
                "sum",
                "min",
                "max",
                "count"
            ]

            if operation not in allowed_operations:
                raise ValueError(
                    f"Unsupported operation: {operation}"
                )

            grouped = self.df.groupby(
                group_column
            )[value_column]

            if operation == "mean":
                result = grouped.mean()

            elif operation == "median":
                result = grouped.median()

            elif operation == "sum":
                result = grouped.sum()

            elif operation == "min":
                result = grouped.min()

            elif operation == "max":
                result = grouped.max()

            else:
                result = grouped.count()

            result = (
                result
                .sort_values(ascending=False)
                .head(top_n)
            )

            records = []

            for group, value in result.items():

                records.append({
                    str(group_column): str(group),
                    str(operation): float(value)
                })

            return {
                "success": True,
                "operation": "group_stats",
                "group_column": group_column,
                "value_column": value_column,
                "aggregation": operation,
                "data": records
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error)
            }