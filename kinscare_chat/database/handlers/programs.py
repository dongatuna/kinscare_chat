import json
from kinscare_chat.database.access import read_db, write_db
from kinscare_chat.database.utils import schemafy

class ProgramsDbCore:
    """
    A class to handle database operations related to programs.
    """

    @classmethod
    def add_program(cls, program_data):
        """
        Add a new program to the database.

        Returns:
        Any: The result of the database operation.
        """
        sql = schemafy(
            """
            INSERT INTO kinscare_chat.programs (program_data) VALUES (
                %s
            );
            """
        )
        json_data = json.dumps(program_data)
        return write_db.do('execute', sql=sql, data=(json_data,))

    @classmethod
    def get_all_programs(cls):
        """
        Fetches all programs from the database.

        Returns:
        list: List of programs fetched from the database.
        """
        sql = schemafy("SELECT * FROM kinscare_chat.programs;")
        return read_db.do('select', sql=sql, data=None)
