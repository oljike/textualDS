import json
import yaml
import jsonlines
# combine sys msg, code string, and code outputs into sft data

with open("../../datasets/dataanalytics/code_strings.json") as f:
    code_strings = json.load(f)


with open("../../datasets/dataanalytics/sft_data.yaml") as f:
    sft_data = yaml.safe_load(f)


dt = {}
sft_openai_train = []
sft_openai_val = []
en = 0
for dsname, v in code_strings.items():


    for taskname, vv in v.items():
        current_inp = {"messages": [{"role": "system", "content": "You are tasked with combining multiple Python code snippets into a cohesive single flow. Your goal is to merge the provided code snippets without duplicating any code while ensuring that each snippet is included and executed in the appropriate sequence. All code must be unified under single function called def get_results(df). All numerical must be converted to separate dataframes, do not convert them to json. Image must be returned together with the results. The dataframe df is already provided. The code is the following:"}]}
        current_inp["messages"].append({"role": "user", "content": str(vv["code_strings"])})
        current_inp["messages"].append({"role": "assistant", "content": str(sft_data[dsname][taskname]["agg"])})
        # print(vv["code_strings"])
        # print(sft_data[dsname][taskname]["agg"])

        if en<18:
            sft_openai_train.append(current_inp)
        else:
            sft_openai_val.append(current_inp)
        en += 1



with open("../../datasets/dataanalytics/sft_openai_train.jsonl", 'w') as jsonl_file:
    for item in sft_openai_train:
        json_line = json.dumps(item) + '\n'
        jsonl_file.write(json_line)


with open("../../datasets/dataanalytics/sft_openai_val.jsonl", 'w') as jsonl_file:
    for item in sft_openai_val:
        json_line = json.dumps(item) + '\n'
        jsonl_file.write(json_line)


