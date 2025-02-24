import psycopg2

db_url = "your database key"
try:
    connection = psycopg2.connect(db_url)
    print("Database connection established successfully.")
    connection.close()
except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")