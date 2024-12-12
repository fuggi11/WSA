from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import re

app = Flask(__name__)

app.secret_key = 'your secret key'


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Aji2611#',
    'database': 'walmartsales'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'invoice_id' in request.form:
        invoice_id = request.form['invoice_id']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)  # Use dictionary cursor
        cursor.execute('SELECT * FROM sales WHERE invoice_id = %s', (invoice_id,))
        data = cursor.fetchone()
        if data:
            msg=(
    f"On {data['date'].strftime('%A, %B %d, %Y')}, at {data['time_of_day']} in {data['city']} "
    f"(Branch {data['branch']}), a {data['gender']} {data['customer_type']} customer purchased "
    f"{data['product_line']}. The total amount was ${data['total']:.2f}. "
    f"The payment was made using a {data['payment']}. The rating for the transaction was {data['rating']}."
     )
            
        else:
            msg = 'Incorrect invoice_id'

        cursor.close()
        connection.close()
    return render_template('login.html', msg=msg)

@app.route('/process_sales_analysis', methods=['POST'])
def process_sales_analysis():
    # Logic to generate and display sales analysis (e.g., bar chart)
    return "Displaying Sales Analysis of Items."

@app.route('/process_branch_sales', methods=['POST'])
def process_branch_sales():
    # Logic to analyze sales based on branch
    return "Displaying Sales Based on Branch."

@app.route('/process_customer_feedback', methods=['POST'])
def process_customer_feedback():
    # Logic to display customer feedback
    return "Displaying Customer Feedback."


if __name__ == '__main__':
    app.run(debug=True, port=8000)