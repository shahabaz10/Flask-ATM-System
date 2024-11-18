from flask import Flask, render_template, request, redirect, flash, session
from pymongo import MongoClient
from bson import ObjectId


app = Flask(__name__)

# MongoDB setup
client = MongoClient("localhost:27017")
db = client["atm_database"]
users_collection = db["atm_login"]

# Main route (Login)
@app.route('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pin = request.form['pin']
        user = users_collection.find_one({"pin": pin})
        
        if user:
            session['pin'] = str(user['_id'])  # Store user ID in session
            return redirect('/transaction')
        else:
            flash("Invalid PIN. Please try again.", "error")
            return redirect('/login')
    
    return render_template('login.html')


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        pin = request.form.get('pin')
        confirm_pin = request.form.get('confirm_pin')

        if pin != confirm_pin:
            flash("PINs do not match. Please try again.", "error")
            return redirect('/register')

        new_user = {
            "name": name,
            "pin": pin,
        }

        try:
            users_collection.insert_one(new_user)
            flash("Registration successful!", "success")
            return redirect('/login')
        except Exception as e:
            flash("An error occurred during registration.", "error")
            print(e)
            return redirect('/register')

    return render_template('register.html')

# Initialize the balance variable
balance = 1000

# Transaction route (for deposit, withdraw, balance check, and change PIN)
@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    global balance  # Declare balance as a global variable
    if request.method == 'POST':
        transaction_type = request.form.get('transaction')
        amount_str = request.form.get('amount', '0')  
        amount = float(amount_str) if amount_str else 0.0

        if transaction_type == 'balance':
            return redirect('/balance')
        elif transaction_type == 'deposit':
            balance += amount
            flash(f'Deposited ${amount:.2f} successfully!', 'success')
            return redirect('/balance')
        elif transaction_type == 'withdraw':
            if amount <= balance:
                balance -= amount
                flash(f'Withdrew ${amount:.2f} successfully!', 'success')
            else:
                flash('Insufficient balance!', 'error')
            return redirect('/balance')
        elif transaction_type == 'change':
            return redirect('/change')  # Redirect to change PIN page

    return render_template('transaction.html')

# Balance route (check balance)
@app.route('/balance')
def balance_page():
    global balance  # Declare balance as a global variable
    return render_template('balance.html', balance=balance)

# Change PIN route (add this route)

@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        # Debugging to see if the form data is being received
        print(f"Form data received: {request.form}")  # Debugging line

        current_pin = request.form['current_pin']
        new_pin = request.form['new_pin']
        confirm_new_pin = request.form['confirm_new_pin']

        # Retrieve user info from MongoDB
        user_id = session.get('pin')
        if not user_id:
            flash("You need to log in first.", "error")
            return redirect('/login')

        user = users_collection.find_one({"_id": ObjectId(user_id)})

        if not user:
            flash("User not found.", "error")
            return redirect('/login')

        # Check if current PIN matches
        if user['pin'] != current_pin:
            flash("Current PIN is incorrect.", "error")
            return render_template('change_pin.html')

        # Check if the new PIN and confirm PIN match
        if new_pin != confirm_new_pin:
            flash("New PINs do not match.", "error")
            return render_template('change.html')

        # Update the PIN in MongoDB
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"pin": new_pin}})
        flash("PIN successfully changed.", "success")
        return redirect('/transaction')

    return render_template('change.html')


if __name__ == '__main__':
    app.secret_key = 'admin123'  # Ensure this key is set
    app.run(debug=True)
