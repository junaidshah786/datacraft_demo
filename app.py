from controller.generate_insights import get_texual_insights
from controller.connect_to_sql import database_connection, fetch_data
from controller.generate_answers_gpt import convert_question_to_sql_query,convert_schema_to_sql_query_suggestions
import controller.excel_to_db as xlsxx
from controller.visualization import visualization, get_answer_for_visualization
import streamlit as st
import openai
import time 
import traceback
import logging
logging.basicConfig(level=logging.DEBUG)
import re
import pandas as pd


openai.api_key = st.secrets["openai_api_key"]

def validate_dbname_naming_convention(name):
    if not name or not name[0].isalpha():
        return False

    return bool(re.match(r'^[a-zA-Z0-9_]*$', name))

def initialize_session_state():
    session_state_vars = ['db_connection', 'connect_to_database', 'schema', 'xls_connection', 'host', 'user', 'database', "settings",'cleaning_strategy']

    for var in session_state_vars:
        if var not in st.session_state:
            st.session_state[var] = []

def download_excel():
    file_path = 'files/DummyData.xlsx'
    with open(file_path, 'rb') as f:
        data = f.read()
    return data     



def upload_excel_file():
    if st.session_state['schema'] == []:
        uploaded_file = st.sidebar.file_uploader("Choose a file")
        if uploaded_file is None:
            if st.sidebar.button('Download Excel file', help='''A dummy Excel file can be downloaded here.'''):
                    excel_data = download_excel()
                    st.sidebar.download_button(label='Click Here :inbox_tray:', data=excel_data, file_name='sample_excel.xlsx', key='download_button', help='Click to download')
    
        if uploaded_file is not None:
            db_name = st.sidebar.text_input("Project name: ")
            st.session_state['cleaning_strategy'] = st.sidebar.radio(
            "Would you like to clean data before submitting?",
            ["Yes"],
            index=None,
        )
           
            if validate_dbname_naming_convention(db_name):
                submit_button = st.sidebar.button("Submit")
            else:
                submit_button = st.sidebar.button("Submit", disabled=True, help='''Make sure you have choosen a cleaning strategy, also try changing project name.''')
        

            if submit_button : 
                with st.spinner('Your Excel file is in the oven.'):
                    try:
                        xls_connection, schema = xlsxx.excel_to_mysql(uploaded_file, db_name,st.session_state['cleaning_strategy'])
                    except Exception as e:
                        st.error(f"An error occurred: Try changing project name.")
                        return
                    st.session_state['schema'] = schema

                    st.session_state['xls_connection'] = xls_connection

                    st.toast('File uploaded successfully.', icon='🎉')

    
# def clear_history():
#     session_state_vars = ['db_connection', 'connect_to_database', 'schema', 'xls_connection', 'host', 'user', 'database','warning_displayed_cleaning','cleaning_strategy', "sql_query_suggestions"]
    

#     for var in session_state_vars:
#         # if var not in st.session_state:
#         st.session_state[var] = []

def connect_to_sql():
    if st.session_state['schema'] == []:
        with st.sidebar:
            st.subheader("Connection Settings")
            st.session_state['host'] = st.text_input("MySQL Host:", value="70.98.204.225")
            st.session_state['user'] = st.text_input("MySQL Username:", value="root")
            st.session_state['password'] = st.text_input("MySQL Password:", type="password", value="BJe11cybiR7WpXgfmQJs")
            st.session_state['database'] = st.text_input("MySQL Database Name:")


        connect_to_database= st.sidebar.button("Connect", key='check_connection')
        
        if st.session_state['host'] and st.session_state['user'] and st.session_state['database'] and connect_to_database:
            db_connection, schema = database_connection(
                st.session_state['host'],
                st.session_state['user'],
                st.session_state['password'],
                st.session_state['database']
            )
            st.session_state['schema'] = schema
            st.session_state['db_connection'] = db_connection


def main():
    try:
        # st.title(":rainbow[Data Craft]")
        st.title("Data Craft")
        st.markdown(
            """
            <style>
                .stButton>button {
                background-color: #000000;
                color: #FFFFFF;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        initialize_session_state()

        DB_option = st.sidebar.selectbox(
            "How would you like to be connected?",
            ("Upload Excel File", "Connect to SQL", "Connect to MongoDB"),
            index=None,
            placeholder="Select DB...",
            key="DB_selectbox"  # Add a unique key to the selectbox
            
        )    
        



        
        if st.session_state['cleaning_strategy'] == 'manual':
            if 'warning_displayed_cleaning' not in st.session_state:
                st.session_state.warning_displayed_cleaning = True
                
                success_message = st.sidebar.warning("Make sure that the Data in the Excel sheet is clean.")
                time.sleep(4)   
                success_message.empty() 

        
        if DB_option is None:    
            if 'sql_query_suggestions' in st.session_state:
                del st.session_state.sql_query_suggestions
            session_state_vars = ['db_connection', 'connect_to_database', 'schema', 'xls_connection', 'host', 'user', 'database','warning_displayed_cleaning','cleaning_strategy']
            

            for var in session_state_vars:
                st.session_state[var] = []

            
        if DB_option == 'Upload Excel File': 
            upload_excel_file()
                
 

        elif DB_option == 'Connect to SQL':
            if st.session_state["db_connection"] == []:
                print("\n\n called for new connection")
                
                connect_to_sql()    

        elif DB_option == 'Connect to MongoDB':
            st.success('Connected to MongoDB')

#########################################################################check this xls
        if st.session_state['xls_connection']:
            st.session_state['db_connection'] = st.session_state['xls_connection']
            

        if st.session_state['db_connection']:
            # st.write('schema: ',st.session_state['schema'])
            st.markdown("---")
            with st.form(key='my_form', clear_on_submit=False):  
                # Check if the user_query key exists in session_state, if not set to an empty string
                user_query = st.session_state.get('user_query', '')
                user_query = st.text_area("Enter your query:", value=user_query, height=70, max_chars=1000)

                submit_button = st.form_submit_button(label='Draft Insights')     
                response_type = st.selectbox("Select Chart Type", ["Text", "Tabular", "Graph/chart"]) 
                if response_type=='Graph/chart':
                    chart_type = st.selectbox("Select Chart Type", ["bar", "line", "scatter"])  # Add more chart types as needed
                
                # st.session_state['show_tabular']= st.radio(
                # "Show data in tabular form?", ["Yes"], index=None)
                
            if "sql_query_suggestions" not in st.session_state:
                st.session_state['sql_query_suggestions'] = convert_schema_to_sql_query_suggestions(st.session_state['schema'])
            
            

            if submit_button and user_query:
                with st.spinner('Generating an Answer, Please wait...'):
                    sql_query = convert_question_to_sql_query(user_query, st.session_state['schema'])  
            
                    print("generated query:",sql_query,'fghjk')
                    # st.success(sql_query)
                    if sql_query != " Please enter the relevent query ! ":
                        print("inside please enter ")
                        with st.sidebar.expander("Generated SQL Query", expanded=False):
                            st.success(sql_query)
                        # st.write('db connection 112: ', st.session_state['db_connection'])
                        # it fetches the answer using the sql command geenrated
                        data, dataframe_for_table = fetch_data(st.session_state['db_connection'], sql_query)
                        print("data: ",data)
                        if data == 500:
                            return
                        if any(element is None for element in data[0]):
                            st.error("No data found, Please recheck your query.")
                            return
                        
                        elif response_type== 'Tabular':
                            # for i in dataframe_for_table :
                            #     print('\ndataframe_for_table:',i)
                            st.table(dataframe_for_table)
                            return
                        elif response_type == 'Text':
                        # print('data fetched:', data)
                        # gives an answer in user friendly format using LLM
                            
                            processed_data = get_texual_insights(user_query, data)
                            st.success(processed_data)
                            
                        elif response_type == 'Graph/chart':
                            query_nature = get_answer_for_visualization(sql_query)
                            print("query nature : ",query_nature)
                            if "Insight" in query_nature:
                                processed_data = get_texual_insights(user_query, data)
                                st.success(processed_data)

                            else:                                
                                visualization(data, query_nature,chart_type)

                        # st.write(query_nature)
                        # if any(element is None for element in data[0]):
                        #     st.error("No data found, Please recheck your query.")
                        # else:
                        # if "Insight" in query_nature:
                        #     processed_data = get_texual_insights(user_query, data)
                        #     st.success(processed_data)

                        # else:                                
                        #     visualization(data, query_nature,chart_type)
                                
                    else:
                        st.warning("Please enter the relevant query!")
            st.title('Suggested queries')
            st.text(st.session_state["sql_query_suggestions"])

    except Exception as e:
        stack_trace = traceback.format_exc()
        st.error(f"An error occurred: {str(e)}")
        print(f"ERROR OCCURRED: {e}\n{stack_trace}")

if __name__ == "__main__":
    main()
