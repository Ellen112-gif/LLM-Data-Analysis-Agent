import pandas as pd


class DataQualityChecker:
    """
    Check common data quality issues.
    The checker only detects problems.
    It does NOT modify the original dataset.
    """

    def __init__(self, df):
        self.df = df

    # =========================
    # 1. Missing Values
    # =========================
    def check_missing_values(self):
        """Check columns with missing values."""
        issues = []
        for column in self.df.columns:
            missing_count = int(self.df[column].isna().sum())
            if missing_count > 0:
                missing_ratio = missing_count / len(self.df)
                issues.append({
                    "type": "missing_values",
                    "column": column,
                    "count": missing_count,
                    "ratio": round(missing_ratio, 4),
                    "severity": "high" if missing_ratio > 0.3 else "medium"
                })
        return issues

    # =========================
    # 2. Duplicate Rows
    # =========================
    def check_duplicates(self):
        """Check duplicate rows."""
        duplicate_count = int(self.df.duplicated().sum())
        if duplicate_count == 0:
            return []
        duplicate_ratio = duplicate_count / len(self.df)
        return [{
            "type": "duplicate_rows",
            "count": duplicate_count,
            "ratio": round(duplicate_ratio, 4),
            "severity": "high" if duplicate_ratio > 0.05 else "medium"
        }]

    # =========================
    # 3. Constant Columns
    # =========================
    def check_constant_columns(self):
        """Check columns containing only one unique value."""
        issues = []
        for column in self.df.columns:
            unique_count = self.df[column].nunique(dropna=False)
            if unique_count <= 1:
                issues.append({
                    "type": "constant_column",
                    "column": column,
                    "unique_count": int(unique_count),
                    "severity": "medium"
                })
        return issues

    # =========================
    # 4. High Cardinality
    # =========================
    def check_high_cardinality(self):
        """
        Check categorical/text columns with
        unusually high unique-value ratios.
        """
        issues = []
        for column in self.df.columns:
            series = self.df[column]
            # Only check object/string columns
            if series.dtype == "object" or str(series.dtype) == "string":
                unique_ratio = series.nunique(dropna=True) / len(self.df)
                if unique_ratio > 0.5:
                    issues.append({
                        "type": "high_cardinality",
                        "column": column,
                        "unique_count": int(series.nunique(dropna=True)),
                        "unique_ratio": round(unique_ratio, 4),
                        "severity": "low"
                    })
        return issues

    # =========================
    # 5. Numeric Outliers
    # =========================
    def check_numeric_outliers(self):
        """
        Detect numeric outliers using the IQR method.
        Values outside:
            Q1 - 1.5 * IQR
            Q3 + 1.5 * IQR
        are considered statistical outliers.
        """
        issues = []
        numeric_columns = self.df.select_dtypes(include=["number"]).columns
        for column in numeric_columns:
            series = self.df[column].dropna()
            if len(series) == 0:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_mask = (series < lower_bound) | (series > upper_bound)
            outlier_count = int(outlier_mask.sum())
            if outlier_count > 0:
                outlier_ratio = outlier_count / len(series)
                issues.append({
                    "type": "numeric_outliers",
                    "column": column,
                    "count": outlier_count,
                    "ratio": round(outlier_ratio, 4),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                    "severity": "high" if outlier_ratio > 0.05 else "medium"
                })
        return issues

    # =========================
    # 6. Invalid Values
    # =========================
    def check_invalid_values(self):
        """
        Check obviously invalid numeric values.
        This is a generic check.
        It does not assume business-specific rules.
        """
        issues = []
        # Quantity should normally not be zero
        # in many transaction datasets.
        if "Quantity" in self.df.columns:
            invalid_count = int((self.df["Quantity"] == 0).sum())
            if invalid_count > 0:
                issues.append({
                    "type": "invalid_values",
                    "column": "Quantity",
                    "condition": "Quantity == 0",
                    "count": invalid_count,
                    "severity": "medium"
                })
        # UnitPrice should normally not be negative
        if "UnitPrice" in self.df.columns:
            invalid_count = int((self.df["UnitPrice"] < 0).sum())
            if invalid_count > 0:
                issues.append({
                    "type": "invalid_values",
                    "column": "UnitPrice",
                    "condition": "UnitPrice < 0",
                    "count": invalid_count,
                    "severity": "high"
                })
        return issues

    # =========================
    # 7. Run All Checks
    # =========================
    def run_all_checks(self):
        """Run all quality checks."""
        report = {
            "dataset": {
                "rows": len(self.df),
                "columns": len(self.df.columns)
            },
            "issues": []
        }

        report["issues"].extend(self.check_missing_values())
        report["issues"].extend(self.check_duplicates())
        report["issues"].extend(self.check_constant_columns())
        report["issues"].extend(self.check_high_cardinality())
        report["issues"].extend(self.check_numeric_outliers())
        report["issues"].extend(self.check_invalid_values())

        # Summary
        report["summary"] = {
            "total_issues": len(report["issues"]),
            "high": sum(1 for issue in report["issues"] if issue["severity"] == "high"),
            "medium": sum(1 for issue in report["issues"] if issue["severity"] == "medium"),
            "low": sum(1 for issue in report["issues"] if issue["severity"] == "low")
        }
        return report
