
from flask import cli
import mysql.connector
from db_config import get_db_connection  # type: ignore

# CGI header for HTML output
print("Content-type: text/html\n")

# Form Data Receive Karna
form = cli.FieldStorage()
email = form.getvalue("email")
password = form.getvalue("password")

# Database Connection
conn = get_db_connection()
cursor = conn.cursor()

# Check if user exists
query = "SELECT is_verified FROM users WHERE email = %s AND password_hash = %s"
cursor.execute(query, (email, password))
result = cursor.fetchone()

cursor.close()
conn.close()

# HTML Response
print("<html><body>")
if result:
    if result[0]:  # is_verified == TRUE
        print("<h2>✅ Login Successful!</h2>")
    else:
        print("<h2>⚠️ Email not verified!</h2>")
else:
    print("<h2>❌ Invalid Email or Password!</h2>")
print("</body></html>")
