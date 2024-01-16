import torch
import transformers

import transformers
model = transformers.AutoModelForCausalLM.from_pretrained(
  'mosaicml/mpt-7b',
  trust_remote_code=True
)


from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")


system_message = "You are a cautious assistant. You carefully follow instructions. You a are a specialist in technical tasks."
user_message = '''Given the following text which describes some data science task/dataset, extract the task formulation 
or introduction and formulate it more technically. Make it short and precise.   Do not include any summaries or task execution plans. The text is:
Making every bit count - Where to invest to combat air pollution in India?
Identifying the cities that require immediate attention to their increasing air pollution
Snap...pop...crackle...snap...flare... - The fire kept modifying its tone as I fed more twigs and leaves into its mouth with the long handle outdoor broom I was holding. I was 10 years old. Along with my grandfather, I was burning all the dry leaves and twigs that were lying on our backyard. It was fun to do it! But, looking back I realise that I was unknowingly contributing to the air pollution problem in India.    
    Did my grandfather and I want to pollute the environment? Nope.
    But were we? Yes.
    Air pollution is an evil, but not necessarily a ploy of bad people. When countries and local industries are fighting for survival, they somehow tend to forget their obligations to the environment. It's not entirely their fault. Hence, I believe the strongest focus to deal with air pollution or any kind of pollution is to not place a ton of sanctions but to provide an alternative way for people to live the lives they dream of.
In this notebook, I make an attempt to understand how investments can be made in order to minimize the effect of air pollution in a city. 
NOTE:
The work here is my interpretation of the data at hand. The recommendations I will suggest are based on what I find is true through my analysis. They need not necessarily resonate in the same tone with every reader.
    
![](https://www.halifax.ca/sites/default/files/pages/in-content/2018-06/Brush-Burning-HRM.jpg)
But, what if those twigs were being burnt because we needed warmth? Are we still wrong?
Introduction
This notebook is a submission to the [Where to deploy resources in India to combat air pollution](https://www.kaggle.com/rohanrao/air-quality-data-in-india/tasks?taskId=1877) hosted by [@romandovega](https://www.kaggle.com/romandovega) on the [Air Quality Data in India](https://www.kaggle.com/rohanrao/air-quality-data-in-india) dataset compiled by [@rohanrao](https://www.kaggle.com/rohanrao).  
In a crux, the task requires a submission that would convince a rich uncle to provide monetary investment to improve the quality of air in a given city. The necessity is to tie up all loose ends with data-based evidence and also present a rough plan as to how things must be done and also how progress can be measured. A maximum of 3 cities can be chosen from the prospective list of 25+ cities present in the dataset at the time of this analysis.
Summary
In summary, the three main cities that have been chosen are Ahmedabad, Lucknow and Patna. Ahmedabad is to be given the initial investment for the next 3 years. If this is succesful, investment should go to Lucknow and Patna before any other city in this dataset.  
Gurugram needs to be kept under observation for its rapid decline in air quality. However, instead of directly funding to improve air in Gurugram, it would be better to inform the tech giants in Gurugram(almost 50% of Fortune 500 companies have offices here) about the problem. They could tackle the issue as a part of their CSR activities to improve the living standards of their employees.  
The following slide deck gives a brief view of why the 3 above cities need to be funded. The deck is typically all you need to read, *Potential Investor*.
For a nuts and bolts understanding of how the analysis was conducted, **please read on.**'''

prompt = f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant"

from transformers import pipeline

pipe = pipeline('text-generation', model=model, tokenizer=tokenizer, device='cuda:0')

with torch.autocast('cuda', dtype=torch.float16):
    print(
        pipe(prompt + '\n',
            max_new_tokens=200,
            do_sample=True,
            use_cache=True))


