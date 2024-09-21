# EXAMPLE CODE

import json
import psycopg2
from psycopg2.extras import Json


def insert_data_to_db(json_filename):
    # Read the input JSON file
    with open(json_filename, 'r', encoding='UTF-8') as infile:
        data = json.load(infile)

    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname="your_dbname",
        user="your_user",
        password="your_password",
        host="your_host"
    )
    cur = conn.cursor()

    # Insert data into the database
    for item in data:
        cur.execute("""
            INSERT INTO kinscare_chat.programs (
                user_id, name, institution, url, description, 
                course_prerequisites, application_requirements, application_deadline, 
                number_of_annual_intakes, information_session_schedules, course_costs, 
                application_contact, average_salary, related_courses, related_courses_url
            ) VALUES (
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s
            )
        """, (
            1,  # Assuming user_id is 1 for all entries, you can adjust this accordingly
            item.get('name'),
            item.get('institution'),
            item.get('url'),
            item.get('description'),
            item.get('course_prerequisites'),
            item.get('application_requirements'),
            item.get('application_deadline'),
            item.get('number_of_annual_intakes'),
            item.get('information_session_schedules'),
            Json(item.get('course_costs')),  # Convert dict to JSONB
            Json(item.get('application_contact')),  # Convert dict to JSONB
            item.get('average_salary'),
            item.get('related_courses'),
            item.get('related_courses_url')
        ))

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()

# Example usage
#json_filename = 'data/nursing_programs/nursing_washington.json' 
# Replace with your JSON file path

#insert_data_to_db(json_filename)
