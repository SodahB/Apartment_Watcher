import snowflake.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Snowflake connection parameters
username = os.getenv("username")
password = os.getenv("password")
host = os.getenv("host")
warehouse = os.getenv("warehouse")
role = "USER_ADMIN_ROLE"
database = "apartment_watcher"
schema = "USERS"

if not all([username, password, host, warehouse, database, schema]):
    raise ValueError("Some environment variables are missing.")



# Connect to Snowflake
def get_sf_connection():
    conn = snowflake.connector.connect(
        user=username,
        password=password,
        account=host,
        warehouse=warehouse,
        database=database,
        schema=schema,
        role=role
    )
    return conn



def update_subscription(user_preferences, selected_apartment_types, user_municipalities_ids):

# Establish Snowflake connection
    try:
        conn = get_sf_connection()
        cursor = conn.cursor()

        cursor.execute("BEGIN")
        
        # Insert or update user subscription
        cursor.execute("""
            SELECT id FROM user WHERE email = %s
        """, (user_preferences['email'],))
        
        user = cursor.fetchone()
        if user:
            print("User exists. Proceeding...")
            # Update existing user

            #user table
            print("Updating user table.")
            cursor.execute("""
                UPDATE user
                SET email = %(email)s, 
                    min_rent = %(min_rent)s, 
                    max_rent = %(max_rent)s, 
                    min_rooms = %(min_rooms)s, 
                    max_rooms = %(max_rooms)s, 
                    min_size = %(min_size)s, 
                    max_size = %(max_size)s, 
                    balcony_required = %(balcony_required)s, 
                    any_floor = %(any_floor)s, 
                    any_floor_except_bottom = %(any_floor_except_bottom)s, 
                    elevator_required = %(elevator_required)s, 
                    bottom_floor_required = %(bottom_floor_required)s, 
                    bottom_or_elevator_required = %(bottom_or_elevator_required)s
                WHERE email = %(email)s
            """, user_preferences)

            #fetch existing user's id
            user_id = user[0]
            selected_apartment_types['user_id'] = user_id

            # Update the user_apartment_type_filters table if the user exists
            print("Updating filtering table.")
            cursor.execute("""
                UPDATE user_apartment_type_filters
                SET new_development = %(New Development)s, 
                    standard_lease = %(Standard)s, 
                    youth = %(Youth)s, 
                    student = %(Student)s, 
                    senior = %(Senior)s, 
                    short_term = %(Short term)s, 
                    youth_friendship = %(Youth Friendship)s, 
                    fast_track = %(Fast Track)s, 
                    limited_mobility = %(Accessibility for Limited Mobility)s, 
                    limited_orientation = %(Accessibility for Limited Orientation)s
                WHERE user_id = %(user_id)s
            """, selected_apartment_types)

            #Update the municipalities if the user exists
            print("Updating municipality table.")
            # deleting existing municipalities to overwrite with new ones
            cursor.execute("""
                DELETE FROM user_municipality
                WHERE user_id = %s
            """, (user_id,))
            
            # inserting many through creating tuples
            values = [(user_id, municipality_id) for municipality_id in user_municipalities_ids]
            cursor.executemany("""
                INSERT INTO user_municipality(user_id, municipality_id)
                VALUES (%s, %s)
            """, values) 

        else:
            # Insert new user
            print("User does not exist. Proceeding...")
            #user table
            print("Updating user table.")
            cursor.execute("""
                INSERT INTO user(
                    email, min_rent, max_rent, min_rooms, max_rooms, min_size, max_size,
                    balcony_required, any_floor, any_floor_except_bottom, elevator_required,
                    bottom_floor_required, bottom_or_elevator_required
                )
                VALUES (%(email)s, %(min_rent)s, %(max_rent)s, %(min_rooms)s, %(max_rooms)s, %(min_size)s, %(max_size)s,
                        %(balcony_required)s, %(any_floor)s, %(any_floor_except_bottom)s, %(elevator_required)s,
                        %(bottom_floor_required)s, %(bottom_or_elevator_required)s)
            """, user_preferences)
            cursor.execute("SELECT MAX(id) FROM user")
            user_id = cursor.fetchone()[0]

            if user_id is None:
                print("Error: user_id is NULL!")
            selected_apartment_types['user_id'] = user_id
        
            #user_apartment_type_filters table
            print("Updating filtering table.")
            cursor.execute("""
                INSERT INTO user_apartment_type_filters (
                    user_id, new_development, standard_lease, youth, student, senior, short_term,
                    youth_friendship, fast_track, limited_mobility, limited_orientation
                )
                VALUES (%(user_id)s, %(New Development)s, %(Standard)s, %(Youth)s, %(Student)s, %(Senior)s, %(Short term)s,
                        %(Youth Friendship)s, %(Fast Track)s, %(Accessibility for Limited Mobility)s, %(Accessibility for Limited Orientation)s)
            """, selected_apartment_types)

            print("Updating municipality table.")
            #user municipality table
            for municipality_id in user_municipalities_ids:
                cursor.execute("""
                    INSERT INTO user_municipality(
                        user_id, municipality_id
                    )
                    VALUES (%(user_id)s, %(municipality_id)s)
                """, {"user_id": user_id, "municipality_id": municipality_id})


                
        conn.commit()
        print("Success, changes commited.")

    #catch errors and roll back if something is unsuccessful
    except Exception as e:
        print(f"Error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()