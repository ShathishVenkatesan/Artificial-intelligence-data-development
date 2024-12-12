from tests.load.tasks import BaseDBConnectionBehavior
import json


class PostgreSQLConnectionBehavior(BaseDBConnectionBehavior):
    """
    This class defines the behavior of a PostgreSQL connection.
    @TODO: Read query values from sql_queries.json file
    """
    db_type = "postgres"
    table_name = "solar_flare_data"
    
    # Loading queries from sql_queries.json file
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.native_queries = self.load_sql_queries()

    def load_sql_queries(self):
        try:
            # Load queries from sql_queries.json
            with open('path_to_your_sql_queries.json', 'r') as f:
                queries = json.load(f)
            return queries
        except Exception as e:
            logger.error(f"Error loading SQL queries: {e}")
            return []

    def get_native_query(self, query_name):
        """
        Fetches the appropriate query string by query name.
        """
        return self.native_queries.get(query_name, f"Query '{query_name}' not found.")
    
    # Example of query usage with the dynamic table_name
    native_query_aggregation = f"SELECT COUNT(*) AS total_flares FROM tests.{table_name};"
    native_query_average = f"SELECT AVG(peak_c_per_s) AS avg_peak_counts FROM tests.{table_name};"
    native_query_max = f"SELECT MAX(energy_kev) AS max_energy FROM tests.{table_name};"
    native_query_grouping = f"SELECT active_region_ar, COUNT(*) AS flare_count  FROM tests.{table_name} GROUP BY active_region_ar;"

    @task
    def run_native_query(self):
        """This task runs a native DB select query."""
        for n_query in self.native_queries:
            query = self.get_native_query(n_query)
            self.__post_query(query)
