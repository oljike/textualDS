import json
import re


class Chat:

    def __init__(self, coder, planner, checker):
        '''
        we need task_prompt to initilize the coder and planner agents
        :param task_prompt:
        coder: the llm initilised with coder system message
        planner: the llm initialised with planner system message
        '''

        self.coder = coder
        self.planner = planner
        self.checker = checker


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


    def chat(self, msg, coder_err=None):
        '''
        how chatting of single message happens?
        the message is passed to a planner. he provides a detailed plan which is a number list.
        the second llm accept the plan and generates the code. let's do it simple then
        :param msg:
        :return:
        '''

        planner_response = self.planner.step(msg)

        if coder_err:
            planner_response += 'Keep in mind that the following error occured in the previous run: ' + coder_err

        coder_response = self.coder.step(planner_response)
        coder_function = json.loads(coder_response)['function']

        ### run checker
        checker_response = self.checker.step(coder_function)
        checker_result = json.loads(checker_response)
        if checker_result['result']:
            return coder_function
        else:
            return 'bad response due to: ' + checker_result['explanation']
