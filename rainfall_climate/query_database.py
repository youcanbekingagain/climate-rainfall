from datetime import datetime
from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


class PostgresDataHandler:
    def __init__(self):
        self.engine = self.create_engine()

    def create_engine(self):
        try:
            db_url = os.getenv("DATABASE_URL")
            engine = create_engine(db_url)
            print("Successfully connected to the database.")
            return engine
        except Exception as e:
            print(f"An error occurred while connecting to the database: {e}")
            return None

    def store_data_in_postgres(self, df, table_name="rainfall_data"):
        try:
            if self.engine:
                df.to_sql(table_name, self.engine, if_exists="append", index=False)
                print(f"Data successfully stored in {table_name} table.")
            else:
                print("Engine is not initialized. Cannot store data.")
        except Exception as e:
            print(f"An error occurred while storing data: {e}")

    def query_table(self, query_date, frequency):
        try:
            if not self.engine:
                print("Engine is not initialized. Cannot query data.")
                return None

            if frequency == "daily":
                table_name = "rainfall_data_partitioned_districts"
                query = text(
                    f"""
                    SELECT state, district, rain, tmin, tmax
                    FROM {table_name}
                    WHERE time::date = :time
                    """
                )
                params = {"time": query_date}
            elif frequency == "monthly":
                table_name = "rainfall_data_partitioned_districts_monthly"
                query = text(
                    f"""
                    SELECT state, district, year, month, rain, tmin, tmax
                    FROM {table_name}
                    WHERE year = :year AND LOWER(month) = LOWER(:month)
                    """
                )
                params = {
                    "year": query_date.year,
                    "month": query_date.strftime(
                        "%b"
                    ).lower(),  # Use lower case for matching
                }
            elif frequency == "yearly":
                table_name = "rainfall_data_partitioned_districts_yearly"
                query = text(
                    f"""
                    SELECT state, district, year, rain, tmin, tmax
                    FROM {table_name}
                    WHERE year = :year
                    """
                )
                params = {"year": query_date.year}
            else:
                raise ValueError(
                    "Invalid frequency. Choose from 'daily', 'monthly', or 'yearly'."
                )

            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                result_df = pd.DataFrame(result.fetchall(), columns=result.keys())
                # Ensure correct data types
                if "year" in result_df.columns:
                    result_df["year"] = result_df["year"].astype(int)
                if "rain" in result_df.columns:
                    result_df["rain"] = result_df["rain"].astype(float)
                if "tmin" in result_df.columns:
                    result_df["tmin"] = result_df["tmin"].astype(float)
                if "tmax" in result_df.columns:
                    result_df["tmax"] = result_df["tmax"].astype(float)

                return result_df

        except Exception as e:
            print(f"An error occurred while querying data: {e}")
            return None
