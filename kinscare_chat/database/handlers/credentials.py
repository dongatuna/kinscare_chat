from kinscare_chat.database.access import read_db, write_db
from kinscare_chat.database.utils import schemafy

class CredentialsDbCore:
    """
    A class to handle database operations related to Facebook and Instagram credentials.
    """

    @classmethod
    def add_fb_creds(cls, user_id, access_token, token_type=None, expires_in=None):
        """
        Add Facebook credentials to the database.
        """
        sql = schemafy(
            """
            INSERT INTO kinscare_chat.fb_creds (
                user_id, access_token, token_type, expires_in
            ) VALUES (%s, %s, %s, %s)
            RETURNING id;
            """
        )
        params = (user_id, access_token, token_type, expires_in)
        return write_db.do('execute', sql=sql, data=params)

    @classmethod
    def get_fb_creds(cls, user_id):
        """
        Retrieve Facebook credentials from the database.
        """
        sql = schemafy(
            "SELECT * FROM kinscare_chat.fb_creds WHERE user_id = %s;"
        )
        return read_db.do('select_one', sql=sql, data=(user_id,))

    @classmethod
    def add_ig_creds(cls, user_id, access_token, token_type=None, expires_in=None):
        """
        Add Instagram credentials to the database.
        """
        sql = schemafy(
            """
            INSERT INTO kinscare_chat.ig_creds (
                user_id, access_token, token_type, expires_in
            ) VALUES (%s, %s, %s, %s)
            RETURNING id;
            """
        )
        params = (user_id, access_token, token_type, expires_in)
        return write_db.do('execute', sql=sql, data=params)

    @classmethod
    def get_ig_creds(cls, user_id):
        """
        Retrieve Instagram credentials from the database.
        """
        sql = schemafy(
            "SELECT * FROM kinscare_chat.ig_creds WHERE user_id = %s;"
        )
        return read_db.do('select_one', sql=sql, data=(user_id,))

# Example usage
if __name__ == "__main__":
    # Add Facebook credentials
    fb_result = CredentialsDbCore.add_fb_creds(
        user_id='12345',
        access_token='fb_access_token',
        token_type='Bearer',
        expires_in=3600
    )
    print(fb_result)

    # Retrieve Facebook credentials
    fb_creds = CredentialsDbCore.get_fb_creds(user_id='12345')
    print(fb_creds)

    # Add Instagram credentials
    ig_result = CredentialsDbCore.add_ig_creds(
        user_id='67890',
        access_token='ig_access_token',
        token_type='Bearer',
        expires_in=3600
    )
    print(ig_result)

    # Retrieve Instagram credentials
    ig_creds = CredentialsDbCore.get_ig_creds(user_id='67890')
    print(ig_creds)
