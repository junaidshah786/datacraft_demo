import pandas as pd
import mysql.connector
from mysql.connector import Error
import streamlit as st
import re
import logging
import json

logging.basicConfig(level=logging.DEBUG)

with open('./config.json', 'r') as file:
    config = json.load(file)


user= config['user']
password= config['password']
host= config['host']


# Function to create a MySQL connection
    
def create_connection(database, user, password, host='localhost'):    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            print(f"The name {database} is already in use !")
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
                cursor.execute(f"CREATE DATABASE {database}")
                print(f"Database '{database}' created successfully.")
                connection.close()

                # Now, attempt to connect to the newly created database
                connection = mysql.connector.connect(
                    host=host,
                    user=user,
                    password=password,
                    database=database   
                )

                if connection.is_connected():
                    print(f"Connected to the database: {database}")
                    
                    
                   
                    return connection

            except Error as e:
                print(f"Error creating or connecting to the database: {e}")
                return None

        else:
            print(f"Error: {e}")
            return None
        
        


def infer_data_type_auto(series, majority_threshold=0.9):
    # Function to check if a string represents a numeric value
    def is_numeric(value):
        return bool(re.match(r'^\s*-?\d+(\.\d+)?\s*$', str(value)))

    # Function to check if a string represents a date-only value
    def is_date(value):
        return bool(re.match(r'^(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})$', str(value)))

    # Function to check if a string represents a datetime value
    def is_datetime(value):
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$', str(value)))

    # Function to check if a string represents a boolean value
    def is_boolean(value):
        return str(value).lower() in ['true', 'false']

    # Function to check if a string represents a numeric value with a dollar sign
    def is_dollar_numeric(value):
        return bool(re.match(r'^\s*\$\s*\d+(\.\d+)?\s*$', str(value)))

    # Count the number of values for each data type
    numeric_count = series.apply(is_numeric)
    date_count = series.apply(is_date)
    datetime_count = series.apply(is_datetime)
    boolean_count = series.apply(is_boolean)
    dollar_numeric_count = series.apply(is_dollar_numeric)
    text_count = ~(numeric_count | date_count | datetime_count | boolean_count | dollar_numeric_count)

    total_count = len(series)

    # Calculate percentages of values for each data type
    numeric_percentage = numeric_count.sum() / total_count
    date_percentage = date_count.sum() / total_count
    datetime_percentage = datetime_count.sum() / total_count
    boolean_percentage = boolean_count.sum() / total_count
    dollar_numeric_percentage = dollar_numeric_count.sum() / total_count
    text_percentage = text_count.sum() / total_count

    # Create a dictionary of data type percentages
    type_percentages = {
        'NUMERIC': numeric_percentage + dollar_numeric_percentage,
        'DATE': date_percentage,
        'DATETIME': datetime_percentage,
        'BOOLEAN': boolean_percentage,
        'TEXT': text_percentage
    }

    print("type_percentages:", type_percentages)

    # Infer the data type based on the majority percentage
    inferred_type = max(type_percentages, key=type_percentages.get)

    # Check if the majority percentage exceeds the threshold
    if type_percentages[inferred_type] >= majority_threshold:
        data_type = inferred_type
    else:
        # Default to TEXT if the majority data type is not recognized
        data_type = 'TEXT'

    print("returned data type:", data_type)

    return data_type

def infer_data_type(series):
    # Infer the data type of the column based on the first non-null value
    if pd.api.types.is_numeric_dtype(series):
        data_type = 'NUMERIC'   
    elif pd.api.types.is_float_dtype(series):
            data_type = 'FLOAT'
    elif pd.api.types.is_datetime64_any_dtype(series):
        data_type = 'DATETIME'
    elif pd.api.types.is_string_dtype(series):
        # Check for string (TEXT or VARCHAR based on length)
        # max_length = series.str.len().max()
        # data_type = f"VARCHAR({min(max_length, 255)})"
        print('stringss')
        
        # Check if the data contains a pattern resembling a dollar sign and numeric values
        if series.str.contains(r'\$\s*\d+', na=False).any():
            data_type = 'NUMERIC'
        else:
            data_type = 'TEXT'

        # data_type = 'TEXT'
        

    elif pd.api.types.is_bool_dtype(series):
        data_type = 'BOOLEAN'   
    else:
        # Default to TEXT if the data type is not recognized
        data_type = 'TEXT'
        
    print(f"Column data type: {data_type}")
    return data_type





sql_keywords = [
    'DATABASE','SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'JOIN',
    'UNION', 'INSERT', 'UPDATE',
    'DELETE', 'CREATE', 'ALTER', 'DROP', 'TABLE', 'VIEW', 'INDEX', 'PRIMARY',
    'FOREIGN', 'KEY', 'CONSTRAINT', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN',
    'IS', 'NULL', 'ASC', 'DESC', 'AS', 'DISTINCT', 'ON', 'HAVING', 'LIMIT',
    'OFFSET', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'UPPER', 'LOWER', 'CASE',
    'WHEN', 'THEN', 'ELSE', 'END', 'JOIN', 'INNER', 'OUTER', 'LEFT', 'RIGHT',
    'FULL', 'ALL', 'ANY', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
]

def is_dollar_numeric(value):
    return bool(re.match(r'^\s*\$\s*\d+(\.\d+)?\s*$', str(value)))

def is_sql_keyword(word):
    return word.upper() in sql_keywords

def clean_column_name(col):
    # Remove leading and trailing spaces
    cleaned_col = col.strip()
    
    # Replace spaces with underscores
    cleaned_col = cleaned_col.replace(" ", "_")
    
    # Replace special characters with underscores
    cleaned_col = re.sub(r'[^a-zA-Z0-9_]', '', cleaned_col)
    
    # Check if the cleaned column name is an SQL keyword
    if is_sql_keyword(col):
        cleaned_col = f"{col}_"
    
    # if iskeyword(cleaned_col.upper()):
    #     cleaned_col = f"{cleaned_col}_"
    
    return cleaned_col

# Function to create tables and insert data
def excel_to_mysql(excel_file, database,cleaning_strategy):
    
    # user = 'root'
    # password = 'atm8019atM@'
    # host = 'localhost'
    
    # user = 'root'
    # password = 'BJe11cybiR7WpXgfmQJs'
    # host = '70.98.204.225'
    schema = {}
    # Read Excel file into a dictionary of DataFrames
    xls_data = pd.read_excel(excel_file, sheet_name=None)

    # Create a MySQL connection
    connection = create_connection(database, user, password, host)
    if connection is None :
        return

    elif connection == "Database name already in use !":
        return "Database name already in use !"
    
    else:   
        try:
            cursor = connection.cursor()

            # Iterate through sheets and create tables
            for sheet_name, sheet_data in xls_data.items():
                
                # Use sheet name as table name (you may need to sanitize the sheet names)
                table_name = sheet_name.lower().replace(" ", "_")
                print(f"Creating table '{table_name}'")

                cleaned_column_names = [clean_column_name(col) for col in sheet_data.columns]
                print("cleaned_column_names RE:", cleaned_column_names)
                # if cleaning_strategy=='manual':
                #     column_types = {col: infer_data_type(sheet_data[col]) for col in sheet_data.columns}
                #     print("\n\nColumn Types:", column_types)
                if cleaning_strategy == 'Yes' :
                    column_types = {col: infer_data_type_auto(sheet_data[col]) for col in sheet_data.columns}
                    print("\n\nColumn Types:", column_types)
                else:
                    column_types = {col: infer_data_type(sheet_data[col]) for col in sheet_data.columns}
                    print("\n\nColumn Types:", column_types)                   
                
                # Create the CREATE TABLE query
                create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'`{col}` {col_type}' for col, col_type in zip(cleaned_column_names, column_types.values())])})"
                print("create_table_query: ", create_table_query)
                cursor.execute(create_table_query)
                print(f"Table '{table_name}' created")

                # Iterate through sheets again and insert data into tables
                if cleaning_strategy == 'Yes':                 
                    
                    for _, row in sheet_data.iterrows():
                        for col, data_type in column_types.items():
                            if data_type == 'NUMERIC':
                                # If the data follows the pattern $ with numbers, remove $ and convert to numeric
                                if is_dollar_numeric(row[col]):
                                    # Remove $ and convert to numeric
                                    row[col] = pd.to_numeric(row[col].replace('$', ''), errors='coerce')
                                    if pd.notna(row[col]):
                                        row[col] = float(row[col])  # Convert to float (or int if no decimal places are expected)

                                else:
                                    row[col] = pd.to_numeric(row[col], errors='coerce')
                                    
                                    
                            elif data_type == 'DATE':
                                row[col] = pd.to_datetime(row[col], errors='coerce').date() if pd.notna(row[col]) else None
                            elif data_type == 'DATETIME':
                                row[col] = pd.to_datetime(row[col], errors='coerce')    
                            elif data_type == 'TEXT':
                                # You may add additional text handling logic if needed
                                pass
                            elif data_type == 'BOOLEAN':
                                row[col] = str(row[col]).lower() in ['true', '1', 'yes', 'false']

                        # Convert NaN values to None
                        row = row.where(pd.notna(row), None)

                        insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s']*len(row))})"
                        
                        # logging.debug(f"Insert query: ", insert_query, tuple(row))
                        print(f"Insert query: ", insert_query, tuple(row))
                        
                        cursor.execute(insert_query, tuple(row))

                        
                    connection.commit()
                    # logging.debug(f"Data inserted into '{table_name}' table")
                    print(f"Data inserted into '{table_name}' table")

                else:
                    # for sheet_name, sheet_data in xls_data.items():
                        for _, row in sheet_data.iterrows():
                            # print('table name: ',table_name,'row:',row)1  
                            
                            # Replace 'NA' or other non-numeric values with a default value, replaces empty cells with NAN, handles data type issues
                            # This is an anonymous (lambda) function that takes an argument x (each element of the Series) and returns 0 if the element is either NaN (pd.isna(x)) or an empty string (x == ''), and returns the original value x otherwise.
                            # row = row.apply(lambda x: 0 if pd.isna(x) or x == '' else x)
                            row = row.apply(lambda x: None if pd.isna(x) or x == '' else x)
                            
                            # Remove dollar sign only if the value follows the pattern of numbers followed by a dollar sign
                            row = row.apply(lambda x: re.sub(r'\$\s*', '', str(x)) if pd.notna(x) and isinstance(x, str) else x)


                            insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s']*len(row))})"   
        
                            print(f"Insert query: ",insert_query,tuple(row))

                            cursor.execute(insert_query,tuple(row))
                                
                        connection.commit()
                            # logging.debug(f"Data inserted into '{table_name}' table")
                            # print(f"Data inserted into '{table_name}' table")




            # Define your SQL query
            schema_query = f""" SELECT table_name, column_name
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE table_schema = '{database}';"""

            # Execute the query
            cursor.execute(schema_query)

            # Fetch all rows
            rows = cursor.fetchall()

            # Display the fetched data using st.write
            # with st.sidebar:
            # st.subheader("Schema:", schema)
            
            for row in rows:
                table_name, column_name = row
                if table_name not in schema:
                    
                    schema[table_name] = []
                schema[table_name].append(column_name)
            # st.write("Schema:", schema)
            # connection.commit()
            print("Data successfully imported into the MySQL database.")
            #excel_accepted = True
            return connection, schema
        except Error as e:
            print(f"Error: {e}")
            
            


        # finally:
        #     if connection.is_connected():
        #         cursor.close()
        #         connection.close()
        #         print("Connection closed.")

# Replace the placeholders with your MySQL details
#excel_file_path = 'd:\OFFICE\AI\DemandScience\DummyData.xlsx'
#database_name = 'sales_v1'
  # Use 'localhost' if MySQL is on the same machine, otherwise provide the IP address

#excel_to_mysql(excel_file_path, database_name)
