# in this script I use LLM to extract information from notebook to generate short and precise description of the task
import os
os.environ["OPENAI_API_KEY"] = "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"
from openai import OpenAI
import json


if __name__=="__main__":
    client = OpenAI()

    data = json.load(open('../../data/kaggle_meta/all_task_raw.json'))

    system_message = "You are a cautious assistant. You carefully follow instructions. You a are a specialist in technical tasks."
    user_message = '''Given the following text which contains some data science task/dataset, extract the task  
        and formulate it more technically.  Make it short and precise, but in few sentences. If possible, include the 
        metrics which are required/allowed.  Return json format {task: the output task}. Do not include any summaries 
        or conclusion. If task is unclear return {task: None}. The text is: '''

    all_sys_msgs = {}
    for nb in data:
        # print(nb)
        # if 'tabular-xgboost' not in nb:
        #     continue

        meta = '\n'.join(data[nb][:5])

        prompt_input = system_message + '\n' + user_message + '\n' + meta

        response_format = {"type": "json_object"}
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format=response_format,
            messages=[{"role": "user", "content": prompt_input}],
            seed=42)

        print(response.choices[0].message.content)
        all_sys_msgs[nb] = json.loads(response.choices[0].message.content)['task']


    with open('../../data/kaggle_meta/all_task_procs.json', 'w') as f:
        json.dump(all_sys_msgs, f)