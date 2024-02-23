from typing import Any, Dict, List, Optional
from openai import OpenAI, AsyncOpenAI
import json
import asyncio


OAI_PRICE1K = {
    "text-ada-001": 0.0004,
    "text-babbage-001": 0.0005,
    "text-curie-001": 0.002,
    "code-cushman-001": 0.024,
    "code-davinci-002": 0.1,
    "text-davinci-002": 0.02,
    "text-davinci-003": 0.02,
    "gpt-3.5-turbo-instruct": (0.0015, 0.002),
    "gpt-3.5-turbo-0301": (0.0015, 0.002),  # deprecate in Sep
    "gpt-3.5-turbo-0613": (0.0015, 0.002),
    "gpt-3.5-turbo-16k": (0.003, 0.004),
    "gpt-3.5-turbo-16k-0613": (0.003, 0.004),
    "gpt-35-turbo": (0.0015, 0.002),
    "gpt-35-turbo-16k": (0.003, 0.004),
    "gpt-35-turbo-instruct": (0.0015, 0.002),
    "gpt-4": (0.03, 0.06),
    "gpt-4-32k": (0.06, 0.12),
    "gpt-4-0314": (0.03, 0.06),  # deprecate in Sep
    "gpt-4-32k-0314": (0.06, 0.12),  # deprecate in Sep
    "gpt-4-0613": (0.03, 0.06),
    "gpt-4-32k-0613": (0.06, 0.12),
    # 11-06
    "gpt-3.5-turbo": (0.0015, 0.002),  # default is still 0613
    "gpt-3.5-turbo-1106": (0.001, 0.002),
    "gpt-35-turbo-1106": (0.001, 0.002),
    "gpt-4-1106-preview": (0.01, 0.03),
    "gpt-4-0125-preview": (0.01, 0.03),
    "gpt-4-turbo-preview": (0.01, 0.03),
    "gpt-4-1106-vision-preview": (0.01, 0.03),  # TODO: support vision pricing of images
}

class ChatAgent():

    def __init__(self, role, system_message, json_format=False, keep_history=True):

        self.role = role
        self.system_message = system_message

        with open('chatdev/api.json') as f:
            data = json.load(f)
            self.api_key = data['openai_api']
        self.stored_messages = [{"role": "system", "content": self.system_message}]

        _client = AsyncOpenAI(
            # provide a dummy API key so that requests made directly will always fail
            api_key='<this client should never be used directly!>',
        )

        self.aclient = _client.with_options(api_key=self.api_key)
        self.client = OpenAI(api_key=self.api_key)
        self.json_mode = json_format
        self.keep_history = keep_history

    def update_messages(self, message):
        r"""Updates the stored messages list with a new message.

        Args:
            message (ChatMessage): The new message to add to the stored
                messages.

        Returns:
            List[ChatMessage]: The updated stored messages.
        """
        self.stored_messages.append(message)
        return self.stored_messages

    def update_user_message(self, message):

        self.stored_messages.append({"role": "user", "content": message})
        return self.stored_messages

    def update_assistant_message(self, message):

        self.stored_messages.append({"role": "assistant", "content": message})
        return self.stored_messages

    def get_cost(self, response):
        """Calculate the cost of the response."""
        model = response.model
        if model not in OAI_PRICE1K:
            print(f"Model {model} is not found. The cost will be 0.")
            return 0

        n_input_tokens = response.usage.prompt_tokens
        n_output_tokens = response.usage.completion_tokens
        print("n_input_tokens: ", n_input_tokens)
        print("n_output_tokens: ", n_output_tokens)
        tmp_price1K = OAI_PRICE1K[model]
        # First value is input token rate, second value is output token rate
        return (tmp_price1K[0] * n_input_tokens + tmp_price1K[1] * n_output_tokens) / 1000


    async def astep_timeout(self, input_message, timeout=100):

        try:
            agent_output = await asyncio.wait_for(self.astep(input_message), timeout)
        except asyncio.TimeoutError:
            print("Timeout occurred. Rerunning the function...")
            agent_output = await self.astep_timeout(input_message, timeout)  # Rerun the function
        return agent_output

    async def astep_timeout_coder(self, input_message, task_en, output, timeout=100):

        try:
            await asyncio.wait_for(self.astep_coder(input_message, task_en, output), timeout)
        except asyncio.TimeoutError:
            print("Timeout occurred. Rerunning the function...")
            await self.astep_timeout_coder(input_message, task_en, output, timeout)  # Rerun the function

    async def astep(self, input_message):
        r"""Performs a single step in the chat with accumulating prompt messages.
        """

        input_prompt = self.stored_messages + [{"role": "user", "content": input_message}]

        print('########## prompt for ' + self.role + ": ")
        print(input_prompt)
        # print(self.stored_messages)
        response_format = {"type": "json_object"} if self.json_mode else {"type": "text"}

        response = await self.aclient.chat.completions.create(
                                                       model="gpt-4-0125-preview",
                                                       response_format=response_format,
                                                       messages=input_prompt)
        self.get_cost(response)
        response = response.choices[0].message.content
        print('###### task {} completed'.format(input_message))
        print(response)

        return response

    async def astep_coder(self, input_message, task_en, output):
        r"""Performs a single step in the chat with accumulating prompt messages.
        """

        input_prompt = self.stored_messages + [{"role": "user", "content": input_message}]

        print('########## prompt for ' + self.role + str(task_en) + ": ")
        print(input_prompt)
        # print(self.stored_messages)
        response_format = {"type": "json_object"} if self.json_mode else {"type": "text"}

        response = await self.aclient.chat.completions.create(
                                                       model="gpt-4-0125-preview",
                                                       response_format=response_format,
                                                       messages=input_prompt)
        self.get_cost(response)
        response = response.choices[0].message.content
        print('###### task {} completed'.format(task_en))
        print(response)

        output[task_en] = response

    def step(self, input_message):

        r"""Performs a single step in the chat session by generating a response
        to the input message.

        Args:
            input_message (ChatMessage): The input message to the agent.
        """

        self.update_user_message(input_message)

        print('########## prompt for ' + self.role + ": ")
        print(self.stored_messages)


        # if self.role == 'coder_agg':
        #     model = "ft:gpt-3.5-turbo-0613:personal::8t8YROdV"
        #     response_format = {"type": "text"}
        # else:

        model = "gpt-4-0125-preview"
        response_format = {"type": "json_object"} if self.json_mode else {"type": "text"}
        response = self.client.chat.completions.create(
                                                   model=model,
                                                   response_format=response_format,
                                                   messages=self.stored_messages)
        cost = self.get_cost(response)
        response = response.choices[0].message.content

        self.update_assistant_message(response)
        # self.client.close()

        return response