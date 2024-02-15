import json
import re
import asyncio

class Chat:

    def __init__(self, agents, ds_name):
        '''
        we need task_prompt to initilize the coder and planner agents
        :param task_prompt:
        coder: the llm initilised with coder system message
        planner: the llm initialised with planner system message
        '''

        self.ds_name = ds_name
        for agent in agents:
            setattr(self, agent.role, agent)


    @staticmethod
    def extract_python_functions(str_func):
        # Regular expression to match Python-like function definitions
        pattern = re.compile(r'\bdef\b\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*:(.*?)(?=\bdef\b|\Z)', re.DOTALL)

        # Find all matches in the input text
        matches = re.finditer(pattern, str_func)

        # Extract and return the function definitions as a list of strings
        function_definitions = [match.group(0) for match in matches]

        output_funcs = []
        for func in function_definitions:


            post_func = [func.split('\n')[0]]
            for line in func.split('\n')[1:]:
                if line[:4] == '    ' and line[5] != '#':
                    post_func.append(line)

            final_func = '\n'.join(post_func)

            final_func = final_func.strip().strip('}').strip('{')
            # Replace escaped characters with their actual values
            final_func = final_func.replace('\\n', '\n').replace('\t', '    ')
            output_funcs.append(final_func)

        return output_funcs

    async def chat(self, task, coder_err=None):
        '''
        how chatting of single message happens?
        the message is passed to a planner. he provides a detailed plan which is a number list.
        the second llm accept the plan and generates the code. let's do it simple then
        :param msg:
        :return:
        '''


        planner_response = self.planner.step(task)
        print('########## planner_response: ', planner_response)

        # now we need to add the AsyncIO operation here
        plan_list = json.loads(planner_response)['plan']

        # working code
        # code_outputs = {}
        # coroutines = []
        # for en, pi in enumerate(plan_list):
        #     coroutines.append(self.coder_base.astep(pi, en, code_outputs))
        # await asyncio.gather(*coroutines)

        import random
        async def run_coroutine_with_timeout(self, en, pi, code_outputs):
            try:
                await asyncio.wait_for(self.coder_base.astep(pi, en, code_outputs), timeout=100)
            except asyncio.TimeoutError:
                print(f"Coroutine {en} exceeded timeout, rerunning...")
                await self.coder_base.astep(pi, en, code_outputs)

        code_outputs = {}
        tasks = [run_coroutine_with_timeout(self, en, pi, code_outputs) for en, pi in enumerate(plan_list)]
        await asyncio.gather(*tasks)

        # sort by the task index
        code_outputs = dict(sorted(code_outputs.items()))
        code_strings = [json.loads(x)['code'] for x in list(code_outputs.values())]

        # implement new logic of code aggregator.
        # for example, iterate the list of code and append each new line to the previous using LLM.
        code_agg_outputs = []
        code0 = code_strings[0]
        for code1 in code_strings[1:]:
            agg_inp = '\n'.join([code0, code1])
            coder_agg_response = self.coder_agg.step(agg_inp)
            code_agg_outputs.append((agg_inp, coder_agg_response))
            json_res = json.loads(coder_agg_response)
            coder_function = json_res['function']
            code0 = coder_function


        # coder_response = self.coder.step(planner_response)
        # coder_agg_response = await self.coder_agg.step(code_strings)
        # print('########## coder_response ', coder_agg_response)
        # json_res = json.loads(coder_agg_response)
        # coder_function = json_res['function']
        return coder_function

    async def chat_sft(self, task, coder_err=None):
        '''
        how chatting of single message happens?
        the message is passed to a planner. he provides a detailed plan which is a number list.
        the second llm accept the plan and generates the code. let's do it simple then
        :param msg:
        :return:
        '''

        import time
        start = time.time()
        planner_response = self.planner.step(task)
        print('########## planner_response: ', planner_response)

        # if coder_err:
        #     planner_response += 'Keep in mind that the following error occurred in the previous run: ' + coder_err

        # now we need to add the AsyncIO operation here
        plan_list = json.loads(planner_response)['plan']

        # working code
        # code_outputs = {}
        # coroutines = []
        # for en, pi in enumerate(plan_list):
        #     coroutines.append(self.coder_base.astep(pi, en, code_outputs))
        # await asyncio.gather(*coroutines)

        import random
        async def run_coroutine_with_timeout(self, en, pi, code_outputs):
            try:
                await asyncio.wait_for(self.coder_base.astep(pi, en, code_outputs), timeout=100)
            except asyncio.TimeoutError:
                print(f"Coroutine {en} exceeded timeout, rerunning...")
                await self.coder_base.astep(pi, en, code_outputs)

        code_outputs = {}
        tasks = [run_coroutine_with_timeout(self, en, pi, code_outputs) for en, pi in enumerate(plan_list)]
        await asyncio.gather(*tasks)

        # sort by the task index
        code_outputs = dict(sorted(code_outputs.items()))
        # print(code_outputs)
        code_strings = [json.loads(x)['code'] for x in list(code_outputs.values())]

        end = time.time() - start

        import os
        if not os.path.exists("./datasets/dataanalytics/code_strings.json"):
            data = {}
        else:
            with open("./datasets/dataanalytics/code_strings.json") as f:
                data = json.load(f)

        if self.ds_name not in data:
            data[self.ds_name] = {task: {'code_strings': code_strings, 'time': end}}
        else:
            data[self.ds_name][task] = {'code_strings': code_strings, 'time': end}

        with open("./datasets/dataanalytics/code_strings.json", "w") as f:
            json.dump(data, f)

        # code_strings = '\n'.join(code_strings)
        print("##### CODER BASE COROUTINES ARE DONE")
        return "def get_results(df):\n  pass"

        # implement new logic of code aggregator.
        # for example, iterate the list of code and append each new line to the previous using LLM.
        code_agg_outputs = []
        code0 = code_strings[0]
        for code1 in code_strings[1:]:
            agg_inp = '\n'.join([code0, code1])
            coder_agg_response = self.coder_agg.step(agg_inp)
            code_agg_outputs.append((agg_inp, coder_agg_response))
            json_res = json.loads(coder_agg_response)
            coder_function = json_res['function']
            code0 = coder_function


        # coder_response = self.coder.step(planner_response)
        # coder_agg_response = await self.coder_agg.step(code_strings)
        # print('########## coder_response ', coder_agg_response)
        # json_res = json.loads(coder_agg_response)
        # coder_function = json_res['function']
        return coder_function
        # run checker
        # checker_response = self.checker.step(coder_function)
        # checker_result = json.loads(checker_response)
        # return {'valid': checker_result['result'], 'func': coder_function, 'explanation': checker_result['explanation']}



