from flask import Flask, render_template, request, redirect, url_for, session, Response
import mysql.connector
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') 
import io
import base64
import pandas as pd
msg=''
total_sales=''
average_rating=''
branch_graph=''
product_graph=''
top_selling_products=''
msg1=''
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
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    msg = ''
    # Connect to the database
    connection = get_db_connection()
    cursor = connection.cursor()
    if cursor:
                    print("Cursor creation successful.")  # Debugging log
    else:
                    print("Cursor creation failed.")
    # Total Sales
    cursor.execute('SELECT SUM(Total) FROM sales')
    total_sales = cursor.fetchone()[0]

    # Average Rating
    cursor.execute('SELECT AVG(Rating) FROM sales')
    average_rating = cursor.fetchone()[0]

    # Sales by Branch
    cursor.execute('SELECT Branch, COUNT(*) as count FROM sales GROUP BY Branch')
    branch_sales = cursor.fetchall()

    # Top-selling product lines
    cursor.execute('SELECT `Product line`, COUNT(*) as count FROM sales GROUP BY `Product line` ORDER BY count DESC LIMIT 5')
    top_selling_products = cursor.fetchall()

    cursor.close()
    connection.close()

    # Prepare data for visualization (Sales by Branch and Product Lines)
    branch_df = pd.DataFrame(branch_sales, columns=['branch', 'count'])
    product_df = pd.DataFrame(top_selling_products, columns=['product_line', 'count'])

    # Define bright colors
    bright_colors = ['#FFD700', '#FF6347', '#90EE90', '#ADD8E6', '#FF69B4', '#FF4500', '#32CD32']

    # Sales by Branch Pie Chart
    plt.figure(figsize=(8, 8))
    patches, texts, autotexts = plt.pie(
        branch_df['count'],
        colors=bright_colors[:len(branch_df)],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 16, 'fontweight': 'bold'}  # Make text bold and large
    )
    plt.legend(patches, branch_df['branch'], loc='upper left', title="Branches", fontsize=12)
    plt.title('Sales Distribution by Branch', fontsize=18, fontweight='bold')
    img_branch = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_branch, format='png', dpi=300)
    img_branch.seek(0)
    plt.close()

    # Top Selling Product Lines Pie Chart
    plt.figure(figsize=(8, 8))
    patches, texts, autotexts = plt.pie(
        product_df['count'],
        colors=bright_colors[:len(product_df)],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 16, 'fontweight': 'bold'}  # Make text bold and large
    )
    plt.legend(patches, product_df['product_line'], loc='upper left', title="Product Lines", fontsize=12)
    plt.title('Top Selling Product Lines Distribution', fontsize=18, fontweight='bold')
    img_product = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_product, format='png', dpi=300)
    img_product.seek(0)
    plt.close()

    # Encode the images in base64
    branch_graph = base64.b64encode(img_branch.getvalue()).decode('utf8')
    branch_graph = f"data:image/png;base64,{branch_graph}"

    product_graph = base64.b64encode(img_product.getvalue()).decode('utf8')
    product_graph = f"data:image/png;base64,{product_graph}"

    return render_template(
        'login.html',
        total_sales=total_sales,
        average_rating=average_rating,
        branch_graph=branch_graph,
        product_graph=product_graph,
        top_selling_products=top_selling_products,
        msg=msg,msg1=msg1
    )




@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'invoice_id' in request.form:
        invoice_id = request.form['invoice_id']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM sales WHERE invoice_id = %s', (invoice_id,))
        data = cursor.fetchone()
        if data:
            msg = (
                f"On {data['date'].strftime('%A, %B %d, %Y')}, at {data['time_of_day']} in {data['city']} "
                f"(Branch {data['branch']}), a {data['gender']} {data['customer_type']} customer purchased "
                f"{data['product_line']}. The total amount was ${data['total']:.2f}. "
                f"The payment was made using a {data['payment']}. The rating for the transaction was {data['rating']}."
            )
        else:
            msg = 'Incorrect invoice_id'
        cursor.close()
        connection.close()
    return render_template('login.html', msg=msg,
        total_sales=total_sales,
        average_rating=average_rating,
        branch_graph=branch_graph,
        product_graph=product_graph,
        top_selling_products=top_selling_products)

@app.route('/process_sales_analysis', methods=['POST'])
def process_sales_analysis():
    # Generate a bar chart for item sales analysis
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT product_line, COUNT(*) as count FROM sales GROUP BY product_line')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Prepare data for visualization
    df = pd.DataFrame(rows, columns=['product_line', 'count'])
    product_lines = df['product_line']
    counts = df['count']

    # Generate the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(product_lines, counts, color='skyblue')
    plt.title('Sales Analysis of Items')
    plt.xlabel('Product Line')
    plt.ylabel('Count')
    plt.xticks(rotation=45)

    # Save the figure to a BytesIO object
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Encode the image in base64
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')
    graph_url = f"data:image/png;base64,{graph_url}"
    return render_template('login.html', sales_graph=f"data:image/png;base64,{graph_url}")

@app.route('/process_branch_sales', methods=['POST'])
def process_branch_sales():
    # Generate a bar chart for branch sales
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT branch, COUNT(*) as count FROM sales GROUP BY branch')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Prepare data for visualization
    df = pd.DataFrame(rows, columns=['branch', 'count'])
    branches = df['branch']
    counts = df['count']

    # Generate the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(branches, counts, color='lightcoral')
    plt.title('Sales Based on Branch')
    plt.xlabel('Branch')
    plt.ylabel('Count')

    # Save the figure to a BytesIO object
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Encode the image in base64
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('login.html', branch_graph=f"data:image/png;base64,{graph_url}")
@app.route('/process_customer_feedback', methods=['POST'])

def process_customer_feedback():
   
    cursor=None
    connection=None
    if request.method == 'POST':
        feedback = request.form.get('feedback')  # Safely retrieve feedback from the form
        if feedback:
            try:
                # Use the feedback database connection
                connection = get_db_connection()
                if connection:
                    print("Database connection successful.")  # Debugging log
                else:
                    print("Database connection failed.")  # Debugging log
                
                # Attempt to create a cursor
                cursor = connection.cursor(dictionary=True)
                if cursor:
                    print("Cursor creation successful.")  # Debugging log
                else:
                    print("Cursor creation failed.")  # Debugging log
                # Insert feedback into the feedback database
                cursor.execute('INSERT INTO feedback (feedback_text) VALUES (%s)', (feedback,))
                connection.commit()
                
                msg1 = 'Feedback submitted successfully!'
            except mysql.connector.Error as err:
                msg1 = f"Error: {err}"
            finally:
                cursor.close()
                connection.close()
        else:
            msg1 = 'Feedback cannot be empty.'
        dashboard()
        return render_template('login.html', msg=msg,
        total_sales=total_sales,
        average_rating=average_rating,
        branch_graph=branch_graph,
        product_graph=product_graph,
        top_selling_products=top_selling_products,msg1=msg1)

def render_t():
       return render_template('login.html', msg=msg,
        total_sales=total_sales,
        average_rating=average_rating,
        branch_graph=branch_graph,
        product_graph=product_graph,
        top_selling_products=top_selling_products,msg1=msg1)
@app.route('/hist', methods=['GET'])
def hist():
    return render_template('hist.html')
from datetime import datetime

@app.route('/hist_p', methods=['GET', 'POST'])
def hist_p():
    dis = ''
    if request.method == 'POST' and 'phone' in request.form:
        phone = request.form['phone']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'SELECT `Invoice ID`, Branch, City, `Customer type`, Gender, `Product line`, `Unit price`, Quantity, `Tax 5%`, Total, Date, Time, Payment, cogs, `gross margin percentage`, `gross income`, Rating, Phone '
             'FROM sales WHERE Phone = %s', (phone,)
        )
        data = cursor.fetchall()
        
        if data:
            # Generate fancy message for each transaction
            dis = ""
            for transaction in data:
                # Fancy Message Combining Columns
                date_obj = datetime.strptime(transaction['Date'], '%Y-%m-%d')
                message = (
                    f"On {date_obj.strftime('%A, %B %d, %Y')} at {transaction['Time']} in {transaction['City']} "
                    f"(Branch {transaction['Branch']}), a {transaction['Gender']} {transaction['Customer type']} customer purchased "
                    f"from the {transaction['Product line']} line. The total amount was ${transaction['Total']:.2f} "
                    f"and the payment was made using {transaction['Payment']}. Rating: {transaction['Rating']}/10."
                )
                dis += f"<p>{message}</p><br>"

            # Table of Other Details
            dis += """
            <table class="table">
                <tr>
                    <th>Invoice ID</th>
                    <th>Product Line</th>
                    <th>Unit Price</th>
                    <th>Quantity</th>
                    <th>Tax 5%</th>
                    <th>Total</th>
                    <th>Payment</th>
                    <th>Rating</th>
                </tr>
            """
            for transaction in data:
                dis += f"""
                <tr>
                    <td>{transaction['Invoice ID']}</td>
                    <td>{transaction['Product line']}</td>
                    <td>${transaction['Unit price']:.2f}</td>
                    <td>{transaction['Quantity']}</td>
                    <td>${transaction['Tax 5%']:.2f}</td>
                    <td>${transaction['Total']:.2f}</td>
                    <td>{transaction['Payment']}</td>
                    <td>{transaction['Rating']}</td>
                </tr>
                """
            dis += "</table>"

        else:
            dis = 'No transactions found for this phone number.'
        
        cursor.close()
        connection.close()
    
    return render_template('hist.html', dis=dis)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
