from locust import SequentialTaskSet, task, events
from tests.utils.query_generator import QueryGenerator as query
from tests.utils.config import get_value_from_json_env_var, generate_random_db_name

from mindsdb.utilities import log

logger = log.getLogger(__name__)

class BaseDBConnectionBehavior(SequentialTaskSet):
    def on_start(self):
        """This method is called once for each user when they start."""
        self.query_generator = query()
        self.random_db_name = generate_random_db_name(f"{self.db_type}_datasource")
        self.create_new_datasource()

    def __post_query(self, query):
        """Helper method to send a query and handle the response."""
        try:
            response = self.client.post('/api/sql/query', json={'query': query})
            response.raise_for_status()  # Raise exception for HTTP errors
            response_data = response.json()
            
            # Check if the response is valid
            if response_data.get('type') == 'error':
                raise ValueError(f"Query error: {response_data.get('error_message')}")
            
            return response_data
        except Exception as e:
            logger.error(f'Error running query "{query}": {e}')
            events.request.fire(
                request_type="POST",
                name="/api/sql/query",
                response_time=0,
                response_length=0,
                exception=e
            )
            self.interrupt(reschedule=True)  # Interrupt task and reschedule

    def create_new_datasource(self):
        """Creates a new data source for the test."""
        try:
            db_config = get_value_from_json_env_var("INTEGRATIONS_CONFIG", self.db_type)
            create_db_query = self.query_generator.create_database_query(
                self.random_db_name,
                self.db_type,
                db_config
            )
            self.__post_query(create_db_query)  # Send query to create the database
        except Exception as e:
            logger.error(f"Error creating new datasource: {e}")
            events.request.fire(
                request_type="POST",
                name="create_database",
                response_time=0,
                response_length=0,
                exception=e
            )

    @task
    def select_integration_query(self):
        """Performs a SELECT query from the newly created integration."""
        query = f'SELECT * FROM {self.random_db_name}.{self.table_name} LIMIT 10'
        self.__post_query(query)  # Send SELECT query

    @task
    def run_native_query(self):
        """Runs a native DB select query."""
        for n_query in self.native_queries:
            query = f'SELECT * FROM {self.random_db_name}( {n_query})'
            self.__post_query(query)  # Send each native query
