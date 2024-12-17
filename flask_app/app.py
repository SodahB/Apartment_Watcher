from flask import Flask, render_template, request, redirect
import snowflake.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Snowflake connection parameters
username = os.getenv("username")
password = os.getenv("password")
host = os.getenv("host")
warehouse = os.getenv("warehouse")
role = "USER_ADMIN_ROLE"
database = "apartment_watcher"
schema = "USERS"

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

# Home page showing subscription form
@app.route('/')
def index():
    # Define the municipalities list
    municipalities = [
        "Botkyrka", "Danderyd", "Ekero", "Haninge", "Huddinge", "Håbo",
        "Järfälla", "Lidingö", "Nacka", "Norrtälje", "Nykvarn", "Nynäshamn",
        "Salem", "Sigtuna", "Sollentuna", "Solna", "Stockholm", "Strängnäs",
        "Sundbyberg", "Södertälje", "Tyresö", "Täby", "Upplands Väsby",
        "Upplands-Bro", "Vallentuna", "Värmdö", "Österåker"
    ]
    
    # Define the apartment types list
    apartment_types = [
        'Standard', 'Youth', 'Student', 'New Development', 'Senior', 
        'Short term', 'Fast Track', 'Accessibility for Limited Mobility', 'Accessibility for Limited Orientation'
    ]
    
    # Pass both lists to the template
    return render_template('index.html', municipalities=municipalities, apartment_types=apartment_types)

# Handle form submission
@app.route('/subscribe', methods=['POST'])
def subscribe():
    # Get form data
    email = request.form['email']
    municipalities = request.form.getlist('municipality')
    accessibility = request.form.getlist('accessibility')
    balcony = 'yes' in request.form.getlist('balcony')

    # Establish Snowflake connection
    conn = get_sf_connection()
    cursor = conn.cursor()

    # Insert or update user subscription
    cursor.execute(f"SELECT * FROM user_subscriptions WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        # Update existing record
        cursor.execute("""
            UPDATE user_subscriptions
            SET municipalities = %s, accessibility = %s, balcony = %s
            WHERE email = %s
        """, (','.join(municipalities), ','.join(accessibility), balcony, email))
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO user_subscriptions (email, municipalities, accessibility, balcony)
            VALUES (%s, %s, %s, %s)
        """, (email, ','.join(municipalities), ','.join(accessibility), balcony))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
