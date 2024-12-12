class QueryGenerator:
    """
    A helper class to generate SQL queries for MindsDB Actions.
    """

    @staticmethod
    def create_database_query(database_name: str, engine: str, parameters: dict) -> str:
        """
        Generate a CREATE DATABASE query with the given parameters.

        :param database_name: The name of the database to create.
        :param engine: The database engine to use.
        :param parameters: A dictionary of parameters for the engine.
        :return: The generated SQL query as a string.
        """
        parameter_str = ",\n  ".join(
            [f'"{key}": "{value}"' if isinstance(value, str) else f'"{key}": {value}' for key, value in parameters.items()]
        )
        return f"""CREATE DATABASE {database_name}
                    WITH ENGINE = '{engine}',
                        PARAMETERS = {{
                        {parameter_str}
                    }};"""

    @staticmethod
    def create_ml_engine_query(ml_engine_name: str, engine: str, parameters: dict) -> str:
        """
        Generate a CREATE ML ENGINE query with the given parameters.

        :param ml_engine_name: The name of the ML Engine to create.
        :param engine: The ML Engine to use.
        :param parameters: A dictionary of parameters for the engine.
        :return: The generated SQL query as a string.
        """
        # Handle empty parameters gracefully
        parameters = parameters or {}
        parameter_str = ",\n  ".join([f"{key} = '{value}'" for key, value in parameters.items()])
        using_clause = f"\nUSING\n\t{parameter_str};" if parameters else ""

        return f"""CREATE ML_ENGINE {ml_engine_name}
                        FROM {engine}{using_clause};
                    """

    @staticmethod
    def create_model(model_name: str, target_var: str, parameters: dict) -> str:
        """
        Generate a CREATE MODEL query with the given parameters.

        :param model_name: The name of the model to create.
        :param target_var: The target variable to predict.
        :param parameters: A dictionary of parameters for the model.
        :return: The generated SQL query as a string.
        """
        parameter_str = ",\n  ".join([f'"{key}": "{value}"' for key, value in parameters.items()])
        return f"""CREATE MODEL {model_name}
                PREDICT {target_var}
                USING
                    {parameter_str}
                ;"""

    @staticmethod
    def simple_select_query(table_name: str, columns: list = None, limit: int = 10) -> str:
        """
        Generate a simple SELECT query with the given parameters.

        :param table_name: The name of the table to query.
        :param columns: A list of columns to SELECT.
        :param limit: The number of rows to LIMIT the query to.
        :return: The generated SQL query as a string.
        """
        columns = columns or ["*"]  # Default to selecting all columns if not specified
        column_str = ", ".join(columns)
        limit_str = f" LIMIT {limit}" if limit else ""
        return f"""SELECT {column_str} FROM {table_name}{limit_str};"""
