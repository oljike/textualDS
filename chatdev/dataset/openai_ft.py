from openai import OpenAI
client = OpenAI()

client.fine_tuning.jobs.create(
  training_file="../../datasets/dataanalytics/sft_openai.jsonl",
  model="gpt-3.5-turbo",
    hyperparameters={
        "n_epochs": 2
    }
)


