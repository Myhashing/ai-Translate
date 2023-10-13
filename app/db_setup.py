import mysql.connector

db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password=''
)

cursor = db_connection.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS python")

# Use the new database
cursor.execute("USE python")

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        post_id INT AUTO_INCREMENT PRIMARY KEY,
        content TEXT,
        translated_content TEXT,
        status VARCHAR(10)
    )
""")

db_connection.commit()
cursor.close()
db_connection.close()
