import json
import os
import sys
import logging
from kinscare_chat.database.core import DbSession
from kinscare_chat.database.handlers.programs import ProgramsDbCore
from kinscare_chat.database.utils import schemafy
from kinscare_chat.server.serve import run_server

# Configure logging
logging.basicConfig(level=logging.INFO)


SOURCE_DIR = os.path.join(os.path.dirname(__file__), "database", "sql")
DATA_JSON_FILES = [
    "data/nursing_programs/nursing_washington.json"
]

def setup_programs():
    # TODO: use more advanced comparison to capture changes in the new file vs DB
    add_all = False
    # Fetch all programs from the database
    existing_programs = ProgramsDbCore.get_all_programs()

    if existing_programs is None:
        add_all = True

    for json_filename in DATA_JSON_FILES:
        with open(json_filename, 'r', encoding='UTF-8') as infile:
            data = json.load(infile)

        if add_all is False:
            # Validate and insert programs from JSON file
            for program in data:
                if not program_exists(program, existing_programs):
                    # Insert the program into the database
                    add_program_to_db(program)
        else:
            for program in data:
                # Insert the program into the database
                add_program_to_db(program)

def program_exists(program: dict, existing_programs) -> bool:
    """
    Check if a program already exists in the database.

    Args:
    - program (dict): Program data to check.
    - existing_programs (list of dict): 
        List of existing programs fetched from the database.

    Returns:
    bool: True if the program already exists, False otherwise.
    """
    for existing_program in existing_programs:
        if (
            program['name'] == existing_program['program_data']['name'] and
            program['institution'] == existing_program['program_data']['institution']
        ):
            return True
    return False

def add_program_to_db(program: dict):
    """
    Add a program to the database.

    Args:
    - program (dict): Program data to add.
    - db (DbSession): Database session object.
    """
    # Add program to database using ProgramsDbCore class method
    ProgramsDbCore.add_program(program)

def process_sql_file(db: DbSession, filename: str) -> None:
    """Reads an SQL file, schemafies it, and executes it on the database."""
    filepath = os.path.join(SOURCE_DIR, filename)
    try:
        with open(filepath, 'r', encoding='UTF-8') as file:
            sql = schemafy(file.read())
            db.do('execute', sql)
    except IOError as e:
        print(f"Error reading file {filename}: {e}")
        sys.exit(1)

def prepare_database(db: DbSession) -> None:
    """Prepares the database by creating a schema and processing SQL files."""
    schema_name = os.getenv('DB_SCHEMA')
    if not schema_name:
        print("Environment variable 'DB_SCHEMA' not set.")
        sys.exit(1)

    db.do('execute', f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
    for sql_file in ['schema.sql', 'migration.sql']:
        process_sql_file(db, sql_file)
    db.do('commit')

def run():
    """Main entrypoint."""
    db = DbSession('setup')
    try:
        logging.info("--- Kinscare Chat   started   ---")
        prepare_database(db)
        setup_programs()
        run_server()
    except KeyboardInterrupt:
        logging.error("Kinscare Chat interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        sys.exit(2)

if __name__ == "__main__":
    run()
