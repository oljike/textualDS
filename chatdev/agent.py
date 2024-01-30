from typing import Any, Dict, List, Optional
from openai import OpenAI, AsyncOpenAI
import json

class ChatAgent():

    def __init__(self, role, system_message, json_format=False, keep_history=True):

        self.role = role
        self.system_message = system_message

        with open('chatdev/api.json') as f:
            data = json.load(f)
            self.api_key = data['openai_api']
        self.stored_messages: List = [{"role": "system", "content": self.system_message}]
        self.client = AsyncOpenAI(api_key=self.api_key)
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

        self.stored_messages.append({"role": "user", "content": message})
        return self.stored_messages

    async def step_single(self, input_message, task_en):
        r"""Performs a single step in the chat with accumulating prompt messages.
        """

        input_prompt = self.stored_messages + [{"role": "user", "content": input_message}]

        print('########## prompt for ' + self.role + ": " + json.dumps(input_prompt))
        print(self.stored_messages)

        response_format = {"type": "json_object"} if self.json_mode else {"type": "text"}
        response = await self.client.chat.completions.create(
                                                   model="gpt-4-1106-preview",
                                                   response_format=response_format,
                                                   messages=input_prompt,
                                                   seed=42)
        response = response.choices[0].message.content
        print('task {} completed'.format(task_en))
        return response

    async def step(self, input_message):

        r"""Performs a single step in the chat session by generating a response
        to the input message.

        Args:
            input_message (ChatMessage): The input message to the agent.
        """

        if self.keep_history:
            self.update_user_message(input_message)

        print('########## prompt for ' + self.role + ": " + json.dumps(self.stored_messages))

        response_format = {"type": "json_object"} if self.json_mode else {"type": "text"}
        response = await self.client.chat.completions.create(
                                                   model="gpt-4-1106-preview",
                                                   response_format=response_format,
                                                   messages=self.stored_messages,
                                                   seed=42)
        response = response.choices[0].message.content

        if self.keep_history:
            self.update_assistant_message(response)

        return response