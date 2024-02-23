from openai import OpenAI
import json


with open('../api.json') as f:
  data = json.load(f)
  api_key = data['openai_api']
client = OpenAI(api_key=api_key)




data_path = "../../datasets/dataanalytics/sft_openai_val.jsonl"

# Load the dataset
with open(data_path, 'r', encoding='utf-8') as f:
    dataset = [json.loads(line) for line in f]

sys_msg = dataset[0]['messages'][0]['content']
user = dataset[0]['messages'][1]['content']


model_id = "ft:gpt-3.5-turbo-1106:personal::8sywKRNQ"
completion_ft = client.chat.completions.create(
  model=model_id,
  messages=[
    {"role": "system", "content": sys_msg},
    {"role": "user", "content": user}
  ]
)
print(completion_ft.choices[0].message.content)



completion_dft = client.chat.completions.create(
  model="gpt-4-0125-preview",
  messages=[
    {"role": "system", "content": sys_msg},
    {"role": "user", "content": user}
  ]
)
print(completion_dft.choices[0].message.content)
