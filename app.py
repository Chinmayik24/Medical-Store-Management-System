from flask import Flask, render_template, request, redirect, url_for
import mysql.connector as sqlct
import datetime

app = Flask(__name__)

# Database connection setup
def get_db_connection():
    mycn = sqlct.connect(
        host="localhost",
        user="root",
        password="chinnu@2003k",
        database="medical_store"
    )
    return mycn

# Initialize database and tables
def createdb():
    mycn = get_db_connection()
    mycur = mycn.cursor()
    cmd1 = """
    CREATE TABLE IF NOT EXISTS _medicalproject (
        ProductCode INT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        Packing VARCHAR(50),
        Expirydate DATE,
        Company VARCHAR(50),
        Batch VARCHAR(10),
        Quantity INT,
        Rate INT
    )
    """
    mycur.execute(cmd1)

    cust1 = """
    CREATE TABLE IF NOT EXISTS customertable (
        BillNumber INT,
        Customername VARCHAR(50),
        Doctorname VARCHAR(50),
        Productcode INT,
        Quantity INT,
        FOREIGN KEY (Productcode) REFERENCES _medicalproject(ProductCode)
    )
    """
    mycur.execute(cust1)
    mycn.close()

createdb()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        data = (
            request.form['ProductCode'],
            request.form['name'],
            request.form['Packing'],
            request.form['ExpiryDate'],
            request.form['Company'],
            request.form['Batch'],
            request.form['Quantity'],
            request.form['Rate']
        )
        mycn = get_db_connection()
        mycur = mycn.cursor()
        cmd = """
        INSERT INTO _medicalproject (ProductCode, name, Packing, Expirydate, Company, Batch, Quantity, Rate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        mycur.execute(cmd, data)
        mycn.commit()
        mycn.close()
        return redirect(url_for('display_medicine'))
    return render_template('add_medicine.html')

@app.route('/display_medicine')
def display_medicine():
    mycn = get_db_connection()
    mycur = mycn.cursor()
    cmd = "SELECT * FROM _medicalproject"
    mycur.execute(cmd)
    results = mycur.fetchall()
    mycn.close()
    return render_template('display_medicine.html', medicines=results)

@app.route('/search_medicine', methods=['GET', 'POST'])
def search_medicine():
    if request.method == 'POST':
        med_name = request.form['med_name']
        mycn = get_db_connection()
        mycur = mycn.cursor()
        cmd = "SELECT * FROM _medicalproject WHERE name LIKE %s"
        mycur.execute(cmd, ('%' + med_name + '%',))
        results = mycur.fetchall()
        mycn.close()
        return render_template('search_medicine.html', medicines=results)
    return render_template('search_medicine.html', medicines=None)

@app.route('/expiry_stock')
def expiry_stock():
    expdate = datetime.date.today()
    mycn = get_db_connection()
    mycur = mycn.cursor()
    cmd = "SELECT ProductCode, name, Expirydate, Batch FROM _medicalproject WHERE Expirydate <= %s"
    mycur.execute(cmd, (expdate,))
    results = mycur.fetchall()
    mycn.close()
    return render_template('expiry_stock.html', stocks=results)

@app.route('/display_companywise', methods=['GET', 'POST'])
def display_companywise():
    if request.method == 'POST':
        company_name = request.form['company_name']
        mycn = get_db_connection()
        mycur = mycn.cursor()
        cmd = "SELECT * FROM _medicalproject WHERE Company = %s"
        mycur.execute(cmd, (company_name,))
        results = mycur.fetchall()
        mycn.close()
        return render_template('companywise.html', medicines=results)
    return render_template('companywise.html', medicines=None)

@app.route('/delete_medicine', methods=['GET', 'POST'])
def delete_medicine():
    if request.method == 'POST':
        delete_medicine = int(request.form['delete_medicine'])
        mycn = get_db_connection()
        mycur = mycn.cursor()
        cmd = "SELECT COUNT(*) FROM customertable WHERE Productcode = %s"
        mycur.execute(cmd, (delete_medicine,))
        total_record = mycur.fetchone()[0]
        if total_record == 0:
            cmd = "DELETE FROM _medicalproject WHERE ProductCode = %s"
            mycur.execute(cmd, (delete_medicine,))
            mycn.commit()
        else:
            cmd = "UPDATE _medicalproject SET Quantity = 0 WHERE ProductCode = %s"
            mycur.execute(cmd, (delete_medicine,))
            mycn.commit()
        mycn.close()
        return redirect(url_for('display_medicine'))
    return render_template('delete_medicine.html')

@app.route('/add_newbill', methods=['GET', 'POST'])
def add_newbill():
    if request.method == 'POST':
        BillNumber = request.form['BillNumber']
        name = request.form['name']
        DoctorName = request.form['DoctorName']
        Productcode = request.form['Productcode']
        Quantity = request.form['Quantity']
        mycn = get_db_connection()
        mycur = mycn.cursor()
        cmd = """
        INSERT INTO customertable (BillNumber, Customername, Doctorname, Productcode, Quantity)
        VALUES (%s, %s, %s, %s, %s)
        """
        mycur.execute(cmd, (BillNumber, name, DoctorName, Productcode, Quantity))
        mycn.commit()
        mycn.close()
        return redirect(url_for('display_bill'))
    return render_template('add_newbill.html')

@app.route('/display_bill')
def display_bill():
    mycn = get_db_connection()
    mycur = mycn.cursor()
    cmd = """
    SELECT CT.BillNumber, CT.Customername, CT.Doctorname, CT.Productcode, MDT.name, CT.Quantity, MDT.Rate, CT.Quantity * MDT.Rate AS Amount
    FROM customertable CT
    JOIN _medicalproject MDT ON CT.Productcode = MDT.ProductCode
    """
    mycur.execute(cmd)
    results = mycur.fetchall()
    mycn.close()
    return render_template('display_bill.html', bills=results)

@app.route('/search_bill', methods=['GET', 'POST'])
def search_bill():
    if request.method == 'POST':
        Bill_Number = int(request.form['Bill_Number'])
        mycn = get_db_connection()
        mycur = mycn.cursor()
        cmd = """
        SELECT CT.BillNumber, CT.Customername, CT.Doctorname, CT.Productcode, MDT.name, CT.Quantity, MDT.Rate, CT.Quantity * MDT.Rate AS Amount
        FROM customertable CT
        JOIN _medicalproject MDT ON CT.Productcode = MDT.ProductCode
        WHERE CT.BillNumber = %s
        """
        mycur.execute(cmd, (Bill_Number,))
        result = mycur.fetchone()
        mycn.close()
        return render_template('search_bill.html', bill=result)
    return render_template('search_bill.html', bill=None)

if __name__ == '__main__':
    app.run(debug=True)
