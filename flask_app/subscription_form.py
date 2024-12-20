from flask import Flask, render_template, request, redirect, flash
from .update_subscription import update_subscription
from dotenv import load_dotenv
import os



app = Flask(__name__)

load_dotenv()
secret_key = os.getenv("secret_key")
app.secret_key = secret_key


# Home page showing subscription form
@app.route('/')
def index():
    # Define the municipalities list
    municipalities= [
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
    try:
        #create dictionary for storing values, with some defaults
        user_preferences = {"any_floor": False, "any_floor_except_bottom": False, "elevator_required" :False,
    "bottom_floor_required": False, "bottom_or_elevator_required": False}
        # Get form data for user table
        user_preferences["email"] = request.form.get('email', '')
        if not user_preferences["email"]:
            flash('Email is required.', 'error')
            return redirect('/')
        user_preferences["min_rent"] = request.form['min_rent']
        user_preferences["max_rent"] = request.form['max_rent']
        user_preferences["min_rooms"] = request.form['min_rooms']
        user_preferences["max_rooms"] = request.form['max_rooms']
        user_preferences["min_size"] = request.form['min_size']
        user_preferences["max_size"] = request.form['max_size']
        user_preferences["balcony_required"] = 'balcony_required' in request.form.getlist('balcony')
        accessibility_and_floor = request.form['accessibility_and_floor']
        user_preferences[accessibility_and_floor] = True

        
        #define and get form data for filter table
        user_apartment_types = {
        'Standard': False,
        'Youth': False,
        'Student': False,
        'New Development': False,
        'Senior': False,
        'Short term': False,
        'Fast Track': False,
        'Accessibility for Limited Mobility': False,
        'Accessibility for Limited Orientation': False
        }
        
        selected_apartment_types = request.form.getlist('apartment_types')
        for type in user_apartment_types:
            if type in selected_apartment_types:
                user_apartment_types[type] = True

        if 'Youth' in selected_apartment_types:
            user_apartment_types["Youth Friendship"] = True
        else:
            user_apartment_types["Youth Friendship"] = False

        #define and get form data for municipality table
        municipality_ids = {
        "Botkyrka": 1, "Danderyd": 2, "Ekero": 3, "Haninge": 4, "Huddinge": 5, "Håbo": 6,
        "Järfälla": 7, "Lidingö": 8, "Nacka": 9, "Norrtälje": 10, "Nykvarn": 11, "Nynäshamn": 12, "Salem": 13,
        "Sigtuna": 14, "Sollentuna": 15, "Solna": 16, "Stockholm": 17, "Strängnäs": 18, "Sundbyberg": 19, "Södertälje": 20,
        "Tyresö": 21, "Täby": 22, "Upplands Väsby": 23, "Upplands-Bro": 24, "Vallentuna": 25,
        "Värmdö": 26, "Österåker": 27}

        
        user_municipalities = request.form.getlist('municipality')
        user_municipalities_ids = []
        for municipality in user_municipalities:
            user_municipalities_ids.append(municipality_ids[municipality])


        print("Calling update_subscription...")
        update_subscription(user_preferences, user_apartment_types, user_municipalities_ids)

        flash('Subscription updated successfully!', 'success')
        return redirect('/')
    
    except Exception as e:
        print(f"Error occurred in subscribe route: {e}")
        flash('An error occurred. Please try again.', 'error')

if __name__ == '__main__':
    app.run(debug=True)
