import mysql.connector
from mysql.connector import Error
import connect_to_database as db_conn
import q_forms_getdata as forms


mongo_uri = "mongodb+srv://lelafeprojs:jnU61BQJbxxQEEbA@cluster0.faiklh9.mongodb.net/?retryWrites=true&w=majority"
form_id = "65b0ac27542b0000f600330e"

db ,form_schema = db_conn.connect_to_mongo(mongo_uri,form_id)
mysql_conn,table_name = db_conn.define_sql_database(form_schema)
if mysql_conn != "Database name already in use !":
    forms.get_data_from_form_entries(db,form_schema,form_id,mysql_conn,table_name)
    
    