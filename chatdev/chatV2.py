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


    # async def single_step_async(self, agent):


    async def chat(self, task):
        '''
        how chatting of single message happens?
        the message is passed to a planner. he provides a detailed plan which is a number list.
        the second llm accept the plan and generates the code. let's do it simple then
        :param msg:
        :return:
        '''

        task_classifier = self.task_classifier.step(task)


        planner_response = self.planner.step(task)
        print('########## planner_response: ', planner_response)

        # now we need to add the AsyncIO operation here
        plan_list = json.loads(planner_response)['plan']

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
        code_strings = '\n'.join(code_strings)

        # coder_response = self.coder.step(planner_response)
        coder_agg_response = self.coder_agg.step(code_strings)
        print('########## coder_response ', coder_agg_response)
        json_res = json.loads(coder_agg_response)
        coder_function = json_res['function']
        return coder_function

    async def achat(self, task, chat_outputs):
        '''
        how chatting of single message happens?
        the message is passed to a planner. he provides a detailed plan which is a number list.
        the second llm accept the plan and generates the code. let's do it simple then
        :param msg:
        :return:
        '''

        # planner_response = await self.planner.astep(task)
        planner_response = await self.planner.astep_timeout(task, 100)
        print('########## planner_response: ', planner_response)

        # now we need to add the AsyncIO operation here
        plan_list = json.loads(planner_response)['plan']

        code_outputs = {}
        tasks = []
        for en, pi in enumerate(plan_list):
            tasks.append(self.coder_base.astep_timeout_coder(pi, en, code_outputs, 100))
        await asyncio.gather(*tasks)


        # sort by the task index
        code_outputs = dict(sorted(code_outputs.items()))
        code_strings = [json.loads(x)['code'] for x in list(code_outputs.values())]
        code_strings = '\n'.join(code_strings)

        # coder_response = self.coder.step(planner_response)
        # coder_agg_response = await self.coder_agg.astep(code_strings)
        coder_agg_response = await self.coder_agg.astep_timeout(code_strings, 100)
        print('########## coder_response ', coder_agg_response)
        json_res = json.loads(coder_agg_response)
        coder_function = json_res['function']
        chat_outputs[task] = coder_function