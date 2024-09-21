import json
from kinscare_chat.database.access import read_db, write_db
from kinscare_chat.database.utils import schemafy

class UsersDbCore:
    """
    A class to handle database operations related to users.
    """

    @classmethod
    def update_setting(cls, user_id: int, new_settings: dict):
        """
        Update the settings of a user account. Merges the new settings with the existing ones.
        If the user_id does not have an entry, inserts a new one.

        Returns:
        Any: The result of the database operation.
        """
        # Check if the user exists
        check_sql = schemafy(
            """
            SELECT settings FROM kinscare_chat.users WHERE user_id = %s;
            """
        )
        existing_settings = read_db.do('fetchone', sql=check_sql, data=(user_id,))

        if existing_settings:
            # Merge the new settings with the existing ones
            update_sql = schemafy(
                """
                UPDATE kinscare_chat.users 
                SET settings = settings || %s 
                WHERE user_id = %s;
                """
            )
            json_data = json.dumps(new_settings)
            return write_db.do('execute', sql=update_sql, data=(json_data, user_id))
        else:
            # Insert new user settings
            insert_sql = schemafy(
                """
                INSERT INTO kinscare_chat.users (user_id, settings)
                VALUES (%s, %s);
                """
            )
            json_data = json.dumps(new_settings)
            return write_db.do('execute', sql=insert_sql, data=(user_id, json_data))

    @classmethod
    def get_settings(cls, user_id: int) -> dict:
        """
        Retrieve the settings of a user account.

        Returns:
        dict: The settings of the user account.
        """
        sql = schemafy(
            """
            SELECT settings FROM kinscare_chat.users WHERE user_id = %s;
            """
        )
        result = read_db.do('select_one', sql=sql, data=(user_id,))
        if result:
            return result['settings']
        return {}
