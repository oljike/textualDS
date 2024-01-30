import os
import pandas as pd
# os.environ["OPENAI_API_KEY"] = "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"
from openai import OpenAI
import json

class Explorer:

    def __init__(self, df):
        """
        The goal of this class it make data exploration. It accepts the description of the dataset if it exists
        Also, it parses the columns and makes description of them semantically.
        It also can parse the some random table cells to understand what can be expected in there.

        """
        self.columns = df.columns
        with open('chatdev/api.json') as f:
            data = json.load(f)
            print(data)
            self.api_key = data['openai_api']

        self.client = OpenAI(api_key=self.api_key)

    def run(self, desc):

        init_desc = self.init_desc(desc)

        return init_desc


    def init_desc(self, desc=None):

        prefix = '''Answer the following questions:
        Explain the what do the following columns represent: {columns}. 
        '''

        input = f"{prefix.format(desc=desc, columns=self.columns)}"
        interpretation = self.client.chat.completions.create(
                                                   model="gpt-3.5-turbo",
                                                   messages=[
                                                       {"role": "system", "content": "You are a specialist in data. Your goal is to explain the given table."},
                                                       {"role": "user", "content": input}])
        interpretation = interpretation.choices[0].message.content
        return interpretation


    def get_questions(self,  desc):

        prefix = '''Based on the following description: {desc} of the dataframe, generate most important analysis 
        questions which can be addressed to data scientist and evaluated using Python and data analysis techniques.
        You don't have any other data sources, so the above questions can be answered using only provided columns.
        '''
        output_format = 'The output format should be the following JSON: {question number: question, ...}'

        input = f"{prefix.format(desc=desc)}" + output_format
        interpretation = self.client.chat.completions.create(
                                                   model="gpt-3.5-turbo",
                                                   # response_format={"type": "json_object"},
                                                   messages=[
                                                       {"role": "system", "content": "You are a specialist in data designed to output JSON."},
                                                       {"role": "user", "content": input}])

        interpretation = interpretation.choices[0].message.content
        return interpretation