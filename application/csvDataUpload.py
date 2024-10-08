import csv
import pymysql


# Function to read CSV file and insert rows into MySQL database
def insert_data_from_csv(csv_file, table):
    # MySQL database connection parameters
    host = 'localhost'
    username = 'jkwon247'
    password = 'Test!234'
    #database = 'team5_db'
    database = 'team5_db_test'

    # Connect to MySQL database
    connection = pymysql.connect(host=host,
                                 user=username,
                                 password=password,
                                 db=database,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        # Create cursor
        cursor = connection.cursor()

        # Read CSV file
        with open(csv_file, 'r') as file:
            csv_data = csv.reader(file)
            next(csv_data)  # Skip header row if it exists

            # Iterate over each row in CSV
            for row in csv_data:
                # Construct SQL query to insert row into table
                if table == 'Universities':
                    sql_query = "INSERT INTO Universities (uni_name, email, phone, password, address, city, state, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                elif table == 'Sports':
                    sql_query = "INSERT INTO Sports (event_name, category, season, gender) VALUES (%s, %s, %s, %s)"
                elif table == 'Athletes':
                    sql_query = "INSERT INTO Athletes (firstName, lastName, gender) VALUES (%s, %s, %s)"
                elif table == 'AthleteSports':
                    sql_query = "INSERT INTO AthleteSports (athlete_id, sport_id, year, ranking) VALUES (%s, %s, %s, %s)"
                elif table == 'AthletesUniversities':
                    sql_query = "INSERT INTO AthletesUniversities (athlete_id, uni_id) VALUES (%s, %s)"
                elif table == 'Faculty':
                    sql_query = "INSERT INTO Faculty (university_id, firstName, lastName, email, password) VALUES (%s, %s, %s, %s, %s)"
                else:
                    print("Invalid table name.")
                    return

                cursor.execute(sql_query, row)

        # Commit changes to database
        connection.commit()
        print("Data inserted successfully")

    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()

    finally:
        # Close database connection
        connection.close()


# Example usage
if __name__ == "__main__":
    csv_file_name = input("Enter CSV file name: ")
    csv_file_path = "./csvFiles/" + csv_file_name
    table = input("Enter table name (Universities, Sports, Athletes, AthleteSports, or AthletesUniversities): ")

    insert_data_from_csv(csv_file_path, table)