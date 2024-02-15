import sys
from os.path import abspath, join, dirname
app_path = abspath(join(dirname(__file__), '..'))
sys.path.append(app_path)

from chatdev.chat import Chat
from chatdev.agent import ChatAgent
from chatdev.explorer import Explorer
import json
import yaml
import types
import asyncio
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
matplotlib.use('agg')


class Flow:

    def __init__(self, data, columns_desc=None, ds_name=""):

        self.df = data
        self.columns = self.df.columns

        with open('chatdev/sys_msg.yaml', 'r') as file:
            sys_data = yaml.load(file, Loader=yaml.FullLoader)

        planner_format = '''{"description":"the description of the plan","plan":"the numbered list plan"}'''
        planner_sys_msg = sys_data['planner'].format(desc='', columns=columns_desc, format=planner_format)
        planner = ChatAgent('planner', planner_sys_msg, json_format=True, keep_history=True)

        json_format = '''{"explanation": "the explanation of the code", "function":  "def get_results(df):  python code here"}'''
        coder_sys_msg = sys_data['coder'].format(columns=columns_desc, format=json_format)
        coder = ChatAgent('coder', coder_sys_msg, json_format=True, keep_history=True)

        coder_base_format = '''{"explanation": "the explanation of the code", "code":  "python code here"}'''
        coder_base_sys_msg = sys_data['coderBase'].format(columns=columns_desc, format=coder_base_format)
        coder_base = ChatAgent('coder_base', coder_base_sys_msg, json_format=True, keep_history=True)

        coder_agg_format = '''{"description": "short description of the code",  "function":  "def get_results(df):  python code here"}'''
        coder_agg_sys_msg = sys_data['coderAgg'].format(columns=columns_desc, format=coder_agg_format)
        coder_agg = ChatAgent('coder_agg', coder_agg_sys_msg, json_format=True, keep_history=True)

        checker_format = ''' {"explanation": "the explanation of the function validness", "result":  "True if valid /False if not valid"}'''
        coder_sys_msg = sys_data['checker'].format(columns=self.columns, format=checker_format)
        checker = ChatAgent('checker', coder_sys_msg, json_format=True, keep_history=True)

        # small token size LLM which just fixed current function
        corrector_format = '''{"explanation": "the explanation of the function error and how to fix it", "function":  the fixed function }'''
        corrector_sys_msg = sys_data['corrector'].format(columns=self.columns, format=corrector_format)
        self.corrector = ChatAgent('corrector', corrector_sys_msg, json_format=True, keep_history=True)
        self.chatroom = Chat([coder, planner, checker, coder_base, coder_agg], ds_name)

    async def flow(self, msg):

        '''
        This function hold the flow of the chat. If normal function is generated, then it is executed.
        If error occurs, then the Error is passed back to the chatroom and new iteration is conducted.
        Now it only works for single pass coding plans.

        :param msg:
        :return:
        '''

        coder_err = None

        chatroom_resp = await self.chatroom.chat_sft(msg, coder_err)
        print("######## chatroom response: ", chatroom_resp)



async def handle_execution(flow, prompt):

    # Call the async flow method
    bot_response = await flow.flow(prompt)
    # Store the flow object in session state
    return bot_response, flow


def run_test():



    def get_predefined_ds():

        with open('datasets/dataanalytics/val.yaml', 'r') as file:
            ds_meta = yaml.load(file, Loader=yaml.FullLoader)

        datasets = {}
        for ds, v in ds_meta.items():
            path = 'datasets/dataanalytics/' + v['path']
            datasets[ds] = path

        return datasets

    def load_predefined_ds(predefined_datasets, selected_option):
        path = predefined_datasets[selected_option]
        df = pd.read_csv(path)
        return df

    def get_tasks(ds):

        with open('datasets/dataanalytics/val.yaml', 'r') as file:
            ds_meta = yaml.load(file, Loader=yaml.FullLoader)

        questions = ds_meta[ds]['questions']

        output = []
        for k, v in questions.items():
            output.append(v)

        return output

    import os
    predefined_datasets = get_predefined_ds()
    for selected_dataset in predefined_datasets:
        df = load_predefined_ds(predefined_datasets, selected_dataset)
        predefined_tasks = get_tasks(selected_dataset)


        if os.path.exists("./datasets/dataanalytics/code_strings.json"):
            with open("./datasets/dataanalytics/code_strings.json") as f:
                cs = json.load(f)
                if selected_dataset in cs:
                    continue

        print("Worknig on: ", selected_dataset)
        for task in predefined_tasks[:2]:
            init_desc = f"{', '.join(df.columns)}."
            # prompt = "make a customer behavior analysis"
            # prompt = "name 10 most popular items sold by the store"
            flow = Flow(df, init_desc, selected_dataset)
            asyncio.run(handle_execution(flow, task))


if __name__=="__main__":

    # import pandas as pd
    # data = pd.read_csv('./datasets/dataanalytics/market_basket_dataset.csv')
    # # explorer = Explorer(data)
    # init_desc = ""#explorer.init_desc()
    #
    # init_desc = f"{', '.join(data.columns)}."
    # prompt = "make a customer behavior analysis"
    # # prompt = "name 10 most popular items sold by the store"
    # flow = Flow(data, init_desc)
    # # flow.flow()
    #
    # asyncio.run(handle_execution(flow, prompt))
    run_test()