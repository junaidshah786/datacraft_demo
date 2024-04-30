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
    #print("CONTROL DATA :",control_data)
    #form_schema["form_id"] = form_id
    for control_items in control_data:
        #print("control items :  ",control_items)
        id = control_items.get("id")
        control_type = control_items.get("controlType")
        key = control_type + '_' + str(id)
        value = control_items.get("fieldName")
        form_schema[key] = value

    #labels = controls.find({}, {'fieldName': 1})
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
    mysql_password = "atm8019atM@"  # Replace with your MySQL password
    mysql_database = "mongo_formssss"  # Replace with your MySQL database name
    
    # mysql_host = "localhost"
    # mysql_user = "root"  # Replace with your MySQL username
    # mysql_password = "Andleeb.mysql@123"  # Replace with your MySQL password
    # mysql_database = "mongo_forms"  # Replace with your MySQL database name
     # Create a MySQL connection
    mysql_conn = create_sql_connection(mysql_database, mysql_user, mysql_password, mysql_host)
    print("SQL CONNECTION COMPLETED")
    if mysql_conn is None :
        return

    elif mysql_conn == "Database name already in use !":
        return "Database name already in use !"

    else:
        mysql_cursor = mysql_conn.cursor()
        
    table_name = 'Form_Entries'
    # Create SQL table and insert data
    create_table_query = f"CREATE TABLE {table_name} ("
    insert_data_query = f"INSERT INTO {table_name} VALUES ("

    # Build the CREATE TABLE query
    #skip_first = True
   
    for key, value in form_schema.items():
        # if skip_first:
        #     skip_first = False
        #     continue
        create_table_query += f"{value} VARCHAR(255), "
            #insert_data_query += f"'{value}', "

    create_table_query = create_table_query.rstrip(", ") + ");"
    #insert_data_query = insert_data_query.rstrip(", ") + ");"

    # Create table
    mysql_cursor.execute(create_table_query)
    mysql_conn.commit()
    print("sql db created!")
    return mysql_conn,table_name

def get_data_from_form_entries(db,form_schema,form_id,mysql_conn,table_name):
    form_data=[]
    single_record = []
    form_entries = db.form_entries
    mysql_cursor = mysql_conn.cursor()
    form_data_query= '{"form_id":"' + form_id +'"}'
    schema = list(form_schema.values())
    print("SCHEMA : ",schema)
    insert_data_query = f"INSERT INTO {table_name}({', '.join(schema)}) VALUES"


    form_data_query = eval(form_data_query)
    entries = db.form_entries.find(form_data_query)
    print("FORM SCHEMA : ",form_schema)
    for entry_items in entries:
        for key in form_schema:
           single_record.append(entry_items.get(key))
           
        print("SINGLE RECORD: ",single_record)
        form_data.append(single_record)
        single_record=[]
        #print("FORMDATA",form_data)
        # Iterate over the list of lists and construct the VALUES part of the query
        # Iterate through data rows
    for data_row in form_data:
        # Generate the values part of the query
        values = [f"'{value}'" if value is not None else 'NULL' for value in data_row if value is not None]

        # Print debugging information
        print(f"Values: {values}")
        print(f"Number of Values: {len(values)}")
        print(f"Number of Columns: {len(schema)}")

        # Check if the number of values matches the number of columns
        if len(values) == len(schema):
            insert_data_query += "(" + ", ".join(values) + "), "
        else:
            print("Number of values doesn't match the number of columns.")

        # Remove the trailing comma and execute the query
        insert_data_query = insert_data_query.rstrip(', ')
        print('insert_data_query: ',insert_data_query)
        mysql_cursor.execute(insert_data_query)

        
    print(f"Table '{table_name}' created and data inserted.")




mongo_uri = "mongodb+srv://lelafeprojs:jnU61BQJbxxQEEbA@cluster0.faiklh9.mongodb.net/?retryWrites=true&w=majority"
form_id = "65aa1471172900009400700a"

db ,form_schema = connect_to_mongo(mongo_uri,form_id)
print(db)
mysql_conn,table_name = define_sql_database(form_schema)
get_data_from_form_entries(db,form_schema,form_id,mysql_conn,table_name)