import re
import openai
import streamlit as st
import json

with open('./config.json', 'r') as file:
    config = json.load(file)


gpt_model= config['gpt_model']
openai.api_key = st.secrets["openai_api_key"]




def convert_question_to_sql_query(user_query,schema):
    print('schema:',schema)
    prompt = f"""You are a professional DataBase Adminstrator \
        You have to write the syntatically sementically correct sql query \
        the sql query should be transformed from the customer_query \
        Scrictly make sure the attributes and table names to be used for formulating the sql query should be same as the provided schema\
        schema is a dictionary with table names as keys and table columns as their respective values \
        schema can have a single table only or multiple relational tables\
        while formulating the sql query consider the principles of relational database concepts\
        append a semicolon (;)at the end of sql query.\
        if the customer_query doesn't sound like a query, say "Please enter the relevent query !".
        make sure the column names are choosen from the provided schema only.
        The response should be the sql query only, no additional information like sql etc, consider te below example as reference: SELECT LastName, FirstName FROM employees WHERE EmployeeID = 1;
        
        ```{user_query}```        
        ```{schema}```
    """
    messages = [
        {"role": "system", "content": prompt}
    ]
    

    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]
  
  
def convert_question_to_sql_query(customer_query, schema):
    # openai.api_key = openai_api_key
    # print('schema:',schema)
    prompt = f'''the user will provide you a question related to a database and its schema \
        your task is to  generate an SQL query that retrieves relevant information based on this question\n\nQuestion:```{customer_query}```\n\
        Strictly make sure the attributes and table names to be used for formulating the sql query should be same as the provided schema\nSchema:```{schema}```\n\
        schema is a dictionary with table names as keys and table columns as their respective values \
        schema can have a single table only or multiple relational tables\
        while formulating the sql query strictly consider the principles of relational database concepts.
        In case the user question is irrelevant, simply say "Please enter a relevant query !"
        make sure the column names are choosen from the provided schema only. if the question includes any column name not present in the schema, try finding similar column names from schema and use it instead in the sql query \
        response format example: 'SELECT * FROM employees;'''
    # In case you re not able to generate sql query from the provided information, say "Please enter a relevant query !".\
   
    messages = [
        {"role": "system", "content": " Do not add any preamble, give pure sql query."},
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    res = response.choices[0].message["content"]
    # logging.info(f"SQl query default: {res}")
    print(f"SQl query default: {res}")
    # Remove the sql tag using regular expressions
    clean_sql_query = re.sub(r"sql\s*", "", response.choices[0].message["content"])
    return clean_sql_query

  


def convert_schema_to_sql_query_suggestions(schema):
    print('\n\n schema for suggestions generation:',schema)
    prompt = f"""
        generate five questions based on the given schema: Schema: ```{schema}```
        The questions should be such that it can be easily converted into a mysql query.
        The questions to be generated should be based on the provided schema only.
        Do not make complex questions.
        One Question should be such that its sql query response includes  x-axis and y-axis example: number of orders in each country.

        the response shoud be in a list format only.
        
        Schema: ```{schema}```
    """
    messages = [
        {"role": "system", "content": 'You are a professional DataBase Administrator who generates questions  based on given schema of a sql Database.'},
        {"role": "user", "content": prompt}
    ]
    

    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]
    
