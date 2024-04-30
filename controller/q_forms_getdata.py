import mysql.connector
from mysql.connector import Error


def get_data_from_form_entries(db,form_schema,form_id,mysql_conn,table_name):
 
    form_data = []
    single_record = []
    form_entries = db.form_entries
    mysql_cursor = mysql_conn.cursor()
    form_data_query = '{"form_id":"' + form_id + '"}'
    schema = list(form_schema.values())
    print("SCHEMA : ", schema)
    insert_data_query = f"INSERT INTO {table_name} ({', '.join(schema)}) VALUES "

    form_data_query = eval(form_data_query)
    entries = db.form_entries.find(form_data_query)
    
    for entry_items in entries:
        for key in form_schema:
           
                print(f"Type of entry :  {(entry_items.get(key))}")
                if isinstance(entry_items.get(key), list):
                    for vals in range (len(entry_items.get(key))):
                        # Extract the 'value' from the list if present, otherwise use the original value
                        formatted_value = f"'{entry_items.get(key)[vals].get('value', entry_items.get(key)[vals])}'"
                        formatted_value = str(formatted_value).replace("'", "")
                        single_record.append(formatted_value)
                     
                else:
                    # Use the original value if it's not a dictionary
                    formatted_value = entry_items.get(key)
                
                    single_record.append(formatted_value)

       
        single_record = ['Unknown' if value is None else value for value in single_record]
        
        form_data.append(single_record)
        
        single_record = []
    
    print("FORM DATA: ", form_data)
    # Iterate over the list of lists and construct the VALUES part of the query
    for data_row in form_data:
        # Generate the values part of the query
        values = [f"'{value}'" if value is not None else 'NULL' for value in data_row if value is not None]
        
        if len(values) == len(schema):
            insert_data_query += "(" + ", ".join(values) + "), "
        else:
            print("Number of values doesn't match the number of columns.")

    # Remove the trailing comma and execute the query
    insert_data_query = insert_data_query.rstrip(', ')
    mysql_cursor.execute(insert_data_query)
    mysql_conn.commit()

    print(f"Data inserted into table '{table_name}'.")