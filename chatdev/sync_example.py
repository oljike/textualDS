import asyncio
import json
from openai import OpenAI
import pandas as pd


def send_req(client, system_message, message, task_number):
    stored_messages = [{"role": "system", "content": system_message}]
    stored_messages.append({"role": "user", "content": message})

    response_format = {"type": "json_object"}
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format=response_format,
        messages=stored_messages,
        seed=42)
    response = response.choices[0].message.content
    print(f"Task {task_number} completed.")
    return response



def main():
    with open('api.json') as f:
        data = json.load(f)
    api_key = data['openai_api']
    client = OpenAI(api_key=api_key)

    system_message = '''You are an expert in data science and Python. You have been provided with a DataFrame for analysis.
    The DataFrame is already loaded and is called df.
    The DataFrame contains the following columns and their corresponding descriptions: {columns}.
    You are given a python coding task which is a sub-task of a bigger plan. Your goal is to write python code to solve the task.
    Do not skip any step or leave as comment.
    If the code includes visualizations, refrain from displaying them using a graphical user interface.
    Instead, convert visualizations to Pillow images and return as function output.
    IMPORTANT: Return a valid JSON object in the following format: {format}.'''

    # system_message = '''you are a helpful assistant
    # Return a valid JSON object in the following format: {format}.'''

    format = '''{"explanation": "the explanation of the code", "answer":  "python code here"}'''
    df = pd.read_csv('../datasets/dataanalytics/market_basket_dataset.csv')
    system_message = system_message.format(columns=', '.join(df.columns), format=format)
    # system_message = system_message.format(format=format)

    # message = 'name the largest city in the world'
    message = 'name 10 most popular items sold by the store'

    output = []
    for i in range(10):
        output.append(send_req(client, system_message, message, i + 1))

    print("Starting tasks...")
    print("All tasks completed.")
    print(output)


if __name__ == "__main__":
    main()
