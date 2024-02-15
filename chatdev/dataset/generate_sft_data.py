import json
import yaml
import jsonlines
# combine sys msg, code string, and code outputs into sft data

with open("../../datasets/dataanalytics/code_strings.json") as f:
    code_strings = json.load(f)


with open("../../datasets/dataanalytics/sft_data.yaml") as f:
    sft_data = yaml.safe_load(f)


dt = {}
sft_openai = []
for dsname, v in code_strings.items():


    for taskname, vv in v.items():
        current_inp = {"messages": [{"role": "system", "content": "You are tasked with combining multiple Python code snippets into a cohesive single flow. Your goal is to merge the provided code snippets without duplicating any code while ensuring that each snippet is included and executed in the appropriate sequence. All code must be unified under single function called def get_results(df). All numerical must be converted to separate dataframes, do not convert them to json. Image must be returned together with the results. The dataframe df is already provided. The code is the following:"}]}
        current_inp["messages"].append({"role": "user", "content": str(vv["code_strings"])})
        current_inp["messages"].append({"role": "assistant", "content": str(sft_data[dsname][taskname]["agg"])})
        # print(vv["code_strings"])
        # print(sft_data[dsname][taskname]["agg"])
        sft_openai.append(current_inp)


print(sft_openai)
with open("../../datasets/dataanalytics/sft_openai.jsonl", 'w') as jsonl_file:
    for item in sft_openai:
        json_line = json.dumps(item) + '\n'
        jsonl_file.write(json_line)


