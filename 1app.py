
from flask import Flask, render_template, request, flash, session, redirect, url_for
import mysql.connector
from mysql.connector import Error
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
# from werkzeug.security import generate_password_hash, check_password_hash
import random
app = Flask(__name__)



app.secret_key = 'sri'  # Required for session management and flashing messages

# In-memory storage for registered users (for demonstration purposes)


# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Your MySQL host
            user='root',       # Your MySQL username
            password='Sri/123@',  # Your MySQL password
            database='event_management'  # Your database name
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# # Home Page
# @app.route('/home')
# def home():
#     return render_template('home.html')

# Registration Page (for normal users)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mobile = request.form['mobile']
        dob = request.form['dob']
        email = request.form['email']
        city = request.form['city']
        state = request.form['state']
        role = request.form['role']  # Assuming 'role' field exists (e.g., admin/user)

        connection = create_connection()

        if connection:
            try:
                cursor = connection.cursor()
                # Check if username already exists
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash("Username already exists.", "error")
                    return redirect(url_for('register'))

                # Insert the new user into the database
                insert_query = """INSERT INTO users (username, password, mobile, dob, email, city, state, role) 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(insert_query, (username, password, mobile, dob, email, city, state, role))
                connection.commit()

                flash("Registration successful! Please log in.", "success")
                return redirect(url_for('login'))

            except Exception as e:
                flash(f"An error occurred: {str(e)}", "error")

            finally:
                cursor.close()
                connection.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        

        connection = create_connection()

        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                # Check for valid user credentials
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()

                if user:
                    session['username'] = user['username']  # Store username in session
                    session['role'] = user['role']  # Store user role in session
                    flash("Login successful!", "success")

                    if user['role'] == 'admin':  # Redirect admins to the admin dashboard
                        return redirect(url_for('admin_dashboard'))
                    else:
                        return redirect(url_for('user_dashboard'))  # Redirect normal users to events page

                flash("Invalid username or password.", "error")

            except Exception as e:
                flash(f"An error occurred: {str(e)}", "error")

            finally:
                cursor.close()
                connection.close()

    return render_template('login.html')


@app.route('/user-dashboard')
def user_dashboard():
    # Logic for the user dashboard
    return render_template('user_dashboard.html')

@app.route('/event-handling')
def event_handling():
    # Logic for the user dashboard
    if 'username' in session:
        connection = create_connection()
        
        events_data = []  # List to hold event details

        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM events")  # Fetch all events from the database
            events_data = cursor.fetchall()  # Fetch all rows from the executed query
            
            cursor.close()
            connection.close()

        return render_template('event_handling.html', events=events_data)  # Pass events data to template
    else:
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for('login'))


# Customer Management Page Route
@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        # Insert customer information into the database
        connection = create_connection()

        if connection:
            try:
                cursor = connection.cursor()
                insert_query = """INSERT INTO customers (name, email, phone, address) VALUES (%s,%s,%s,%s)"""
                cursor.execute(insert_query, (name,email ,phone ,address))
                connection.commit()
                flash("Customer added successfully!", "success")

            except Exception as e:
                flash(f"An error occurred: {str(e)}", "error")

            finally:
                cursor.close()
                connection.close()

    # Fetch all customers from the database for display
    customers_data = []
    connection = create_connection()
    
    if connection:
      try:
          cursor=connection.cursor(dictionary=True)
          cursor.execute("SELECT * FROM customers") 
          customers_data=cursor.fetchall() 
      finally:
          cursor.close()
          connection.close()

    
    return render_template('customers.html', customers=customers_data)



# Event Details Page
@app.route('/event_details', methods=['GET', 'POST'])
def event_details():
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        organizer_name = request.form.get('organizer_name')
        address = request.form.get('address')
        event_description = request.form.get('event_description')
        location = request.form.get('location')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        event_type = request.form.get('event_type')

        # Check if all required fields are filled
        if not all([event_name, organizer_name, address, event_description, location, start_time, end_time, event_type]):
            flash("All fields are required.", "error")
            return render_template('event_details.html')

        # Insert the new event into the database
        connection = create_connection()
        
        if connection:
            try:
                cursor = connection.cursor()
                insert_query = """INSERT INTO events ( event_name, organizer_name, address, event_description, location, start_time, end_time, event_type) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(insert_query, ( event_name, organizer_name, address, event_description, location, start_time, end_time, event_type))
                connection.commit()
                # Automatically store customer information when booking an event
                user_email_query = """SELECT email FROM users WHERE username=%s"""
                cursor.execute(user_email_query,(session['username'],))
                user_email=cursor.fetchone() 
                
                if user_email is not None:
                    email=user_email[0]
                    customer_query="""INSERT INTO customers (name,email) VALUES (%s,%s) ON DUPLICATE KEY UPDATE name=%s"""
                    cursor.execute(customer_query,(session['username'],email,email)) 
                    connection.commit()

                flash("Event registered successfully!", "success")
                return redirect(url_for('ticket_booking'))  # Redirect to book tickets page

            except Exception as e:
                flash(f"An error occurred: {str(e)}", "error")
            
            finally:
                cursor.close()
                connection.close()

    return render_template('event_details.html')

# Ticket Booking Form Route
@app.route('/ticket_booking', methods=['GET', 'POST'])
def ticket_booking():
    if request.method == 'POST':
        ticket_name = request.form['ticket_name']
        quantity = int(request.form['quantity'])
        event_type = request.form['event_type']
        cash_payment = request.form['cash_payment']
        customer_name = request.form['customer_name']
        ticket_class = request.form['ticket_class']
        bank_name = request.form['bank_name']
        card_type = request.form['card_type']
        cvv_number = request.form['cvv_number']

        # Insert ticket booking details into the database
        connection = create_connection()
        # event = []
        if connection:
            cursor = connection.cursor()
            insert_query = """INSERT INTO tickets (ticket_name, quantity,
                                                    event_type,
                                                    cash_payment,
                                                    customer_name,
                                                    ticket_class,
                                                    bank_name,
                                                    card_type,
                                                    cvv_number)
                              VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(insert_query,
                           (ticket_name,
                            quantity,
                            event_type,
                            cash_payment,
                            customer_name,
                            ticket_class,
                            bank_name,
                            card_type,
                            cvv_number))
            connection.commit()

            cursor.close()
            connection.close()

            flash("Ticket booked successfully!", "success")
            return redirect(url_for('halls'))  # Redirect to admin dashboard after booking

    return render_template('ticket_booking.html')


# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():

    return render_template('admin_dashboard.html')
    


@app.route('/control-room')
def controlroom():
    # Fetch customers from the database
    connection = create_connection()
    cur = connection.cursor(dictionary=True)
    
    # Fetch all customers
    cur.execute("SELECT * FROM customers")
    customers = cur.fetchall()  # Ensure this returns a list of customer records
    
    # Fetch all halls
    cur.execute("SELECT * FROM halls")
    halls = cur.fetchall()  # Fetch all rows from the executed query
    
    # Check if halls_data is empty
    print("Halls Data:", halls)
    
    # Close cursor and connection
    cur.close()
    connection.close()

    # Pass customers and halls data to the template
    return render_template('controlroom.html', customers=customers, halls=halls)

    # return render_template('controlroom.html', customers=customers)

# @app.route('/control-room')
# def control_room():
    if 'username' in session:  # Check if the user is logged in
        # Fetch customers from the database
        connection = create_connection()
        customers = []
        halls_data = []

        if connection:
            cursor = connection.cursor(dictionary=True)

            # Fetch customers
            cursor.execute("SELECT * FROM customers")
            customers = cursor.fetchall()  # Ensure it fetches all customer records

            # Fetch halls or events
            cursor.execute("SELECT * FROM halls")
            halls_data = cursor.fetchall()  # Fetch all rows from the executed query

            cursor.close()
            connection.close()

        return render_template('control_room.html', customers=customers, events=halls_data)  # Pass data to template
    else:
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for('login'))


@app.route('/send-reminder', methods=['POST'])
def send_reminder():
    customer_id = request.form.get('customer_id')
    message = request.form.get('message')
    # Here you would implement the logic to send the reminder (e.g., email)
    print(f'Sending reminder to customer ID {customer_id}: {message}')
    return redirect(url_for('control_room'))


@app.route('/send_notification/<string:event_name>', methods=['POST'])
def send_notification(event_name):
    connection = create_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        try:
            # Step 1: Fetch the target username from the form
            target_username = request.form.get('username')  # This is the recipient username
            app.logger.info(f"Target username from form: {target_username}")

            if not target_username:
                flash("Recipient username is required to send a notification.", "error")
                return redirect(url_for('admin_dashboard'))

            # Step 2: Fetch the target user's ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (target_username,))
            recipient_user = cursor.fetchone()
            app.logger.info(f"Fetched recipient user: {recipient_user}")

            if not recipient_user:
                flash(f"User '{target_username}' not found.", "error")
                return redirect(url_for('admin_dashboard'))

            recipient_user_id = recipient_user['id']
            app.logger.info(f"Using recipient user_id: {recipient_user_id}")

            # Step 3: Fetch event ID
            cursor.execute("SELECT id FROM events WHERE event_name = %s", (event_name,))
            event = cursor.fetchone()
            app.logger.info(f"Fetched event: {event}")

            if not event:
                flash(f"Event '{event_name}' not found.", "error")
                return redirect(url_for('admin_dashboard'))

            event_id = event['id']

            # Step 4: Insert notification
            message = f"Dear {target_username} ,I kindly request you to contact 910127347486 by 5:00 PM tomorrow to discuss regarding {event_name}.Thank you for your co-operation!"
            insert_query = """INSERT INTO notifications (user_id, message, event_id) VALUES (%s, %s, %s)"""
            app.logger.info(f"Inserting notification: user_id={recipient_user_id}, event_id={event_id}, message={message}")

            cursor.execute(insert_query, (recipient_user_id, message, event_id))
            update_status_query = """UPDATE events SET status = 'Confirmed' WHERE id = %s"""
            cursor.execute(update_status_query, (event_id,))
            # Commit transaction
            connection.commit()
            flash(f"Notification sent to {target_username} for Event: {event_name}.", "success")

        except Exception as e:
            # Log the error for debugging
            app.logger.error(f"Error in send_notification: {e}")
            flash(f"An error occurred: {e}", "error")

        finally:
            # Ensure resources are cleaned up
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return redirect(url_for('admin_dashboard'))


@app.route('/notifications')
def notifications():
    if 'username' not in session:
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for('login'))
    if 'username' in session and 'username' == "admin":
        flash("You are not authorized to access this page.", "error")
        return redirect(url_for('login'))

    print(f"Session username: {session.get('username')}")  # Debugging

    connection = create_connection()
    if 'username' in session:
        try:
            cursor = connection.cursor(dictionary=True)

            # Fetch user ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user = cursor.fetchone()

            if not user:
                flash("User not found.", "error")
                return redirect(url_for('login'))

            user_id = user['id']
            print(f"User ID: {user_id}")  # Debugging

            # Fetch notifications
            cursor.execute("""
                SELECT 
                    n.message, 
                    e.event_name, 
                    n.timestamp, 
                    n.notification_type, 
                    n.is_read, 
                    n.acknowledged 
                FROM notifications n
                JOIN events e ON n.event_id = e.id
                WHERE n.user_id = %s
                ORDER BY n.timestamp DESC
            """, (user_id,))

            notifications_data = cursor.fetchall()
            print(f"Fetched notifications: {notifications_data}")  # Debugging

            return render_template('notifications.html', notifications=notifications_data)

        except Exception as e:
            print(f"Error: {e}")
            flash(f"An error occurred: {e}", "error")
        finally:
            cursor.close()
            connection.close()

    return render_template('notifications.html', notifications=[])

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'srichandanak.24@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'uteu nbjt dmch lzom'      # Use the app password generated from Google
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
s = URLSafeTimedSerializer('Thisisasecret!')  # Secret key for token 

@app.route('/send-email', methods=['POST'])
def send_email():
    subject = request.form.get('subject')
    recipient = request.form.get('recipient')
    body = request.form.get('body')

    if not (subject and recipient and body):
        return "Invalid request. Please provide subject, recipient, and body parameters."

    msg = Message(subject=subject,
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[recipient])
    msg.body = body

    try:
        mail.send(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Check if the email exists in the database
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # Generate an OTP (One-Time Password)
                otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
                
                # Store OTP in session for verification later
                session['otp'] = otp
                session['otp_email'] = email
                
                # Send OTP via email
                msg = Message('Password Reset Request',
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[email])
                msg.body = f'Your OTP for password reset is {otp}'
                mail.send(msg)
                
                flash('Check your email for the OTP to reset your password.', 'info')
                return redirect(url_for('verify_otp'))  # Redirect to OTP verification page
            else:
                flash('Email not found.', 'error')

            cursor.close()
            connection.close()
    
    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        
        if entered_otp and int(entered_otp) == session.get('otp'):
            return redirect(url_for('reset_password'))  # Redirect to reset password page
        else:
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('verify_otp.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        
        # Update the user's password in the database
        email = session.get('otp_email')  # Get email from session
        
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
            connection.commit()
            cursor.close()
            connection.close()

            flash('Your password has been updated!', 'success')
            return redirect(url_for('login'))  # Redirect to login page after resetting

    return render_template('reset_password.html')

@app.route('/halls', methods=['GET', 'POST'])
def halls():
    if request.method == 'POST':
        # Retrieve form data
        hall = request.form.get('hall')
        attendees = request.form.get('attendees')
        food = request.form.get('food')
        tech = request.form.getlist('tech[]')  # For multiple checkbox selections
        setup = request.form.getlist('setup[]')  # For setup requirements
        av = request.form.getlist('av[]')  # For audio/visual requirements
        parking = request.form.get('parking')  # For parking requirements
        artistic = request.form.get('artistic')

        # Validate and process the form data
        if not hall or not attendees or not food:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('halls'))

        # Establish a connection to the database
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            insert_query = """INSERT INTO halls (hall, attendees, food, tech, setup, av, parking, artistic, created_at)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())"""
            cursor.execute(insert_query, (hall, attendees, food, ','.join(tech), ','.join(setup), ','.join(av), parking, artistic))
            connection.commit()
            cursor.close()
            connection.close()

            flash("Ticket booked successfully!", "success")
            return redirect(url_for('user_dashboard'))  # Redirect after successful booking

    # If GET request, just render the form
    return render_template('halls.html')



if __name__ == '__main__':
    app.run(debug=True)




# from flask import Flask, render_template, request, flash, session, redirect, url_for
# import mysql.connector
# from mysql.connector import Error

# app = Flask(__name__)
# app.secret_key = 'sri'  # Replace with a secure key
# users = {}
# # Database connection function
# def create_connection():
#     try:
#         connection = mysql.connector.connect(
#             host='localhost',  # Your MySQL host
#             user='root',  # Your MySQL username
#             password='Sri/123@',  # Your MySQL password
#             database='event_management'  # Your database name
#         )
#         return connection
#     except Error as e:
#         print(f"Error: {e}")
#         return None

#  #Home Page
# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/about')
# def about():
#     return render_template('about.html')



# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         role = request.form['role']

#         # Check if username already exists in the global users dictionary
#         if username in users:
#             flash("Username already exists", "error")
#             return redirect(url_for('register'))

#         # Create a new user dictionary and add it to the dictionary
#         new_user = {
#             "password": password,  # Note: In a real application, hash the password!
#             "role": role
#         }
#         users[username] = new_user  # Use username as key

#         flash("Registration successful! Please log in.", "success")
#         return redirect(url_for('login'))

#     return render_template('register.html')

# # Login Page
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         # Check for valid user credentials
#         if username in users and users[username]['password'] == password:
#             session['username'] = username  # Store username in session
            
#             # Check if the user is an admin
#             if users[username]['role'] == 'admin':
#                 flash("Login successful! Redirecting to admin dashboard.", "success")
#                 return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            
#             flash("Login successful!", "success")
#             return redirect(url_for('event_details'))  # Redirect to home page
            
#         flash("Invalid credentials", "error")

#     return render_template('login.html')


# @app.route('/event_details', methods=['GET', 'POST'])
# def event_details():
#     if request.method == 'POST':
#         event_name = request.form.get('event_name')
#         organizer_name = request.form.get('organizer_name')
#         address = request.form.get('address')
#         event_description = request.form.get('event_description')
#         location = request.form.get('location')
#         start_time = request.form.get('start_time')
#         end_time = request.form.get('end_time')
#         event_type = request.form.get('event_type')

#         # Check if all required fields are filled
#         if not all([event_name, organizer_name, address, event_description, location, start_time, end_time, event_type]):
#             flash("All fields are required.", "error")
#             return render_template('event_details.html')

#         # Check for conflicts in the database
#         connection = create_connection()
#         conflict_found = False
#         if connection:
#             try:
#                 cursor = connection.cursor()
#                 query = """SELECT * FROM events WHERE 
#                             (start_time <= %s AND end_time >= %s) AND 
#                             event_type = %s"""
#                 cursor.execute(query, (end_time, start_time, event_type))
#                 conflict_found = cursor.fetchone() is not None  # If there's any row returned

#                 if not conflict_found:
#                     # No conflict found; insert the new event
#                     insert_query = """INSERT INTO events (event_name, organizer_name, address,
#                                                            event_description, location,
#                                                            start_time, end_time, event_type)
#                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
#                     cursor.execute(insert_query,
#                                    (event_name,
#                                     organizer_name,
#                                     address,
#                                     event_description,
#                                     location,
#                                     start_time,
#                                     end_time,
#                                     event_type))
#                     connection.commit()

#                     # Flash success message and redirect to ticket booking page
#                     flash("Event registered successfully!", "success")
#                     return redirect(url_for('ticket_booking'))  # Redirect to book tickets page
                
#                 else:
#                     flash("Can't register the event. Choose another slot.", "error")

#             except Exception as e:
#                 flash(f"An error occurred: {str(e)}", "error")
#             finally:
#                 cursor.close()
#                 connection.close()

#     return render_template('event_details.html')


# # Ticket Booking Form Route
# @app.route('/ticket_booking', methods=['GET', 'POST'])
# def ticket_booking():
#     if request.method == 'POST':
#         ticket_name = request.form['ticket_name']
#         quantity = int(request.form['quantity'])
#         event_type = request.form['event_type']
#         cash_payment = request.form['cash_payment']
#         customer_name = request.form['customer_name']
#         ticket_class = request.form['ticket_class']
#         bank_name = request.form['bank_name']
#         card_type = request.form['card_type']
#         cvv_number = request.form['cvv_number']

#         # Insert ticket booking details into the database
#         connection = create_connection()
        
#         if connection:
#             cursor = connection.cursor()
#             insert_query = """INSERT INTO tickets (ticket_name, quantity,
#                                                     event_type,
#                                                     cash_payment,
#                                                     customer_name,
#                                                     ticket_class,
#                                                     bank_name,
#                                                     card_type,
#                                                     cvv_number)
#                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
#             cursor.execute(insert_query,
#                            (ticket_name,
#                             quantity,
#                             event_type,
#                             cash_payment,
#                             customer_name,
#                             ticket_class,
#                             bank_name,
#                             card_type,
#                             cvv_number))
#             connection.commit()

#             cursor.close()
#             connection.close()

#             flash("Ticket booked successfully!", "success")
#             return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard after booking

#     return render_template('ticket_booking.html')

# # Admin Dashboard Route
# @app.route('/admin_dashboard')
# def admin_dashboard():
#     connection = create_connection()
#     events_data = []
    
#     if connection:
#         cursor = connection.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM events")
#         events_data = cursor.fetchall()  # Fetch all rows from the executed query
        
#         cursor.close()
#         connection.close()
    
#     return render_template('admin_dashboard.html', events=events_data)  # Pass events data to template

# if __name__ == '__main__':
#     app.run(debug=True)
# from flask import Flask, render_template, request, flash, session, redirect, url_for
# import mysql.connector
# from mysql.connector import Error

# app = Flask(__name__)
# app.secret_key = 'sri'  # Required for session management and flashing messages


# @app.route('/about')
# def about():
#     return render_template('about.html')
# users = {}
# # Database connection function
# def create_connection():
#     try:
#         connection = mysql.connector.connect(
#             host='localhost',  # Your MySQL host
#             user='root',       # Your MySQL username
#             password='Sri/123@',  # Your MySQL password
#             database='event_management'  # Your database name
#         )
#         return connection
#     except Error as e:
#         print(f"Error: {e}")
#         return None
    

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         role = request.form['role']

#         # Check if username already exists in the global users dictionary
#         if username in users:
#             flash("Username already exists", "error")
#             return redirect(url_for('register'))

#         # Create a new user dictionary and add it to the dictionary
#         new_user = {
#             "password": password,  # Note: In a real application, hash the password!
#             "role": role
#         }
#         users[username] = new_user  # Use username as key

#         flash("Registration successful! Please log in.", "success")
#         return redirect(url_for('login'))

#     return render_template('register.html')

# # Home Page
# @app.route('/')
# def home():
#     return render_template('home.html')

# # Admin Login Page
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         # Check for valid user credentials (only one admin)
#         if username == "admin" and password == "admin_password":  # Replace with actual admin credentials check
#             session['username'] = username  # Store username in session
#             flash("Login successful! Redirecting to admin dashboard.", "success")
#             return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            
#         flash("Invalid credentials", "error")

#         return render_template('login.html')

# @app.route('/event_details', methods=['GET', 'POST'])
# def event_details():
#     if request.method == 'POST':
#         event_name = request.form.get('event_name')
#         organizer_name = request.form.get('organizer_name')
#         address = request.form.get('address')
#         event_description = request.form.get('event_description')
#         location = request.form.get('location')
#         start_time = request.form.get('start_time')
#         end_time = request.form.get('end_time')
#         event_type = request.form.get('event_type')

#         # Check if all required fields are filled
#         if not all([event_name, organizer_name, address, event_description, location, start_time, end_time, event_type]):
#             flash("All fields are required.", "error")
#             return render_template('event_details.html')

#         # Check for conflicts in the database
#         connection = create_connection()
#         conflict_found = False
#         if connection:
#             try:
#                 cursor = connection.cursor()
#                 query = """SELECT * FROM events WHERE 
#                             (start_time <= %s AND end_time >= %s) AND 
#                             event_type = %s"""
#                 cursor.execute(query, (end_time, start_time, event_type))
#                 conflict_found = cursor.fetchone() is not None  # If there's any row returned

#                 if not conflict_found:
#                     # No conflict found; insert the new event
#                     insert_query = """INSERT INTO events (event_name, organizer_name, address,
#                                                            event_description, location,
#                                                            start_time, end_time, event_type)
#                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
#                     cursor.execute(insert_query,
#                                    (event_name,
#                                     organizer_name,
#                                     address,
#                                     event_description,
#                                     location,
#                                     start_time,
#                                     end_time,
#                                     event_type))
#                     connection.commit()

#                     # Flash success message and redirect to ticket booking page
#                     flash("Event registered successfully!", "success")
#                     return redirect(url_for('ticket_booking'))  # Redirect to book tickets page
                
#                 else:
#                     flash("Can't register the event. Choose another slot.", "error")

#             except Exception as e:
#                 flash(f"An error occurred: {str(e)}", "error")
#             finally:
#                 cursor.close()
#                 connection.close()

#     return render_template('event_details.html')



# # Ticket Booking Form Route
# @app.route('/ticket_booking', methods=['GET', 'POST'])
# def ticket_booking():
#     if request.method == 'POST':
#         ticket_name = request.form['ticket_name']
#         quantity = int(request.form['quantity'])
#         event_type = request.form['event_type']
#         cash_payment = request.form['cash_payment']
#         customer_name = request.form['customer_name']
#         ticket_class = request.form['ticket_class']
#         bank_name = request.form['bank_name']
#         card_type = request.form['card_type']
#         cvv_number = request.form['cvv_number']

#         # Insert ticket booking details into the database
#         connection = create_connection()
        
#         if connection:
#             cursor = connection.cursor()
#             insert_query = """INSERT INTO tickets (ticket_name, quantity,
#                                                     event_type,
#                                                     cash_payment,
#                                                     customer_name,
#                                                     ticket_class,
#                                                     bank_name,
#                                                     card_type,
#                                                     cvv_number)
#                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
#             cursor.execute(insert_query,
#                            (ticket_name,
#                             quantity,
#                             event_type,
#                             cash_payment,
#                             customer_name,
#                             ticket_class,
#                             bank_name,
#                             card_type,
#                             cvv_number))
#             connection.commit()

#             cursor.close()
#             connection.close()

#             flash("Ticket booked successfully!", "success")
#             return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard after booking

#     return render_template('ticket_booking.html')

# # Admin Dashboard Route
# @app.route('/admin_dashboard')
# def admin_dashboard():
#     if 'username' in session:
#         connection = create_connection()
#         appointments_data = []  # List to hold appointment details

#         if connection:
#             cursor = connection.cursor(dictionary=True)
#             cursor.execute("SELECT * FROM events WHERE status = 'Pending'")  # Fetch pending appointments
#             appointments_data = cursor.fetchall()  # Fetch all rows from the executed query
            
#             cursor.close()
#             connection.close()

#         return render_template('admin_dashboard.html', appointments=appointments_data)  # Pass appointments data to template
#     else:
#         flash("You are not authorized to access this page.", "error")
#         return redirect(url_for('login'))

# # Send Notification (for discussion about hall allocation)
# @app.route('/send_notification/<int:event_id>', methods=['POST'])
# def send_notification(event_id):
#     connection = create_connection()
    
#     if connection:
#         cursor = connection.cursor()
        
#         # Update the event status and send notification logic here (e.g., email)
#         update_query = """UPDATE events SET status = 'Confirmed' WHERE id = %s"""  # Assuming there's an ID column
#         cursor.execute(update_query, (event_id,))
        
#         connection.commit()
        
#         flash(f"Notification sent regarding hall allocation for Event ID: {event_id}.", "success")
        
#         cursor.close()
#         connection.close()

#     return redirect(url_for('admin_dashboard'))

# if __name__ == '__main__':
#     app.run(debug=True)
