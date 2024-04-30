import openai
import os
import pandas as pd
from dotenv import load_dotenv
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import json
# Load environment variables
load_dotenv()
# Set OpenAI API key
openai.api_key = os.getenv('openai_api_key')


with open('./config.json', 'r') as file:
    config = json.load(file)


gpt_model= config['gpt_model']

# def visualization(data,query_nature):

#     # Extracting data
#     x_axis, y_axis = zip(*data)
    
#     # print(f"X-AXIS : {x_axis} \nY-AXIS : {y_axis}")
#     process_labels = query_nature[1:-1].replace('"', '')
#     extracted_labels = process_labels.split(',')
#     horizontal_axis = extracted_labels[1].strip()
#     vertical_axis = extracted_labels[2].strip()
#     #df = pd.DataFrame({horizontal_axis: x_axis, vertical_axis: y_axis})
#     st.title(extracted_labels[3].strip())
#     # sns.set(style="whitegrid")
#     # plt.figure(figsize=(2,2))
#     # bar_plot = sns.barplot(x=horizontal_axis, y=vertical_axis, data=df, palette="viridis", hue=horizontal_axis, legend=False)
#     # bar_plot.set(xlabel=horizontal_axis, ylabel=vertical_axis, title=extracted_labels[3].strip())
#     # st.pyplot(plt)
#     # Create a dictionary for DataFrame
#     data_dict = {x: y for x, y in zip(x_axis, y_axis)}

#     # Display the bar chart using st.bar_chart
#     st.bar_chart(data=data_dict, use_container_width=True)
 

def visualization(data, response, chart_type):
    print("response: ", response)
    print("data: ", data)
    # Extracting data
    x_axis, y_axis = zip(*data)
    
    print("x axis: ",x_axis)    
    print("y axis: ",y_axis)

    process_labels = response[1:-1].replace('"', '')
    extracted_labels = process_labels.split(',')
    horizontal_axis = extracted_labels[1].strip()
    vertical_axis = extracted_labels[2].strip()

    st.title(extracted_labels[3].strip())

    if chart_type == "bar":
        # Create a dictionary for DataFrame
        data_dict = {x: y for x, y in zip(x_axis, y_axis)}
        print('type of data dict: ',type(data_dict))
        print(data_dict)
        # Display the bar chart using st.bar_chart
        st.bar_chart(data=data_dict, use_container_width=True)

    elif chart_type == "line":
        # Create a DataFrame
        df = pd.DataFrame({horizontal_axis: x_axis, vertical_axis: y_axis})
        print('type of data dict: ',type(df))
        print(df)
        # Display the line chart using st.line_chart
        st.line_chart(data=df.set_index(horizontal_axis), use_container_width=True)

    elif chart_type == "scatter":
        # Create a DataFrame
        df = pd.DataFrame({horizontal_axis: x_axis, vertical_axis: y_axis})
        print('type of data dict: ',type(df))
        print(df)    

        # Display the scatter plot using st.scatter_chart
        st.scatter_chart(data=df, x=horizontal_axis, y=vertical_axis, use_container_width=True)

    # elif chart_type == "pie":
    #     # Create a DataFrame
    #     df = pd.DataFrame({horizontal_axis: x_axis, vertical_axis: y_axis})

    #     # Display the pie chart using st.pie_chart
    #     st.pie_chart(data=df.set_index(horizontal_axis), use_container_width=True)

    # Add more elif conditions for other chart types



def get_answer_for_visualization(user_query):

    prompt = f""" you have to follow the specified instructions.\
                 
                Identify the nature of user_query\
                in what form the user_query needs to be answered\
                there can be 3 forms:
                1. Insight
                2. Graph
                3. Chart
            
                If the answer is graph or chart user the user_query to get two labels for x-axis and y-axis\
                append the labels at the end of response list.\
                
                Suggest a title for the graph/chart and append it at the end of the response list.
            
                The response should just be the list formed.

                Example:
                                        
                ["Chart","Countr","Count","Number of Customers in Each Country"]
                       

        ```{user_query}```        
        
    """
    messages = [
        {"role": "system", "content": 'You are an expert Data Scientist'},
        {"role": "user", "content": prompt}
    ] 

    response  = openai.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]
    



