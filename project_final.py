import mysql.connector as sqlct
import datetime

def createdb():
    global mycn
    global mycur
    mycn = sqlct.connect(
        host="localhost",
        user="root",
        password="chinnu@2003k",  # Change this to your MySQL password
        database="medical_store"
    )
    if mycn.is_connected():
        print("\tThank you for choosing to shop with Apollo Medical Store.")
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

def add_medicine():
    ProductCode = int(input("Enter the product code: "))
    name = input("Enter name of the medicine: ")
    Packing = input("Enter the packing details: ")
    ExpiryDate = input("Enter expiry date of medicine (yyyy-mm-dd): ")
    Company = input("Enter name of the company: ")
    Batch = input("Enter batch name of medicine: ")
    Quantity = int(input("Enter quantity for your medicine: "))
    Rate = int(input("Enter rate of your medicine: "))

    cmd = """
    INSERT INTO _medicalproject (ProductCode, name, Packing, Expirydate, Company, Batch, Quantity, Rate)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (ProductCode, name, Packing, ExpiryDate, Company, Batch, Quantity, Rate)
    mycur.execute(cmd, values)
    mycn.commit()
    print("Record has been added successfully")

def display_medicine():
    cmd = "SELECT * FROM _medicalproject"
    mycur.execute(cmd)
    r2 = mycur.fetchall()
    print("=================================================================================================================")
    print("| PRODUCT CODE   MEDICINE NAME   PACKING DETAILS   EXPIRY DATE   COMPANY NAME   BATCH      QUANTITY   RATE  |")
    print("=================================================================================================================")
    for row in r2:
        print(f"| {str(row[0]).ljust(15)} {row[1].ljust(17)} {row[2].ljust(18)} {str(row[3]).ljust(14)} {row[4].ljust(15)} {row[5].ljust(10)} {str(row[6]).ljust(10)} {str(row[7]).ljust(5)} |")
    print("=================================================================================================================")

def search_medicine():
    med_name = input("Enter medicine name for search: ")
    cmd = "SELECT * FROM _medicalproject WHERE name LIKE %s"
    mycur.execute(cmd, ('%' + med_name + '%',))
    r2 = mycur.fetchall()
    if not r2:
        print("No record found")
    else:
        print("PRODUCT CODE   MEDICINE NAME   PACKING DETAILS   EXPIRY DATE   COMPANY NAME   BATCH      QUANTITY   RATE")  
        for row in r2:
            print(f"{str(row[0]).ljust(15)} {row[1].ljust(17)} {row[2].ljust(18)} {str(row[3]).ljust(14)} {row[4].ljust(15)} {row[5].ljust(10)} {str(row[6]).ljust(10)} {str(row[7]).ljust(5)}")

def expiry_stockmodule():
    expdate = datetime.date.today()
    cmd = "SELECT ProductCode, name, Expirydate, Batch FROM _medicalproject WHERE Expirydate <= %s"
    mycur.execute(cmd, (expdate,))
    r2 = mycur.fetchall()
    if not r2:
        print("No expired stock found.")
    else:
        print("PRODUCT CODE   NAME             EXPIRY DATE   BATCH")  
        for row in r2:
            print(f"{str(row[0]).ljust(15)} {row[1].ljust(17)} {str(row[2]).ljust(14)} {str(row[3]).ljust(15)}")

def display_companywise():
    company_name = input("Enter the company name you want to display: ")
    cmd = "SELECT * FROM _medicalproject WHERE Company = %s"
    mycur.execute(cmd, (company_name,))
    r4 = mycur.fetchall()
    if not r4:
        print("No record found")
    else:
        print("PRODUCT CODE   MEDICINE NAME   PACKING DETAILS   EXPIRY DATE   COMPANY NAME   BATCH      QUANTITY   RATE")
        for row in r4:
            print(f"{str(row[0]).ljust(15)} {row[1].ljust(17)} {row[2].ljust(18)} {str(row[3]).ljust(14)} {row[4].ljust(15)} {row[5].ljust(10)} {str(row[6]).ljust(10)} {str(row[7]).ljust(5)}")

def delete_medicine():
    delete_medicine = int(input("Enter the medicine product code that you want to delete: "))
    cmd = "SELECT COUNT(*) FROM customertable WHERE Productcode = %s"
    mycur.execute(cmd, (delete_medicine,))
    total_record = mycur.fetchone()[0]
    if total_record == 0:
        cmd = "DELETE FROM _medicalproject WHERE ProductCode = %s"
        mycur.execute(cmd, (delete_medicine,))
        mycn.commit()
        print("Record has been deleted")
    else:
        cmd = "UPDATE _medicalproject SET Quantity = 0 WHERE ProductCode = %s"
        mycur.execute(cmd, (delete_medicine,))
        mycn.commit()
        print("This medicine has already been sold, so it can't be deleted. Hence, the quantity is set to zero.")

def add_newbill():
    cmd = "SELECT COALESCE(MAX(BillNumber), 0) FROM customertable"
    mycur.execute(cmd)
    BillNumber = mycur.fetchone()[0] + 1
    print(f"Your bill number is: {BillNumber}")
    name = input("Enter your name: ")
    DoctorName = input("Enter your doctor's name: ")
    while True:
        Productcode = int(input("Enter product code of your medicine: "))
        Quantity = int(input("Enter quantity for your medicine: "))
        cmd = """
        INSERT INTO customertable (BillNumber, Customername, Doctorname, Productcode, Quantity)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (BillNumber, name, DoctorName, Productcode, Quantity)
        mycur.execute(cmd, values)
        mycn.commit()
        addmed = input("Do you want to add medicine (y/n)? ")
        if addmed.lower() == 'n':
            break
    print("Record has been added")

def display_bill():
    cmd = """
    SELECT CT.BillNumber, CT.Customername, CT.Doctorname, CT.Productcode, MDT.name, CT.Quantity, MDT.Rate, CT.Quantity * MDT.Rate AS Amount
    FROM customertable CT
    JOIN _medicalproject MDT ON CT.Productcode = MDT.ProductCode
    """
    mycur.execute(cmd)
    r = mycur.fetchall()
    print("BILL NUMBER   CUSTOMER NAME       DOCTOR NAME    PRODUCT CODE   MEDICINE NAME     QUANTITY    RATE    AMOUNT")
    for row in r:
        print(f"{str(row[0]).ljust(12)} {row[1].ljust(20)} {row[2].ljust(15)} {str(row[3]).ljust(12)} {row[4].ljust(15)} {str(row[5]).ljust(8)} {str(row[6]).ljust(7)} {str(row[7]).ljust(7)}")

def search_bill():
    Bill_Number = int(input("Enter the bill number which you want to search: "))
    cmd = """
    SELECT CT.BillNumber, CT.Customername, CT.Doctorname, CT.Productcode, MDT.name, CT.Quantity, MDT.Rate, CT.Quantity * MDT.Rate AS Amount
    FROM customertable CT
    JOIN _medicalproject MDT ON CT.Productcode = MDT.ProductCode
    WHERE CT.BillNumber = %s
    """
    mycur.execute(cmd, (Bill_Number,))
    r3 = mycur.fetchone()
    if r3 is None:
        print("No record found")
    else:
        print(f"Bill Number: {r3[0]}")
        print(f"Customer Name: {r3[1]}")
        print(f"Doctor Name: {r3[2]}")
        print(f"Product Code: {r3[3]}")
        print(f"Medicine Name: {r3[4]}")
        print(f"Quantity: {r3[5]}")
        print(f"Rate: {r3[6]}")
        print(f"Amount: {r3[7]}")

def show_shop_owner_menu():
    while True:
        print("----SHOP OWNER----")
        print("(1) ADD MEDICINE")
        print("(2) DISPLAY ALL MEDICINE")
        print("(3) SEARCH MEDICINE")
        print("(4) DISPLAY MEDICINES COMPANYWISE")
        print("(5) CHECK EXPIRY STOCK")
        print("(6) DELETE MEDICINE")
        print("(7) ADD NEW BILL")
        print("(8) DISPLAY ALL BILLS")
        print("(9) SEARCH BILL")
        print("(10) EXIT")
        choice = input("Please enter your choice: ")

        if choice == '1':
            add_medicine()
        elif choice == '2':
            display_medicine()
        elif choice == '3':
            search_medicine()
        elif choice == '4':
            display_companywise()
        elif choice == '5':
            expiry_stockmodule()
        elif choice == '6':
            delete_medicine()
        elif choice == '7':
            add_newbill()
        elif choice == '8':
            display_bill()
        elif choice == '9':
            search_bill()
        elif choice == '10':
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    createdb()
    show_shop_owner_menu()
