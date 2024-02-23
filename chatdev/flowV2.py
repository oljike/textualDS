import sys
from os.path import abspath, join, dirname
app_path = abspath(join(dirname(__file__), '..'))
sys.path.append(app_path)

from chatdev.chatV2 import Chat
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
        planner_sys_msg = sys_data['planner'].format(desc='', columns=columns_desc, format=planner_format).replace('\n', '')
        planner = ChatAgent('planner', planner_sys_msg, json_format=True, keep_history=True)

        json_format = '''{"explanation": "the explanation of the code", "function":  "def get_results(df):  python code here"}'''
        coder_sys_msg = sys_data['coder'].format(columns=columns_desc, format=json_format).replace('\n', '')
        coder = ChatAgent('coder', coder_sys_msg, json_format=True, keep_history=True)

        coder_base_format = '''{"explanation": "the explanation of the code", "code":  "python code here"}'''
        coder_base_sys_msg = sys_data['coderBase'].format(columns=columns_desc, format=coder_base_format).replace('\n', '')
        coder_base = ChatAgent('coder_base', coder_base_sys_msg, json_format=True, keep_history=True)

        coder_agg_format = '''{"description": "short description of the code",  "function":  "def get_results(df):  python code here"}'''
        coder_agg_sys_msg = sys_data['coderAgg'].format(columns=columns_desc, format=coder_agg_format).replace('\n', '')
        coder_agg = ChatAgent('coder_agg', coder_agg_sys_msg, json_format=True, keep_history=True)

        checker_format = ''' {"explanation": "the explanation of the function validness", "result":  "True if valid /False if not valid"}'''
        coder_sys_msg = sys_data['checker'].format(columns=self.columns, format=checker_format).replace('\n', '')
        checker = ChatAgent('checker', coder_sys_msg, json_format=True, keep_history=True)

        # small token size LLM which just fixed current function
        corrector_format = '''{"explanation": "the explanation of the function error and how to fix it", "function":  the fixed function }'''
        corrector_sys_msg = sys_data['corrector'].format(columns=self.columns, format=corrector_format).replace('\n', '')
        corrector = ChatAgent('corrector', corrector_sys_msg, json_format=True, keep_history=True)

        # small token size LLM which just fixed current function
        classifier_format = '''{"explanation": "the explanation of the answer", "answer": "easy/medium/hard", "new_tasks": "[a list of strings with new tasks]"}'''
        classifier_sys_msg = sys_data['taskClassifier'].format(format=classifier_format, columns=f"{', '.join(self.df.columns)}").replace('\n', '')
        classifier = ChatAgent('classifier', classifier_sys_msg, json_format=True, keep_history=True)

        # small token size LLM which just fixed current function
        analyzer_sys_msg = sys_data['analyzer'].format(format=classifier_format, columns=f"{', '.join(self.df.columns)}").replace('\n', '')
        analyzer = ChatAgent('analyzer', analyzer_sys_msg, json_format=False, keep_history=True)

        self.chatroom = Chat([coder, planner, checker, coder_base, coder_agg, corrector, classifier, analyzer], ds_name)

    @staticmethod
    def create_function(func_str, func_name='get_results', import_libraries=['numpy as np', 'json', 'pandas as pd',
                                                                             'matplotlib.pyplot as plt', 'matplotlib']):
        # Create a namespace for the function
        namespace = {}

        # Combine import statements, function string, and a call to locals()
        imports = "\n".join(f"import {library}" for library in import_libraries) if import_libraries else ""
        tkagg = "matplotlib.use('agg')"
        # inline = "%matplotlib inline"
        full_code = f"{imports}\n{tkagg}\n{func_str}"

        # Use exec to execute the combined code within the namespace
        exec(full_code, namespace)

        # Retrieve the created function from the namespace
        created_func = namespace.get(func_name)

        if not isinstance(created_func, types.FunctionType):
            raise ValueError(f"Function '{func_name}' not found in the specified code.")

        return created_func


    async def process_chat_output(self, task_item, function_resp, all_results, all_funcs):

        gen_en = 0
        while True:
            print("######## gen_en", gen_en)
            if gen_en > 5:
                result = 'Impossible to generate result. Please, reformulate the task or make it more specific.'
                all_results[task_item] = {"result": result, "analysis": "Unavailable"}
                break
            gen_en += 1

            try:
                dynamic_function = self.create_function(function_resp)
                result = dynamic_function(self.df)

                # summarize here. it basically includes the initial task, and the output of the functio
                analyzer_input = f"Task: {task_item}. Data columns: {', '.join(self.df.columns)}"
                result_analysis = await self.chatroom.analyzer.astep_timeout(analyzer_input, 40)

                all_results[task_item] = {"result": result, "analysis": result_analysis}
                all_funcs.append(function_resp)
                break
            except Exception as e:
                coder_err = str(e)
                print('########## error exception: ', coder_err)
                corrector_inp = {"function": function_resp, "error": coder_err}
                corrector_output = await self.chatroom.corrector.astep_timeout(str(corrector_inp))
                function_resp = json.loads(corrector_output)["function"]
                print('########## corrector_response: ', corrector_output)
                print("########## corrected_func: ", function_resp)


    async def flow(self, task):

        '''
        This function hold the flow of the chat. If normal function is generated, then it is executed.
        If error occurs, then the Error is passed back to the chatroom and new iteration is conducted.
        Now it only works for single pass coding plans.

        :param task:
        :return:
        '''

        # classifier first
        classifier_output = await self.chatroom.classifier.astep_timeout(task, 25)
        classifier_output = json.loads(classifier_output)
        if len(classifier_output['new_tasks']) > 2:
            task_list = classifier_output['new_tasks']
        else:
            task_list = [task]

        # task coroutines
        task_coroutines = []
        chat_outputs = {}
        for en, task_item in enumerate(task_list):
            task_coroutines.append(self.chatroom.achat(task_item, chat_outputs))  # Assuming you pass en and pi to chat function
        await asyncio.gather(*task_coroutines)


        # run new loop, which only fixes some syntaxis errors.
        # the while true loop has to be substituted by some stopping criteria.
        all_results = {}
        all_funcs = []
        function_coroutines = []
        for task_item, function_resp in chat_outputs.items():
            function_coroutines.append(
                self.process_chat_output(task_item, function_resp, all_results, all_funcs))

        # Run the tasks concurrently
        await asyncio.gather(*function_coroutines)

        return all_results, all_funcs


async def handle_execution(flow, prompt):

    # Call the async flow method
    bot_response = await flow.flow(prompt)
    # Store the flow object in session state
    return bot_response, flow


if __name__=="__main__":

    import pandas as pd
    data = pd.read_csv('./datasets/dataanalytics/market_basket_dataset.csv')
    # data = pd.read_csv('./datasets/dataanalytics/supply_chain_data.csv')
    # data = pd.read_csv('./datasets/dataanalytics/rides.csv')
    # explorer = Explorer(data)
    init_desc = ""#explorer.init_desc()

    init_desc = f"{', '.join(data.columns)}."
    prompt = "make a customer behavior analysis"
    # prompt = "name 10 most popular items sold by the store"
    # prompt = "calculate and visualise supply ratio"
    flow = Flow(data, init_desc)
    # flow.flow()

    asyncio.run(handle_execution(flow, prompt))
