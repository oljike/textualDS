from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from openai import OpenAI
import os
os.environ["OPENAI_API_KEY"] = "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"

class ChatAgent():

    def __init__(self, role, system_message, json_format=False, keep_history=True):

        self.role = role
        self.system_message = system_message
        self.api_key = "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"
        self.stored_messages: List = [self.system_message]
        self.client = OpenAI()
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

    def step(self, input_message):

        r"""Performs a single step in the chat session by generating a response
        to the input message.

        Args:
            input_message (ChatMessage): The input message to the agent.
        """

        if self.keep_history:
            messages = self.update_messages(input_message)
            prompt_input = '\n'.join(messages)
        else:
            prompt_input = '\n'.join([self.system_message, input_message])

        print('prompt for ' + self.role + ": " + prompt_input)

        response_format = {"type": "json_object"} if self.json_mode else {"type": "text"}
        response = self.client.chat.completions.create(
                                                   model="gpt-4-1106-preview",
                                                   response_format=response_format,
                                                   messages=[{"role": "user", "content": prompt_input}],
                                                   seed=42)

        return response.choices[0].message.content