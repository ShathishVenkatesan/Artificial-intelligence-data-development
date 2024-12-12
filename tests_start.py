from locust import between, HttpUser
from tests.load.test_postgresql import PostgreSQLConnectionBehavior
from tests.utils.config import get_value_from_json_env_var

from mindsdb.utilities import log

logger = log.getLogger(__name__)

class DBConnectionUser(HttpUser):
    tasks = [PostgreSQLConnectionBehavior]
    wait_time = between(5, 15)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load configuration for MindsDB Cloud
        self.config = self.load_config()

        if self.config:
            try:
                # Attempt to login to MindsDB
                response = self.client.post('/cloud/login', json={
                    'email': self.config['user'],
                    'password': self.config['password']
                })
                response.raise_for_status()
                logger.info('Successfully logged into MindsDB Cloud.')
            except Exception as e:
                logger.error(f'Logging into MindsDB failed: {e}')
        else:
            logger.error("MindsDB Cloud configuration not found, cannot proceed with login.")

    def load_config(self):
        """
        Loads configuration from the environment variable or settings file.
        Returns None if configuration is not found.
        """
        try:
            return get_value_from_json_env_var("INTEGRATIONS_CONFIG", "mindsdb_cloud")
        except KeyError as e:
            logger.error(f"Configuration missing for 'mindsdb_cloud': {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading MindsDB configuration: {e}")
            return None
