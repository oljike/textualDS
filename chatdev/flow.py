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

    async def flow(self, msg):

        '''
        This function hold the flow of the chat. If normal function is generated, then it is executed.
        If error occurs, then the Error is passed back to the chatroom and new iteration is conducted.
        Now it only works for single pass coding plans.

        :param msg:
        :return:
        '''

        coder_err = None
        function_resp = await self.chatroom.chat(msg, coder_err)
        print("######## chatroom response: ", function_resp)

        # run new loop, which only fixes some syntaxis errors.
        # the while true loop has to be substituted by some stopping criteria.
        gen_en = 0
        while True:
            print("######## gen_en", gen_en)
            if gen_en > 5:
                result = 'Impossible to generate result. Please, reformulate the task or make it more specific.'
                break
            gen_en += 1

            try:
                dynamic_function = self.create_function(function_resp)
                result = dynamic_function(self.df)
                break
            except Exception as e:
                coder_err = str(e)
                print('########## error exception: ', coder_err)
                corrector_inp = {"function": function_resp, "error": coder_err}
                corrector_output = self.corrector.step(str(corrector_inp))
                function_resp = json.loads(corrector_output)["function"]
                print('########## corrector_response: ', corrector_output)
                print("########## corrected_func: ", function_resp)

            # if success:
            #     break

        # add explanation of the reply

        print(result)
        return result, dynamic_function

    def check_results(self, result):
        '''
        This checks the output of the dynamic function. The output can be None (in case nothing is returned),
        dataframe, digit number,
        :param results:
        :return:
        '''

        if isinstance(result, pd.DataFrame):
            return True

    def flow_beta(self, prompt):
        '''
        1. the prompt is passed to the planner
        2. the plan is returned as a numbered list
        3. iterate through each item in the plan and pass it to the coder
        4. coder generate the function
        5. function is executed
            5.1 it return some output - either df, float, None, error
            5.2 if error has occurred, then function is generated again, with error appended to the coder prompt
        6. the output from the (5) is appended to the outputs_list
        7. after all items from the plan are executed, the task, plan, outputs_list (processed) is passed to the
           the manager whose goal is to summarise the results, i.e save them to files, combine multiple text conclusions
        8. finita.

        Notes:
        At the moment I have a chatroom which consists of some agents. Also, I have described the agents above which
        execute the tasks. Do we need to change the logic by which the chatting occur?
        Yes, the chat.step() functio is currently set to simple one pass logic.

        :param prompt: the task from the user
        :return:
        '''

        # generate plan
        planner_response = self.chatroom.planner.step(prompt)
        input_df = self.df
        code_outputs = {}
        # iterate each item in the plan
        for plan_item in planner_response:

            # generate function
            coder_response = self.chatroom.coder.step(plan_item)
            coder_function = json.loads(coder_response)['function']

            # run checker
            while True:
                checker_response = self.chatroom.checker.step(coder_function)
                checker_result = json.loads(checker_response)
                if checker_result['result']:
                    function_str = coder_function.strip('{').strip('}')
                    break
                else:
                    corrector_inp = {'function': coder_function,
                                     'error': checker_result['explanation']}

                    corrected_output = self.chatroom.corrector.step(str(corrector_inp))
                    coder_function = json.loads(corrected_output)['function']

            # now, run the second iteration loop which check the execution problems
            # the while true loop has to be substituted by some stopping criteria.
            while True:
                try:
                    dynamic_function = self.create_function(function_str)
                    result = dynamic_function(input_df)
                    if self.check_results(result):
                        input_df = result
                    break
                except Exception as e:
                    print(str(e))
                    coder_err = str(e)
                    corrector_inp = {'function': function_str,
                                     'error': coder_err}

                    corrected_output = self.chatroom.corrector.step(str(corrector_inp))
                    function_str = json.loads(corrected_output)['function']
                    # dynamic_function = self.create_function(corrected_func)

            code_outputs[plan_item] = result

        # now we need to run the manager how summarises the results
        final_output = self.chatroom.manager.step(code_outputs)


async def handle_execution(flow, prompt):

    # Call the async flow method
    bot_response = await flow.flow(prompt)
    # Store the flow object in session state
    return bot_response, flow


if __name__=="__main__":

    import pandas as pd
    # data = pd.read_csv('./datasets/dataanalytics/market_basket_dataset.csv')
    data = pd.read_csv('./datasets/dataanalytics/supply_chain_data.csv')
    # explorer = Explorer(data)
    init_desc = ""#explorer.init_desc()

    init_desc = f"{', '.join(data.columns)}."
    prompt = "plot relationship between the price of the products and the revenue generated by them"
    # prompt = "name 10 most popular items sold by the store"
    flow = Flow(data, init_desc)
    # flow.flow()

    asyncio.run(handle_execution(flow, prompt))
