# in this script I use LLM to extract information from notebook to generate short and precise description of the task
import os
os.environ["OPENAI_API_KEY"] = "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"
from openai import OpenAI
import json


if __name__=="__main__":
    client = OpenAI()

    task_data = json.load(open('../../data/kaggle_meta/all_task_procs.json'))
    mds_data = json.load(open('../../data/kaggle_meta/all_task_raw.json'))

    system_message = "You are a cautious assistant. You carefully follow instructions. You a are a specialist in technical tasks."
    user_message = '''Given the following task description and text which describes how the task is executed, generate 
        a detailed plan which solves the task. The plan has to be detailed and numbered list. Do not include non-technical 
        details, which cannot be solved using coding.
         Return json format {plan: the output plan}.  '''

    inputs = 'The task is: {task}. The execution description is {desc}.'


    if os.path.exists('../../data/kaggle_meta/all_task_plans.json'):
        all_plan_msgs = json.load(open('../../data/kaggle_meta/all_task_plans.json'))
    else:
        all_plan_msgs = {}

    try:
        for nb in task_data:
            print(nb)
            if nb in all_plan_msgs:
                print('passing...')
                continue

            task_ = task_data[nb]
            meta_ = mds_data[nb]

            prompt_input = system_message + '\n' + user_message + inputs.format(task=task_, desc=meta_) + '\n'

            response_format = {"type": "json_object"}
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                response_format=response_format,
                messages=[{"role": "user", "content": prompt_input}],
                seed=42)

            print(response.choices[0].message.content)
            all_plan_msgs[nb] = json.loads(response.choices[0].message.content)['plan']

    except Exception as e:
        print('some error occured', e)

    with open('../../data/kaggle_meta/all_task_plans.json', 'w') as f:
        json.dump(all_plan_msgs, f)
