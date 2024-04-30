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
                    


def get_texual_insights(sql_query,data):

    prompt = f"""
                Your role is to interpret and analyze the data in alignment with the requirements specified in the user query.\
                The response should not hold any specification of query and structure of data just the conclusion from the data\
                Provide a precise response.\      
                        
        ```{sql_query}``` 
        ```{data}```       
        
    """
    messages = [
      
        {"role": "system", "content": 'You are an expert Data Analyst.'},
        {"role": "user", "content": prompt}
    ]   


    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
        temperature=0,
    )
    
    return response.choices[0].message["content"]



