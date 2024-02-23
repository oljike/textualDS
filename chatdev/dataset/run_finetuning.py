from openai import OpenAI
import json
with open('../api.json') as f:
  data = json.load(f)
  api_key = data['openai_api']
client = OpenAI(api_key=api_key)

client.fine_tuning.jobs.create(
    training_file="file-bJkhfbEQE18d5gwcd3ibD0aF",
    validation_file="file-ystN9GRFlA4WExVCs7T5Mi4H",
    model="gpt-3.5-turbo-0125",
    hyperparameters={
        "n_epochs": 2

    }
)


