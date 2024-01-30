import json
import re
import asyncio

class Chat:

    def __init__(self, agents):
        '''
        we need task_prompt to initilize the coder and planner agents
        :param task_prompt:
        coder: the llm initilised with coder system message
        planner: the llm initialised with planner system message
        '''

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

        planner_response = await self.planner.step(task)
        print('########## planner_response: ', planner_response)

        # if coder_err:
        #     planner_response += 'Keep in mind that the following error occurred in the previous run: ' + coder_err

        # now we need to add the AsyncIO operation here
        plan_list = json.loads(planner_response)['plan']
        # code_outputs = []
        # for pi in plan_list:
        #     coder_response = await self.coder_base.step_single(pi)
        #     code_outputs.append(coder_response)

        code_outputs = []
        coroutines = [self.coder_base.step_single(pi, en) for en, pi in enumerate(plan_list)]
        coder_responses = await asyncio.gather(*coroutines)
        code_outputs.extend(coder_responses)

        # coder_response = self.coder.step(planner_response)
        coder_agg_response = await self.coder_agg.step(planner_response)
        print('########## coder_response ', coder_agg_response)
        json_res = json.loads(coder_agg_response)
        coder_function = json_res['function']
        return coder_function
        # run checker
        # checker_response = self.checker.step(coder_function)
        # checker_result = json.loads(checker_response)
        # return {'valid': checker_result['result'], 'func': coder_function, 'explanation': checker_result['explanation']}

