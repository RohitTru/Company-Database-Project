from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def log_query(query, results):
    """Helper function to log queries and results for debugging."""
    logging.debug(f"Executed Query: {query}")
    logging.debug(f"Results: {results}")

# Placeholder for SQL reset and insert commands
RESET_SQL = """
-- Your SQL reset and insert commands go here
DELETE FROM InterviewGrade;
DELETE FROM InterviewerAssignment;
DELETE FROM Interview;
DELETE FROM Application;
DELETE FROM JobPosition;
DELETE FROM EmployeeDepartmentAssignment;
DELETE FROM EmployeeSiteAssignment;
DELETE FROM Sale;
DELETE FROM ProductPart;
DELETE FROM VendorPart;
DELETE FROM Part;
DELETE FROM Vendor;
DELETE FROM Site;
DELETE FROM Product;
DELETE FROM Salary;
DELETE FROM PreferredSalesperson;
DELETE FROM Customer;
DELETE FROM Employee;
DELETE FROM PersonType;
DELETE FROM PhoneNumber;
DELETE FROM Person;
DELETE FROM Department;

-- Insert data commands here
INSERT INTO Department (Department_ID, DepartmentName) VALUES
(1, 'Marketing'), (2, 'Sales'), (3, 'Engineering'), (4, 'HR');

INSERT INTO Person (PersonID, LastName, FirstName, Age, Gender, AddressLine1, AddressLine2, City, State, ZipCode) VALUES
(1, 'Smith', 'John', 34, 'M', '123 Maple St', '', 'Dallas', 'TX', 75001),
(2, 'Doe', 'Jane', 28, 'F', '456 Oak St', 'Apt 5', 'Austin', 'TX', 78701),
(3, 'Brown', 'Charlie', 45, 'M', '789 Pine St', '', 'Houston', 'TX', 77001),
(4, 'Taylor', 'Alice', 39, 'F', '321 Cedar St', '', 'Plano', 'TX', 75024),
(101, 'Cole', 'Hellen', 30, 'F', '123 Main St', NULL, 'City', 'State', 12345), -- Interviewee
(102, 'Smith', 'John', 40, 'M', '456 Another St', NULL, 'City', 'State', 12346), -- Interviewer
(201, 'Doe', 'Jane', 35, 'F', '789 Street', NULL, 'City', 'State', 12347),
(202, 'Brown', 'Emily', 25, 'F', '321 Lane', NULL, 'City', 'State', 12348);

INSERT INTO PhoneNumber (PersonID, PhoneNumber) VALUES
(1, '2145551234'),
(1, '2145555678'),
(2, '5125554321'),
(3, '7135558765'),
(101, '2145556789');

INSERT INTO PersonType (PersonID, Type) VALUES
(1, 'Employee'),
(2, 'Customer'),
(3, 'Employee'),
(4, 'PotentialEmployee'),
(101, 'PotentialEmployee');

INSERT INTO Employee (PersonID, Erank, Title, SupervisorID) VALUES
(1, 'Senior', 'Manager', NULL),
(3, 'Junior', 'Engineer', 1),
(201, 'Senior', 'Manager', NULL),
(202, 'Junior', 'Developer', 201);

INSERT INTO Customer (PersonID) VALUES
(2);

INSERT INTO PreferredSalesperson (CustomerID, SalesPersonID) VALUES
(2, 1);

INSERT INTO EmployeeDepartmentAssignment (EmployeeID, DepartmentID, StartTime, EndTime) VALUES
(1, 1, '2023-01-01 08:00:00', '2023-12-31 17:00:00'),
(1, 2, '2023-01-01 08:00:00', '2023-12-31 17:00:00'),
(1, 3, '2023-01-01 08:00:00', '2023-12-31 17:00:00'),
(1, 4, '2023-01-01 08:00:00', '2023-12-31 17:00:00'), -- Employee 1 assigned to all departments
(2, 2, '2023-01-01 08:00:00', '2023-12-31 17:00:00'),
(4, 3, '2023-06-01 09:00:00', '2023-12-31 18:00:00'),
(5, 4, '2023-01-01 08:00:00', '2023-12-31 17:00:00'),
(202, 2, '2023-01-01 08:00:00', '2023-12-31 17:00:00'),
(3, 3, '2023-06-01 09:00:00', '2023-12-31 18:00:00');


INSERT INTO JobPosition (JobID, DepartmentID, JobDescription, PostedDate) VALUES
(1001, 1, 'Marketing Specialist', '2023-05-01'),
(1002, 3, 'Junior Engineer', '2023-07-01'),
(11111, 1, 'Developer', '2011-01-01'), -- For testing Hellen Cole's interview
(12345, 3, 'Software Engineer', '2023-05-01');


INSERT INTO Application (ApplicationID, ApplicantID, JobID, ApplicationDate) VALUES
(1, 4, 1001, '2023-06-10'),
(2, 3, 1002, '2023-07-15'),
(4, 3, 12345, '2023-06-15');; -- Application for job 12345

INSERT INTO Interview (InterviewID, JobID, CandidateID, InterviewTime) VALUES
(1, 1001, 4, '2023-06-15 10:00:00'),
(2, 1002, 3, '2023-08-01 14:00:00'),
(3, 11111, 101, '2011-02-01 10:00:00'); -- Interview for Hellen Cole

INSERT INTO InterviewerAssignment (InterviewID, InterviewerID) VALUES
(1, 1),
(2, 1),
(3, 201); -- John Smith as the interviewer

INSERT INTO InterviewGrade (InterviewID, InterviewerID, Grade) VALUES
(1, 1, 85),
(2, 1, 90),
(3, 201, 75); -- Grade for Hellen Cole

INSERT INTO Product (ProductID, ProductType, Size, ListPrice, Weight, Style) VALUES
(1, 'Electronics', 'Large', 299.99, 1.5, 'Modern'),
(2, 'Furniture', 'Medium', 149.99, 10.0, 'Vintage'),
(3, 'Clothing', 'Small', 49.99, 1.0, 'Casual'); -- For testing product type

INSERT INTO Site (SiteID, SiteName, Location) VALUES
(1, 'Main Office', 'Dallas'),
(2, 'Regional Office', 'Austin'),
(3, 'Test Site', 'Houston'); -- Site with no sales

INSERT INTO EmployeeSiteAssignment (EmployeeID, SiteID, StartDate, EndDate) VALUES
(1, 1, '2023-01-01', '2023-12-31'),
(3, 2, '2023-06-01', '2023-12-31');

INSERT INTO Sale (SalesID, SalesPersonID, CustomerID, ProductID, SiteID, SalesTime) VALUES
(1, 1, 2, 1, 1, '2023-08-15 15:30:00'),
(2, 1, 2, 2, 2, '2023-08-16 16:00:00'),
(3, 1, 2, 3, 1, '2023-08-17 17:00:00'); -- Sale involving all product types

INSERT INTO Vendor (VendorID, Name, AddressLine1, AddressLine2, City, State, ZipCode, AccountNumber, CreditRating, PurchasingWebServiceURL) VALUES
(1, 'ABC Supplies', '101 First Ave', '', 'Houston', 'TX', 77001, '12345', 8, 'http://abc-supplies.com'),
(2, 'XYZ Manufacturing', '202 Second Ave', '', 'Austin', 'TX', 78701, '67890', 9, 'http://xyz-manufacturing.com');

INSERT INTO Part (PartID, ProductID, Quantity, PartName, Weight) VALUES
(1, 1, 50, 'Cup', 3.5),  
(2, 2, 100, 'Bowl', 5.0), 
(3, 3, 20, 'Plate', 2.0);

INSERT INTO VendorPart (VendorID, PartID, Price) VALUES
(1, 1, 25.00),
(2, 2, 35.00),
(1, 3, 10.00); -- Cheapest part

INSERT INTO ProductPart (ProductID, PartID, Quantity) VALUES
(1, 1, 10),
(2, 2, 20),
(3, 3, 5);

INSERT INTO Salary (EmployeeID, TransactionNumber, PayDate, Amount) VALUES
(1, 1, '2023-01-31', 3000.00),
(1, 2, '2023-02-28', 3000.00),
(3, 1, '2023-06-30', 2000.00),
(201, 1, '2023-06-30', 4000.00); -- Highest salary
"""

@app.route("/", methods=["GET", "POST"])
def index():
    data = []  # Stores query results
    error_message = None
    success_message = None
    selected_query = None  # Initialize selected_query to avoid UnboundLocalError

    # Predefined queries
    predefined_queries = {
    "Interviewers for Hellen Cole (Job 11111)": "SELECT DISTINCT i.InterviewerID, p.LastName, p.FirstName FROM InterviewerAssignment i JOIN Interview iv ON i.InterviewID = iv.InterviewID JOIN JobPosition jp ON iv.JobID = jp.JobID JOIN Person p ON i.InterviewerID = p.PersonID WHERE iv.CandidateID = (SELECT PersonID FROM Person WHERE FirstName = 'Hellen' AND LastName = 'Cole') AND jp.JobID = 11111;",
    "Jobs posted by Marketing (January 2011)": "SELECT j.JobID FROM JobPosition j JOIN Department d ON j.DepartmentID = d.Department_ID WHERE d.DepartmentName = 'Marketing' AND j.PostedDate >= '2011-01-01' AND j.PostedDate < '2011-02-01';",
    "Employees with no supervisees": "SELECT e.PersonID, CONCAT(p.FirstName, ' ', p.LastName) AS Name FROM Employee e JOIN Person p ON e.PersonID = p.PersonID WHERE e.PersonID NOT IN (SELECT SupervisorID FROM Employee WHERE SupervisorID IS NOT NULL);",
    "Marketing sites with no sales (March 2011)": "SELECT s.SiteID, s.Location FROM Site s JOIN Department d ON d.DepartmentName = 'Marketing' WHERE s.SiteID NOT IN (SELECT SiteID FROM Sale WHERE SalesTime BETWEEN '2011-03-01' AND '2011-03-31');",
    "Jobs with no hires after 1 month of posting": "SELECT jp.JobID, jp.JobDescription FROM JobPosition jp WHERE NOT EXISTS (SELECT 1 FROM Application a WHERE a.JobID = jp.JobID AND a.ApplicationDate <= DATE_ADD(jp.PostedDate, INTERVAL 1 MONTH));",
    "Salespeople who sold all products > $200": "SELECT sp.PersonID, CONCAT(p.FirstName, ' ', p.LastName) AS Name FROM Employee sp JOIN Person p ON sp.PersonID = p.PersonID WHERE NOT EXISTS (SELECT pt.ProductType FROM Product pt WHERE pt.ListPrice > 200 AND pt.ProductType NOT IN (SELECT DISTINCT pr.ProductType FROM Sale s JOIN Product pr ON s.ProductID = pr.ProductID WHERE s.SalesPersonID = sp.PersonID));",
    "Departments with no job posts (Jan-Feb 2011)": "SELECT d.Department_ID, d.DepartmentName FROM Department d WHERE d.Department_ID NOT IN (SELECT jp.DepartmentID FROM JobPosition jp WHERE jp.PostedDate BETWEEN '2011-01-01' AND '2011-02-28');",
    "Employees applying for job 12345": "SELECT e.PersonID AS EmployeeID, CONCAT(p.FirstName, ' ', p.LastName) AS Name, ed.DepartmentID FROM Employee e JOIN Person p ON e.PersonID = p.PersonID JOIN Application a ON e.PersonID = a.ApplicantID JOIN JobPosition jp ON a.JobID = jp.JobID LEFT JOIN EmployeeDepartmentAssignment ed ON e.PersonID = ed.EmployeeID WHERE jp.JobID = 12345;",
    "Best seller's type": "SELECT pt.Type AS EmployeeType, SUM(1) AS TotalSales FROM Sale s JOIN Employee e ON s.SalesPersonID = e.PersonID JOIN PersonType pt ON e.PersonID = pt.PersonID WHERE pt.Type = 'Employee' GROUP BY pt.Type ORDER BY TotalSales DESC LIMIT 1;",
    "Product type with highest net profit": "SELECT pr.ProductType FROM Product pr JOIN ProductPart pp ON pr.ProductID = pp.ProductID JOIN VendorPart vp ON pp.PartID = vp.PartID GROUP BY pr.ProductType ORDER BY (SUM(pr.ListPrice) - SUM(vp.Price)) DESC LIMIT 1;",
    "Employees working in all departments": "SELECT e.EmployeeID AS PersonID, p.LastName, p.FirstName FROM EmployeeDepartmentAssignment e JOIN Person p ON e.EmployeeID = p.PersonID GROUP BY e.EmployeeID, p.LastName, p.FirstName HAVING COUNT(DISTINCT e.DepartmentID) = (SELECT COUNT(*) FROM Department);",
    "Interviewees selected (name and email)": "SELECT CONCAT(p.FirstName, ' ', p.LastName) AS IntervieweeName, p.Email AS EmailAddress FROM Interview i JOIN Person p ON i.CandidateID = p.PersonID WHERE EXISTS (SELECT 1 FROM InterviewGrade ig WHERE ig.InterviewID = i.InterviewID AND ig.Grade >= 70);",
    "Interviewees (name, phone, email)": "SELECT p.FirstName, p.LastName, ph.PhoneNumber FROM Person p JOIN PhoneNumber ph ON p.PersonID = ph.PersonID JOIN InterviewGrade ig ON p.PersonID = ig.InterviewID;",
    "Employee with highest average salary": "SELECT p.PersonID, p.FirstName, p.LastName FROM Person p JOIN Salary s ON p.PersonID = s.EmployeeID GROUP BY s.EmployeeID ORDER BY AVG(s.Amount) DESC LIMIT 1;",
    "Vendor supplying 'Cup' (lowest price)": "SELECT v.VendorID, v.Name AS VendorName FROM Vendor v JOIN VendorPart vp ON v.VendorID = vp.VendorID JOIN Part p ON vp.PartID = p.PartID WHERE p.PartName = 'Cup' AND p.Weight < 4 AND vp.Price = (SELECT MIN(vp2.Price) FROM VendorPart vp2 JOIN Part p2 ON vp2.PartID = p2.PartID WHERE p2.PartName = 'Cup' AND p2.Weight < 4);"
}

    if request.method == "POST":
        action = request.form["action"]

        if action == "connect":
            # Store connection details in the session
            session["host"] = request.form["host"]
            session["port"] = request.form["port"]
            session["user"] = request.form["user"]
            session["password"] = request.form["password"]
            session["database"] = request.form["database"]
            success_message = "Connected to the database."

        elif action == "disconnect":
            session.clear()
            success_message = "Disconnected from the database."

        elif action == "show_tables":
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 5")
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    data.append({"table_name": table_name, "columns": columns, "rows": rows})
                cursor.close()
                success_message = "Tables and data fetched successfully."
            except mysql.connector.Error as err:
                error_message = f"Error: {err}"
            finally:
                if "connection" in locals() and connection.is_connected():
                    connection.close()

        elif action == "reset":
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                for statement in RESET_SQL.split(";"):
                    if statement.strip():
                        cursor.execute(statement)
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                connection.commit()
                cursor.close()
                success_message = "Database reset and data reinserted successfully."
            except mysql.connector.Error as err:
                error_message = f"Error: {err}"
            finally:
                if "connection" in locals() and connection.is_connected():
                    connection.close()

        elif action == "execute_query":
            selected_query = request.form.get("query")  # Get the selected query
            try:
                connection = get_connection()
                cursor = connection.cursor()
                query = predefined_queries[selected_query]
                cursor.execute(query)
                query_results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                log_query(query, query_results)
                data = [{"columns": columns, "rows": query_results}]
                cursor.close()
                success_message = "Query executed successfully."
            except mysql.connector.Error as err:
                error_message = f"Error executing query: {err}"
            finally:
                if "connection" in locals() and connection.is_connected():
                    connection.close()

    return render_template(
        "index.html",
        data=data,
        predefined_queries=predefined_queries,
        selected_query=selected_query,  # Pass selected query to template
        error_message=error_message,
        success_message=success_message,
        connected=("host" in session),
    )

def get_connection():
    """Helper function to establish a connection using session data."""
    if "host" in session:
        return mysql.connector.connect(
            host=session["host"],
            port=int(session["port"]),
            user=session["user"],
            password=session["password"],
            database=session["database"]
        )
    else:
        raise mysql.connector.Error("Database connection not initialized.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
