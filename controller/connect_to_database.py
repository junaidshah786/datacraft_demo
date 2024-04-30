import mysql.connector
from mysql.connector import Error
import pymongo
def connect_to_mongo(mongo_uri,form_id):
    form_schema = {}

    client = pymongo.MongoClient(mongo_uri)
    db = client.db_stagingqforms   
    controls = db.controls

    form_data_query= '{"form_id":"' + form_id +'"}'
   
    form_data_query = eval(form_data_query)
    control_data = db.controls.find(form_data_query)
   
    for control_items in control_data:
        
        id = control_items.get("id")
        control_type = control_items.get("controlType")

        if control_type == "name":
            if control_items.get("First_Name") == True:
                key = 'name_first' + '_' + str(id)
                value = 'name_first'
                form_schema[key] = value

            if control_items.get("Middle_Name") == True:
                key = 'name_middle' + '_' + str(id)
                value = 'name_middle'
                form_schema[key] = value

            if control_items.get("Last_Name") == True:
                key = 'name_last' + '_' + str(id)
                value = 'name_last'
                form_schema[key] = value

        elif control_type == "address":
                key = 'address_line1' + '_' + str(id)
                value = 'address_line1'
                form_schema[key] = value

                key = 'address_line2' + '_' + str(id)
                value = 'address_line2'
                form_schema[key] = value

                key = 'address_district' + '_' + str(id)
                value = 'address_district'
                form_schema[key] = value

                key = 'address_state' + '_' + str(id)
                value = 'address_state'
                form_schema[key] = value

                key = 'address_zip' + '_' + str(id)
                value = 'address_zip'
                form_schema[key] = value
               
                key = 'address_countrySelected' + '_' + str(id)
                value = 'address_countrySelected'
                form_schema[key] = value

        else:
            key = control_type + '_' + str(id)
            value = control_items.get("label")
            value = value.replace(" ", "")
            form_schema[key] = value

    print("SCHEMA:",form_schema)
    return(db,form_schema)

def create_sql_connection(sql_database, user, password, host='localhost'):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=sql_database
        )
        if connection.is_connected():
            print(f"The name {sql_database} is already in use !")
            return "Database name already in use !"
    except Error as e:
        # Check if the error is related to the database not existing
        if "Unknown database" in str(e):
            try:
                # If the database doesn't exist, create a new one
                connection = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password
                )
                cursor = connection.cursor()
                cursor.execute(f"CREATE DATABASE {sql_database}")
                print(f"Database '{sql_database}' created successfully.")
                connection.close()

                # Now, attempt to connect to the newly created database
                connection = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=sql_database
                )

                if connection.is_connected():
                    print(f"Connected to the database: {sql_database}")
                   
                    return connection

            except Error as e:
                print(f"Error creating or connecting to the database: {e}")
                return None

        else:
            print(f"Error: {e}")
            return None


def define_sql_database(form_schema): 
    mysql_host = "localhost"
    mysql_user = "root"  # Replace with your MySQL username
    mysql_password = "Andleeb.mysql@123"  # Replace with your MySQL password
    mysql_database = "mongo_forms"  # Replace with your MySQL database name
    
    mysql_conn = create_sql_connection(mysql_database, mysql_user, mysql_password, mysql_host)
  
    if mysql_conn is None :
        return

    elif mysql_conn == "Database name already in use !":
        return "Database name already in use !",None

    else:
        mysql_cursor = mysql_conn.cursor()
        
    table_name = 'Form_Entries'
    # Create SQL table and insert data
    create_table_query = f"CREATE TABLE {table_name} ("
 
    for key, value in form_schema.items():
        create_table_query += f"{value} VARCHAR(255), "
           

    create_table_query = create_table_query.rstrip(", ") + ");"
       # Create table
    mysql_cursor.execute(create_table_query)
    mysql_conn.commit()
    print("SQL CONNECTION COMPLETED, DATABASE CREATED !")
    return mysql_conn,table_name