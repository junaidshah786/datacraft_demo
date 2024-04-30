import mysql.connector
import streamlit as st
import time
import pandas as pd




# Function to establish a database connection
def database_connection(host, user, password, database):
    schema = {}
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            success_message_sql = st.sidebar.success("Connection Successful.")
            time.sleep(2)
            success_message_sql.empty()
            
            cursor = connection.cursor()

            # Define your SQL query
            schema_query = f""" SELECT table_name, column_name
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE table_schema = '{database}';"""

            cursor.execute(schema_query)

            # Fetch all rows
            rows = cursor.fetchall()

            # Display the fetched data using st.write
            # with st.sidebar:
            #     st.subheader("Schema:")
            for row in rows:
                table_name, column_name = row
                if table_name not in schema:
                    schema[table_name] = []
                schema[table_name].append(column_name)
            #st.write(schema)
            return connection,schema

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Function to fetch data from the database
def fetch_data(connection,query):
    try:
        cursor = connection.cursor()
        print('query: ',query)
        cursor.execute(query)
        # Fetch column names
        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        # rows=list(rows)
        # rows=rows.tolist()
        # print('roww type:',type(rows), 'column_names: ',type(column_names))
        # print('rows:',rows)
        # st.write('rows:',rows)    
        #st.subheader("Fetched data:") 
        
        formated_rows = []
        # Combine column names and rows into the desired format
        for i in rows:
            formated_rows.append(list(i))
        print("FORMATED ROWS============",formated_rows)
        result_data = [column_names] +  formated_rows
        print("\n\n result data: ",result_data)# Combine column names and rows into the desired format
        if rows:
            # st.write('rows is not empty data: ',rows) 
            # Create a DataFrame with fetched data and column names
            df = pd.DataFrame(rows, columns=column_names)
            

            return rows,df
        else:
            st.error(f"Error: Invalid query! Please provide correct information.")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        
        
        
        
        
        
        
    