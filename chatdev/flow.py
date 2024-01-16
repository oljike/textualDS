from chat import Chat
from agent import ChatAgent
from explorer import Explorer
import json
import types
import pandas as pd
import pickle
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

class Flow:

    def __init__(self, data, desc=None):

        if 'pkl' in data:
            with open(data, 'rb') as file:
                inp = pickle.load(file)
            self.df = inp[0]
        else:
            self.df = pd.read_csv(data)

        self.columns = self.df.columns

        sys_data = json.load(open('sys_msg.json'))

        planner_sys_msg = sys_data['planner'].format(desc='', columns=desc)
        planner = ChatAgent(planner_sys_msg)

        json_format = '''{"explanation": "the explanation of the code", 
                          "function":  "def get_results(df):  python code here"}'''
        coder_sys_msg = sys_data['coder'].format(desc='', task='', columns=desc, format=json_format)
        coder = ChatAgent(coder_sys_msg, json_format=True)

        checker_format = ''' {"explanation": "the explanation of the function validness",
                          "result":  "True if valid /False if not valid"}'''
        coder_sys_msg = sys_data['checker'].format(columns=self.columns, format=checker_format)
        checker = ChatAgent(coder_sys_msg, json_format=True, keep_history=False)

        ### small token size LLM which just fixed current function
        corrector_format = '''{"explanation": "the explanation of the function error and how to fix it",
                                  "function":  the fixed function }'''
        corrector_sys_msg = sys_data['corrector'].format(format=corrector_format)
        self.corrector = ChatAgent(corrector_sys_msg, json_format=True, keep_history=False)

        self.chatroom = Chat(coder, planner, checker)

    @staticmethod
    def create_function(func_str, func_name='get_results', import_libraries=['numpy as np', 'pandas as pd',
                                                                             'matplotlib.pyplot as plt', 'matplotlib']):
        # Create a namespace for the function
        namespace = {}

        # Combine import statements, function string, and a call to locals()
        imports = "\n".join(f"import {library}" for library in import_libraries) if import_libraries else ""
        tkagg = "matplotlib.use('TkAgg')"
        full_code = f"{imports}\n{tkagg}\n{func_str}"

        # Use exec to execute the combined code within the namespace
        exec(full_code, namespace)

        # Retrieve the created function from the namespace
        created_func = namespace.get(func_name)

        if not isinstance(created_func, types.FunctionType):
            raise ValueError(f"Function '{func_name}' not found in the specified code.")

        return created_func


    def flow(self, msg):

        '''
        This function hold the flow of the chat. If normal function is generated, then it is executed.
        If error occurs, then the Error is passed back to the chatroom and new iteration is conducted.
        Now it only works for single pass coding plans.

        :param msg:
        :return:
        '''

        coder_err = None
        success = False
        terminated = False
        while True:

            response = self.chatroom.chat(msg, coder_err)
            print(response)
            if 'bad response' in response:
                coder_err = response
                continue

            print(response)
            dynamic_function = self.create_function(response)

            # run new loop, which only fixes some syntaxis errors.
            # the while true loop has to be substituted by some stopping criteria.
            while True:
                try:
                    result = dynamic_function(self.df)
                    success = True
                    break
                except Exception as e:
                    print(str(e))
                    coder_err = str(e)
                    corrector_inp = {'function': response,
                                      'error': coder_err}

                    corrected_output = self.corrector.step(str(corrector_inp))
                    corrected_func = json.loads(corrected_output)['function']
                    print(corrected_func)
                    dynamic_function = self.create_function(corrected_func)

            if success:
                break

        # add explanation of the reply

        print(result)

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


if __name__=="__main__":

    # data = '../tests/dfs/ecom/ecommerce_customer_data.csv'
    # explorer = Explorer(data)
    # init_desc = explorer.init_desc()

    data = '../DS-1000-main/ds1000_data/Pandas/Insertion/q0/input/input1.pkl'
    flow = Flow(data, None)
    flow.flow('''
             'The DataFrame is read from a CSV file. All rows which have Type 1 are on top, followed by the rows with Type 2, followed by the rows with Type 3, etc.\n',
             "I would like to shuffle the order of the DataFrame's rows according to a list. \\\n",
             'For example, give a list [2, 4, 0, 3, 1, 5] and desired result should be:\n',
             '    Col1  Col2  Col3  Type\n',
             '2      7     8     9     2\n',
             '4     13    14    15     3\n',
             '0     1     2     3     1\n',
             '3    10    11    12     2\n',
             '1     4     5     6     1\n',
             '5    16    17    18     3\n',
             '...\n',
            'How can I achieve this?''')