from flask import Flask, render_template, request, redirect, flash, session,Response
from pymongo import MongoClient




app = Flask(__name__)

# MongoDB setup

client = MongoClient("your connection string")
db = client["atm_database"]
users_collection = db["atm_login"]




# main route also login route

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        pin = request.form['pin']  
        
        # Searching for the user id from the mongo db data base uisng find_one mehtod (only finding the preticular document from the db)

        user = users_collection.find_one({"pin": pin})
        
        if user:
            #using session

            session['pin'] = str(user['_id'])  # Store the user_id in the session
          
            return redirect('/transaction') 
        else:
           

            flash("Invalid username or ID. Please try again.", "error")
            return redirect('/login')
    
    return render_template('login.html')


# route for the register 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        pin = request.form.get('pin')
        confirm_pin = request.form.get('confirm_pin')

        # Check if the PIN and confirmation PIN match
        if pin != confirm_pin:
            flash("PINs do not match. Please try again.", "error")
            return redirect('/register')
        
       

        # Create a new user document

        new_user = {
            "name": name,
            "pin": pin,
            
        }

        # Insert into MongoDB

        try:
            users_collection.insert_one(new_user)  #insertng one document to the mongo db
            flash("Registration successful!", "success")
            return redirect('/login')
        except Exception as e:
            flash("An error occurred during registration.", "error")
            print(e)
            return redirect('/register')
    
    return render_template('register.html')



 # route for transaction 


balance = 1000

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    global balance
    if request.method == 'POST':
        transaction_type = request.form.get('transaction')
        amount_str = request.form.get('amount', '0')  
        
        # Check if the amount field is not empty, then convert it to a float
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
        elif transaction_type == 'pin_generation':
            return redirect('/register')
    
    return render_template('transaction.html')


#route for balance 

@app.route('/balance')
def balance_page():
    global balance
    return render_template('balance.html', balance=balance)

    






if __name__ == '__main__':
    app.secret_key = 'admin123'
    app.run(debug=True)
