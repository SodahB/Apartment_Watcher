from dotenv import load_dotenv
import os
import snowflake.connector
from send_email import send_email

load_dotenv()

username = os.getenv("username")
password = os.getenv("password")
host = os.getenv("host")
warehouse = os.getenv("warehouse")
role = 'EMAIL_ADMIN_ROLE'
database = os.getenv("database")
schema = 'USERS'

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



def find_users():
# find active users' id:s and emails
    try:
        conn = get_sf_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM user u WHERE is_active = 1")
        users = cursor.fetchall()
        if users:
            for user in users:
                user_id, email = user
                cursor.execute(f"""SELECT * FROM user u JOIN USER_APARTMENT_TYPE_FILTERS uatf ON u.id = uatf.user_id WHERE u.id = {user_id};""")
                user_filters = cursor.fetchone()
                user_filter_dict = {
                    'min_rent': user_filters[2],
                    'max_rent': user_filters[3],
                    'min_rooms': user_filters[4],
                    'max_rooms': user_filters[5],
                    'min_size': user_filters[6],
                    'max_size': user_filters[7],
                    'balcony_required': user_filters[8],
                    'any_floor': user_filters[9],
                    'any_floor_except_bottom': user_filters[10],
                    'elevator_required': user_filters[11],
                    'bottom_floor_required': user_filters[12],
                    'bottom_or_elevator_required': user_filters[13],
                    'standard_lease': user_filters[17],
                    'youth': user_filters[18],
                    'student': user_filters[19],
                    'senior': user_filters[20],
                    'short_term': user_filters[21],
                    'youth_friendship': user_filters[22],
                    'fast_track': user_filters[23],
                    'limited_mobility': user_filters[24],
                    'limited_orientation': user_filters[25]
                }

                #create where-clauses for dynamic choices in accessibility (floor and elevator)
                if user_filter_dict['any_floor']:
                    user_filter_dict['floor_condition'] = "1=1"

                elif user_filter_dict['any_floor_except_bottom']:
                    user_filter_dict['floor_condition'] = ("ap.floor > 1")

                elif user_filter_dict['elevator_required']:
                    user_filter_dict['floor_condition'] = ("ap.elevator = 1")

                elif user_filter_dict['bottom_floor_required']:
                    user_filter_dict['floor_condition'] = ("ap.floor = 1")

                elif user_filter_dict['bottom_or_elevator_required']:
                    user_filter_dict['floor_condition'] = ("(ap.floor = 1 OR ap.elevator = 1)")
                #fallback clause
                else:
                    user_filter_dict['floor_condition'] = "2=2"

                #accessibility clause for apartment types
                if user_filter_dict['limited_mobility']:
                    user_filter_dict['mobility_condition'] = "atype.is_limited_mobility = TRUE"
                else:
                    user_filter_dict['mobility_condition'] = '1=1'

                if user_filter_dict['limited_orientation']:
                    user_filter_dict['orientation_condition'] = "atype.is_limited_orientation = TRUE"
                else:
                    user_filter_dict['orientation_condition'] = '1=1'

                if user_filter_dict['balcony_required']:
                    balcony_condition = f"ap.balcony = TRUE"
                else:
                    balcony_condition = "1=1"
                user_filter_dict['balcony_condition'] = balcony_condition

                #creating list of allowed apartment types
                apartment_type = []
                if user_filter_dict['youth']:
                    apartment_type.append('is_youth')
                if user_filter_dict['youth_friendship']:
                    apartment_type.append('is_youth_friendship')
                if user_filter_dict['student']:
                    apartment_type.append('is_student')
                if user_filter_dict['senior']:
                    apartment_type.append('is_senior')
                if user_filter_dict['short_term']:
                    apartment_type.append('is_short_term')
                if user_filter_dict['fast_track']:
                    apartment_type.append('is_fast_track')
                #fallback
                else:
                    apartment_type.append("TRUE")
                
                if 'is_standard' in apartment_type:
                    # Creating condition for 'standard' apartments where all other apartment types are false
                    other_types = ['is_youth', 'is_student', 'is_senior', 'is_short_term', 'is_fast_track', 'is_youth_friendship']
                    standard_condition = " AND ".join([f"{type} = FALSE" for type in other_types])

                    # Create condition for other apartment types, joined by OR
                    specified_types_condition = " OR ".join([f"{type} = TRUE" for type in apartment_type if type != 'is_standard'])

                    # Combinining the two conditions
                    apartment_type_condition = f"(({standard_condition}) OR ({specified_types_condition}))"
                else:
                # combining apartment types if is_standard is not in the lsit
                    apartment_type_condition = "(" + " OR ".join([f"({type} = TRUE)" for type in apartment_type]) + ")"

                user_filter_dict['apartment_type_condition'] = apartment_type_condition

                #municipality filters
                cursor.execute(f"""SELECT m.name FROM user_municipality um JOIN municipality m on um.municipality_id = m.id WHERE um.user_id = {user_id};""")
                user_municipalities= cursor.fetchall()
                user_municipalities_list = [municipality[0] for municipality in user_municipalities]
                user_municipalities_list = [municipality.replace("'", "''") for municipality in user_municipalities_list]
                municipality_condition = "lo.municipality IN (%s)" % ', '.join([f"'{municipality}'" for municipality in user_municipalities_list])
                user_filter_dict['municipality_condition'] = municipality_condition

                #send filters to search function
                search_for_filtered_ads(conn, email, user_filter_dict)

        return None

    except Exception as e:
        print(f"Error occurred while fetching user filters: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def search_for_filtered_ads(conn, email, user_filter_dict):
    try:
        cursor = conn.cursor()
        floor_condition = user_filter_dict['floor_condition']
        balcony_condition = user_filter_dict['balcony_condition']
        apartment_type_condition = user_filter_dict['apartment_type_condition']
        municipality_condition = user_filter_dict['municipality_condition']
        mobility_condition = user_filter_dict['mobility_condition']
        orientation_condition = user_filter_dict['orientation_condition']


        query = """
        SELECT * FROM WAREHOUSE.DIM_APARTMENT ap
        JOIN WAREHOUSE.fct_ad fct ON ap.id = fct.apartment_id
        JOIN WAREHOUSE.dim_apartment_type atype ON atype.id = fct.apartment_type_id
        JOIN WAREHOUSE.dim_location lo ON lo.id = fct.location_id
        JOIN WAREHOUSE.dim_ad ad ON ad.id = fct.ad_id
        WHERE fct.rent >= %s
        AND fct.rent <= %s
        AND ap.rooms >= %s
        AND ap.rooms <= %s
        AND ap.floor_area >= %s
        AND ap.floor_area <= %s
        AND {floor_condition}
        AND {balcony_condition}
        AND {apartment_type_condition}
        AND {orientation_condition}
        AND {mobility_condition}
        AND {municipality_condition}
        AND ad.published >= DATE_TRUNC('day', CURRENT_TIMESTAMP) - INTERVAL '1 day'
        """

        formatted_query = query.format(floor_condition=floor_condition, balcony_condition=balcony_condition, apartment_type_condition= apartment_type_condition, \
mobility_condition= mobility_condition, orientation_condition= orientation_condition, municipality_condition = municipality_condition)
        
        params = (
            user_filter_dict['min_rent'],
            user_filter_dict['max_rent'],
            user_filter_dict['min_rooms'],
            user_filter_dict['max_rooms'],
            user_filter_dict['min_size'],
            user_filter_dict['max_size'],
        )
        cursor.execute(formatted_query, params)
        results = cursor.fetchall()
        compose_filtered_ads(results, email)
    except Exception as e:
        print(f"Error occurred while fetching ads: {e}")
    finally:
        cursor.close()

def compose_filtered_ads(results, email):
    if results == []:
        print('No new ads for current user.')
    else:
        try:
            if not email:
                raise ValueError("Email is None or empty")
            with open("template.html", "r", encoding="utf-8") as file:
                template = file.read()
            html_rows = ""
            for apartment in results:
                special_categories = []
                accessibility = []
                if apartment[13]: special_categories.append("Youth")
                if apartment[14]: special_categories.append("Student")
                if apartment[15]: special_categories.append("Senior")
                if apartment[16]: special_categories.append("Short Term")
                if apartment[17]: special_categories.append("Youth Friendship")
                if apartment[18]: special_categories.append("Fast Track")
                if apartment[19]: accessibility.append("For Limited Mobility")
                if apartment[20]: accessibility.append("For Limited Orientation")
                
                row = f"""
                <tr>
                    <td>{apartment[24]}</td>
                    <td>{apartment[11]} SEK/month</td>
                    <td>{apartment[2]}</td>
                    <td>{apartment[3]} m²</td>
                    <td>{apartment[22]}</td>
                    <td>{apartment[23]}</td>
                    <td>{", ".join(special_categories) if special_categories else "Standard"}</td>
                    <td>{", ".join(accessibility) if accessibility else "None"}</td>
                    <td>{apartment[31]}</td>
                    <td>{apartment[32]}</td>
                    <td><a href="https://bostad.stockholm.se{apartment[29]}">View Details</a></td>
                </tr>
                """
                html_rows += row
            final_html = template.replace("{rows}", html_rows)

            if not final_html:
                raise ValueError("Final HTML content is None or empty")
            
            send_email(email, final_html)

        except Exception as e:
            print(f"Error occurred while composing html: {e}")


if __name__ == '__main__':
    find_users()

    
