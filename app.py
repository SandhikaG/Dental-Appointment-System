from flask import *
import mysql.connector 
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from MySQLdb import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sandhika'
app.config['MYSQL_DB'] = 'doctor'

DOCTOR_ROLE='dr'
PATIENT_ROLE='p'
SUPERADMIN='super'
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        auth_plugin='mysql_native_password'
    )

@app.route("/")
def main():
    session['loggedin']=False
    return render_template('main.html')

@app.route("/logout")
def logout():
   session.pop("username",None)
   session.pop("password",None)
   session['loggedin']=False
   return redirect("/")



   

  #DOCTOR

@app.route("/login.html", methods=['GET', 'POST'])
def logindr():
    if request.method == 'POST' and 'Email' in request.form and 'Password' in request.form:
        email = request.form['Email']
        password = request.form['Password']
        dbconn = get_db_connection()  # Establish the connection
        cursor = dbconn.cursor()
        cursor.execute('SELECT * FROM doctorlogin WHERE Email = %s', (email,))
        account = cursor.fetchone()
        if account:
            if account and check_password_hash(account[2], password):
                session['loggedin'] = True
                session['Email'] = account[1]
                msg="Login Successful"
                return render_template('drdash.html',msg=msg)
            else:
                msg = 'Incorrect email/password!'
                return render_template('login.html', msg=msg)
        else:
            msg="Account not found.Signup first."
            return render_template('singup.html', msg=msg)
    return render_template('login.html')

@app.route('/singup.html', methods=['GET', 'POST'])
def signupdr():
    if request.method == 'POST' and 'Email' in request.form and 'Password' in request.form:
        email = request.form['Email']
        password = generate_password_hash(request.form['Password'])
        dbconn = get_db_connection()  # Establish the connection
        cursor = dbconn.cursor()
        cursor.execute('SELECT * FROM doctorlogin WHERE Email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
            return render_template('singuppt.html', msg=msg)
        else:
            if email in ("sujilin.jesica@msds.christuniversity.in","sandhika.g@msds.chrisyuniversity.in","ellurisri.lakshmi@msds.christuniversity.in"):
                cursor.execute('INSERT INTO doctorlogin (Email,Password) VALUES (%s, %s)', (email, password))
                dbconn.commit()
                msg = 'You have successfully registered!'
                return render_template('login.html', msg=msg)
            else:
                msg = 'Cannot Signup.Only Toothsy approved Dentists can signup.'
                return render_template('singup.html', msg=msg)
        return  render_template('login.html', msg=msg)
    return render_template('singup.html')

@app.route("/forget_password")
def forget_password():
    return render_template("forget_password.html")

@app.route("/reset_password", methods=["POST"])
def reset_password():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    # Check if the email exists in the database
    dbconn=get_db_connection()
    cursor=dbconn.cursor()
    cursor.execute('SELECT * FROM doctorlogin WHERE Email = %s', (email,))
    account = cursor.fetchone()

    if account:
        if password == confirm_password:
            # Hash the password for security
            hashed_password = generate_password_hash(password)
            cursor.execute("UPDATE doctorlogin SET Password = %s WHERE Email = %s", (hashed_password, email))
            dbconn.commit()  # Commit the transaction
            cursor.close()
            msg = "Password reset successful!"
            return render_template('login.html', msg=msg)
        else:
            msg = "Re-entered password does not match the new password."
            return render_template("forget_password.html", msg=msg)
    else:
        msg = "Given email is not yet registered with Toothsy. Please sign up first."
        return render_template('singup.html', msg=msg)

@app.route('/drdash.html', methods=['GET'])
def doctor_dashboard():
    try:
        dbconn = get_db_connection()  # Establish the connection
        cursor = dbconn.cursor()
        filter_date = request.args.get('filter_date')
        
        if filter_date:
            cursor.execute("SELECT * FROM app WHERE date = %s ORDER BY time", (filter_date,))
        else:
            cursor.execute("SELECT * FROM app ORDER BY date, time")
        
        appointments = cursor.fetchall()
        cursor.close()
        
        return render_template('drdash.html', appointments=appointments, filter_date=filter_date)
    except Exception as e:
        return str(e)
@app.route('/videoconsult.html')
def video_consulting():
    try:
        filter_date = request.args.get('filter_date')
        dbconn=get_db_connection()
        cursor=dbconn.cursor()
        
        if filter_date:
            query = "SELECT * FROM bookings WHERE date = %s ORDER BY time"
            cursor.execute(query, (filter_date,))
        else:
            query = "SELECT * FROM bookings ORDER BY date, time"
            cursor.execute(query)
        
        bookings = cursor.fetchall()
        cursor.close()
        return render_template('videoconsult.html', bookings=bookings, filter_date=filter_date)
    except Error as e:
        return f"An error occurred: {e}"
    
@app.route('/patients.html')
def patients():
    try:
        dbconn = get_db_connection()  # Establish the connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT Sno, name,phone FROM app ORDER BY name")
        appointments = cursor.fetchall()
        cursor.close()
        return render_template('patients.html', appointments=appointments)
    except Exception as e:
        error_msg = f"Error fetching appointments: {str(e)}"
        print(error_msg)  # Print the error message for debugging
        return render_template('patients.html', appointments=[], error=error_msg)

@app.route('/launch.html', methods=['GET', 'POST'])
def launch():
    if request.method == 'POST':
        
            product_name = request.form['proname']
            product_desc = request.form['prodesc']
            product_price = request.form['price']
            product_image = request.files['pic']
            photofilename = product_image.filename
            image_path = 'static/'+photofilename
            product_image.save(image_path)

            dbconn = get_db_connection()
            cursor = dbconn.cursor()
            cursor.execute(
                "INSERT INTO products (name, description, price, image_url) VALUES (%s, %s, %s, %s);",
                (product_name, product_desc, product_price, image_path)
            )
            dbconn.commit()
            cursor.close()
            dbconn.close()
            msg = "Product added successfully!"
            return redirect("/launch")
    return render_template("launch.html")

@app.route("/launch")
def l():
    msg= "Product added successfully!"
    return render_template("launch.html",msg=msg)


@app.route("/ordersdisplay")
def display():
    status="Delivered"
    dbconn=get_db_connection()
    cursor = dbconn.cursor()
    cursor.execute("select order_id,phone,product_id,status from orders where status!=%s",(status,))
    orders=cursor.fetchall()
    return render_template("order.html",orders=orders)

@app.route("/shipped", methods=['GET', 'POST'])
def shipped():
    order_id = int(request.args.get('order_id'))
    msg = ''
    dbconn=get_db_connection()
    cursor = dbconn.cursor()
    status = "shipped"
    cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s;", (status, order_id))
    dbconn.commit()  
    cursor.close()
    msg = "Updation successful"
    return msg

@app.route("/delivered", methods=['GET', 'POST'])
def delivered():
    order_id = int(request.args.get('order_id'))
    msg = ''
    status = "Delivered"  
    dbconn=get_db_connection()
    cursor = dbconn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s;", (status, order_id))
    dbconn.commit()  
    cursor.close()
    msg = "Order status updated to delivered successfully."
    
    return msg

#PATIENT

@app.route("/loginp.html", methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        dbconn=get_db_connection()
        cursor =dbconn.cursor()
        cursor.execute('SELECT * FROM usertable WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            if account and check_password_hash(account[2], password):
                session['loggedin'] = True
                session['email'] = account[1]
                msg="login successful"
                return render_template('home.html',msg=msg)
            else:
                msg = 'Incorrect email/password!'
                return render_template('loginp.html', msg=msg)
        else:
            msg="Account not found.Signup first."
            return render_template('singuppt.html', msg=msg)
    return render_template('loginp.html')

@app.route('/singuppt.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            msg = "Re-entered password does not match."
            return render_template('singuppt.html', msg=msg)
        hashed_password = generate_password_hash(password)
        dbconn=get_db_connection()
        cursor = dbconn.cursor()
        cursor.execute('SELECT * FROM usertable WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        else:
            cursor.execute('INSERT INTO usertable (email, password) VALUES (%s, %s)', (email, hashed_password))
            dbconn.commit()
            msg = 'You have successfully registered!'
            return render_template('loginp.html', msg=msg)
        return render_template('singuppt.html', msg=msg)
    return render_template('singuppt.html')


@app.route("/forget_password_p")
def forget_password_p():
    return render_template("forget_password_p.html")



@app.route("/reset_password_p", methods=["POST"])
def reset_password_p():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    # Check if the email exists in the database
    dbconn=get_db_connection()
    cursor = dbconn.cursor()
    cursor.execute('SELECT * FROM usertable WHERE Email = %s', (email,))
    account = cursor.fetchone()

    if account:
        if password == confirm_password:
            # Hash the password for security
            hashed_password = generate_password_hash(password)
            cursor.execute("UPDATE usertable SET Password = %s WHERE Email = %s", (hashed_password, email))
            dbconn.commit()  # Commit the transaction
            cursor.close()
            msg = "Password reset successful!"
            return render_template('loginp.html', msg=msg)
        else:
            msg = "Re-entered password does not match the new password."
            return render_template("forget_password_p.html", msg=msg)
    else:
        msg = "Given email is not yet registered with Toothsy. Please sign up first."
        return render_template('singuppt.html', msg=msg)

@app.route("/home.html")
def h():
    return render_template('home.html')


@app.route("/consultation.html", methods=['GET', 'POST'])
def consultation():
    if request.method == 'POST':
        name = request.form.get('Name')
        age = request.form.get('Age')
        Address = request.form.get('Address')
        phone = request.form.get('Phone')
        time = request.form.get('time')
        date = request.form.get('date')
        problem = request.form.get("problem")
        email = session['email']
        # Debugging: Print values
        
        if not Address:
            return "<script>alert('Address is required. Please fill in the address field.'); window.history.back();</script>"

        dbconn = get_db_connection()  # Establish the connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT * FROM app WHERE date = %s AND time = %s", (date, time))
        result = cursor.fetchone()

        if result:
            return "<script>alert('Sorry, this time slot is already reserved. Please choose another time.'); window.history.back();</script>"
        else:    
            cursor.execute(
                "INSERT INTO app (name, age, address, phone, time, date, msg, problem) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (name, age, Address, phone, time, date, email, problem)
            )
            dbconn.commit()

            send_email(email)
            msg="Your appointment has been booked. For further details, please refer to the email sent."

            return render_template("success.html",message=msg)
        return render_template('home.html')

    return render_template('consultation.html')

def send_email(email):
    sender_email = 'sandhikagovindaraj@gmail.com'
    recipient_email = email # Assuming the email provided by the user is their email address
    subject = 'Appointment Confirmation'
    body = 'Your appointment with Toothsy has been successfully scheduled.'

    # Create a MIMEText object
    email_message = MIMEText(body)
    email_message['Subject'] = subject
    email_message['From'] = sender_email
    email_message['To'] = recipient_email

    # Connect to the SMTP server and send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, 'iipr hnon kylw pvrh')  # Replace 'doctorcare' with your email password
        server.sendmail(sender_email, recipient_email, email_message.as_string())

@app.route("/appointment.html")
def ap():
    return render_template("appointment.html")

@app.route("/video_consultation")
def video():
    return render_template('video_consultation.html')

@app.route('/confirmation.html')
def confirmation():
    try:
        # Connect to MySQL database
        dbconn = get_db_connection()  # Establish the connection
        cursor = dbconn.cursor()
        

        # Retrieve appointment details from the database
        cursor.execute("SELECT * FROM app ORDER BY Sno DESC LIMIT 1")
        appointments = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        

        # Render the confirmation page with appointment details
        return render_template('confirmation.html', appointments=appointments)
    except Exception as e:
        return str(e)




@app.route("/book_appointment", methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        time = request.form.get('time')
        date = request.form.get('date')
        upi_id = request.form.get("upi_id")  # UPI ID is assumed to be a form field

        # Debugging: Print values
        print(f"Name: {name}, Email: {email}, Time: {time}, Date: {date}, UPI_ID: {upi_id}")
        dbconn=get_db_connection()
        cursor = dbconn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE date = %s AND time = %s", (date, time))
        result = cursor.fetchone()
        if not email:
            return "<script>alert('Email is required. Please fill in the email field.'); window.history.back();</script>"

        dbconn = get_db_connection()  # Establish the connection
        cursor = dbconn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE date = %s AND time = %s", (date, time))
        result = cursor.fetchone()

        if result:
            return "<script>alert('Sorry, this time slot is already reserved. Please choose another time.'); window.history.back();</script>"
        else:
            try:
                # Insert data into the database
                cursor.execute(
                    "INSERT INTO bookings (name, time, date, email, upi_id) VALUES (%s, %s, %s, %s, %s)",
                    (name, time, date, email, upi_id)
                )
                dbconn.commit()
                cursor.close()

                # Send email
                send_email_1(name, email, date, time, upi_id)

                # Success message
                flash("Submission successful. Check your email for further details.")
                return redirect('/success')
            except Exception as e:
                print(f"An error occurred: {e}")
                return f"<script>alert('An error occurred: {e}'); window.history.back();</script>"

    return render_template('video_consultation.html')

@app.route('/success')
def success():
    return render_template("success.html", message="Your appointment has been successfully booked.")

def send_email_1(name, recipient_email, date, time, upi_id):
    sender_email = 'sandhikagovindaraj@gmail.com'
    app_password = 'iipr hnon kylw pvrh'  # Replace with the correct Gmail App Password
    subject = 'Video Consultation Appointment Details'
    google_meet_link = 'https://meet.google.com/example-link'  # Replace with the actual Google Meet link
    price = 500
    toothsy_upi_id = 'toothsy@oksbi'

    # Create email body
    body = f"""
    Dear {name},

    Thank you for scheduling a video consultation with MedCare. Below are the details of your appointment:

    - Date: {date}
    - Time: {time}
    - Price: {price} INR
    - Google Meet Link: {google_meet_link}
    - Toothsy UPI ID: {toothsy_upi_id}

    **Important:**
    Please complete the payment of {price} INR using the provided UPI ID. The video consultation will be confirmed only after payment is received from the specified UPI ID: {upi_id}.
   
    Regards,
    Toothsy
    """

    # Create MIME object
    email_message = MIMEMultipart()
    email_message['Subject'] = subject
    email_message['From'] = sender_email
    email_message['To'] = recipient_email
    email_message.attach(MIMEText(body, 'plain'))  # Attach email body

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            # Correctly specify the sender and recipient
            server.sendmail(sender_email, recipient_email, email_message.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


@app.route("/timeslot.html")
def ts():
    return render_template("timeslot.html")



@app.route("/vtimeslot.html")
def vts():
    return render_template("vtimeslot.html")


@app.route('/products', methods=['GET'])
def product_list():
    search_query = request.args.get('search', '')  # Get search query from URL
    
    # Connect to the database
    dbconn=get_db_connection()
    cursor=dbconn.cursor()

    # SQL query to get products based on the search query in both name and description
    if search_query:
        cursor.execute(
            "SELECT * FROM products WHERE name LIKE %s OR description LIKE %s", 
            ('%' + search_query + '%', '%' + search_query + '%')
        )
    else:
        cursor.execute("SELECT * FROM products")
    
    products = cursor.fetchall()
    
    cursor.close()

    return render_template('products.html', products=products, search_query=search_query)



@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    dbconn=get_db_connection()
    cursor=dbconn.cursor()

    # Fetch product details by ID
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()

    if product:
        # Check if the product is already in the cart
        cursor.execute('SELECT * FROM carts WHERE product_id = %s', (product_id,))
        cart_item = cursor.fetchone()

        if cart_item:
            # If the product is already in the cart, increment the quantity
            cursor.execute('UPDATE carts SET quantity = quantity + 1 WHERE product_id = %s', (product_id,))
        else:
            # If the product is not in the cart, insert a new record
            cursor.execute(
                'INSERT INTO carts (product_id, name, description, price, image_url, quantity) VALUES (%s, %s, %s, %s, %s, %s)',
                (product[0], product[1], product[2], product[3], product[4], 1)  # Start with quantity 1
            )
        dbconn.commit()

    cursor.close()
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    dbconn=get_db_connection()
    cursor=dbconn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.description, c.price, c.image_url, c.quantity
        FROM carts c
    """)
    cart_items = cursor.fetchall()
    cursor.close()

    # Calculate total price
    total_price = sum(item[3] * item[5] for item in cart_items)  # price * quantity

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)




    
@app.route('/remove_from_cart/<int:cart_id>')
def remove_from_cart(cart_id):
    dbconn=get_db_connection()
    cursor=dbconn.cursor()
    cursor.execute("DELETE FROM carts WHERE id = %s", (cart_id,))
    dbconn.commit()
    cursor.close()
    return redirect(url_for('cart'))


@app.route('/increment_quantity/<int:cart_id>')
def increment_quantity(cart_id):
    dbconn=get_db_connection()
    cursor=dbconn.cursor()
    cursor.execute("UPDATE carts SET quantity = quantity + 1 WHERE id = %s", (cart_id,))
    dbconn.commit()
    cursor.close()
    return redirect(url_for('cart'))

@app.route('/decrement_quantity/<int:cart_id>')
def decrement_quantity(cart_id):
            dbconn=get_db_connection()
            cursor=dbconn.cursor()
            cursor.execute("UPDATE carts SET quantity = GREATEST(quantity - 1, 1) WHERE id = %s", (cart_id,))
            dbconn.commit()
            cursor.close()
            return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/process_order', methods=['POST'])
def process_order():
    if 'email' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    address = request.form['address']
    phone = request.form['phone']
   
    # Send confirmation email
    email = session['email']
    send_email_2(name,email,address)
    
    dbconn=get_db_connection()
    cursor=dbconn.cursor()
    
    # Move items from carts to orders table
    cursor.execute("""
        INSERT INTO orders (user_name, address, phone, email, product_id, quantity, price, order_date)
        SELECT %s, %s, %s, %s, carts.product_id, carts.quantity, carts.price, NOW()
        FROM carts
    """, (name, address, phone, email))
    
    # Delete items from carts table
    cursor.execute("DELETE FROM carts")
    
    dbconn.commit()
    cursor.close()
    
    return redirect(url_for('order_success'))
def send_email_2(name,email,address):
    try:
        sender_email = 'sandhikagovindaraj@gmail.com'
        recipient_email = email
        subject = 'Order Confirmation'
        body = f'''Dear {name},
                    Your order has been successfully placed. Delivery expected in 3-4 to {address}.
                    Thanks for shopping with us.
                    
                    With Regards,
                    TOOTHSY. '''
        
        email_message = MIMEText(body)
        email_message['Subject'] = subject
        email_message['From'] = sender_email
        email_message['To'] = recipient_email
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, 'iipr hnon kylw pvrh')  # Use App Password, not account password
            server.sendmail(sender_email, recipient_email, email_message.as_string())
        print("Email sent successfully.")
    except OSError as e:
        print(f"Failed to send email: {e}")
        raise



@app.route('/order_success')
def order_success():
    msg="Order placed successfully.For further details refer the mail from TOOTHSY."
    return render_template('order_success.html',msg=msg)

@app.route('/myorders', methods=['GET'])
def my_orders():
    # Ensure user is logged in
    if 'email' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    # Fetch email from session
    email = session['email']
    
    dbconn=get_db_connection()
    cursor=dbconn.cursor()
    
    # Query to perform inner join and fetch required fields
    cursor.execute("""
        SELECT 
            products.name, 
            products.description, 
            products.image_url, 
            orders.quantity, 
            orders.status, 
            orders.price
        FROM orders
        INNER JOIN products ON orders.product_id = products.id
        WHERE orders.email = %s
    """, (email,))
    
    # Fetch all results
    orders = cursor.fetchall()
    cursor.close()
    if orders:
    
        # Pass the orders to the template
        return render_template('myorder.html', orders=orders)
    else:
        msg="No Orders Placed Yet."
        return render_template('myorder.html',msg=msg)
        





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
