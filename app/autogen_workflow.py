from __future__ import annotations

import os
import types
from functools import partial
from queue import Queue
from typing import Union, Dict

from autogen import ChatResult, GroupChat, Agent, OpenAIWrapper, ConversableAgent, UserProxyAgent, GroupChatManager
from autogen.code_utils import content_str
from autogen.io import IOStream
from termcolor import colored


def streamed_print_received_message(
        self,
        message: Union[Dict, str],
        sender: Agent,
        queue: Queue,
        index: int,
        *args,
        **kwargs,
):
    streaming_message = ""
    iostream = IOStream.get_default()
    # print the message received
    iostream.print(
        colored(sender.name, "yellow"), "(to", f"{self.name}):\n", flush=True
    )
    streaming_message += f"{sender.name} (to {self.name}):\n"
    message = self._message_to_dict(message)

    if message.get("tool_responses"):  # Handle tool multi-call responses
        if message.get("role") == "tool":
            queue.put(
                {
                    "index": index,
                    "delta": {"role": "assistant", "content": streaming_message},
                    "finish_reason": "stop",
                }
            )

        for tool_response in message["tool_responses"]:
            index += 1
            self._print_received_message(
                message=tool_response,
                sender=sender,
                queue=queue,
                index=index,
                *args,
                **kwargs,
            )

        if message.get("role") == "tool":
            return  # If role is tool, then content is just a concatenation of all tool_responses

    if message.get("role") in ["function", "tool"]:
        if message["role"] == "function":
            id_key = "name"
        else:
            id_key = "tool_call_id"
        id = message.get(id_key, "No id found")
        func_print = f"***** Response from calling {message['role']} ({id}) *****"
        iostream.print(colored(func_print, "green"), flush=True)
        streaming_message += f"{func_print}\n"
        iostream.print(message["content"], flush=True)
        streaming_message += f"{message['content']}\n"
        iostream.print(colored("*" * len(func_print), "green"), flush=True)
        streaming_message += f"{'*' * len(func_print)}\n"
    else:
        content = message.get("content")
        if content is not None:
            if "context" in message:
                content = OpenAIWrapper.instantiate(
                    content,
                    message["context"],
                    self.llm_config
                    and self.llm_config.get("allow_format_str_template", False),
                )
            iostream.print(content_str(content), flush=True)
            streaming_message += f"{content_str(content)}\n"
        if "function_call" in message and message["function_call"]:
            function_call = dict(message["function_call"])
            func_print = f"***** Suggested function call: {function_call.get('name', '(No function name found)')} *****"
            iostream.print(colored(func_print, "green"), flush=True)
            streaming_message += f"{func_print}\n"
            iostream.print(
                "Arguments: \n",
                function_call.get("arguments", "(No arguments found)"),
                flush=True,
                sep="",
            )
            streaming_message += f"Arguments: \n{function_call.get('arguments', '(No arguments found)')}\n"
            iostream.print(colored("*" * len(func_print), "green"), flush=True)
            streaming_message += f"{'*' * len(func_print)}\n"
        if "tool_calls" in message and message["tool_calls"]:
            for tool_call in message["tool_calls"]:
                id = tool_call.get("id", "No tool call id found")
                function_call = dict(tool_call.get("function", {}))
                func_print = f"***** Suggested tool call ({id}): {function_call.get('name', '(No function name found)')} *****"
                iostream.print(colored(func_print, "green"), flush=True)
                streaming_message += f"{func_print}\n"
                iostream.print(
                    "Arguments: \n",
                    function_call.get("arguments", "(No arguments found)"),
                    flush=True,
                    sep="",
                )
                streaming_message += f"Arguments: \n{function_call.get('arguments', '(No arguments found)')}\n"
                iostream.print(colored("*" * len(func_print), "green"), flush=True)
                streaming_message += f"{'*' * len(func_print)}\n"

    iostream.print("\n", "-" * 80, flush=True, sep="")
    streaming_message += f"\n{'-' * 80}\n"
    queue.put(
        {
            "index": index,
            "delta": {"role": "assistant", "content": streaming_message},
            "finish_reason": "stop",
        }
    )


llm_config = {"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}


class AutogenWorkflow:
    def __init__(self):
        self.queue: Queue | None = None
        self.user_proxy = UserProxyAgent(
            name="UserProxy",
            system_message="You are the UserProxy. You are the user in this conversation.",
            human_input_mode="NEVER",
            code_execution_config=False,
            llm_config=llm_config,
            description="The UserProxy is the user in this conversation. They will be interacting with the other agents in the group chat.",
        )
        self.mitch_hedberg = ConversableAgent(
            name="MitchHedberg",
            system_message="You are the comedian Mitch Hedberg. You are known for your surreal humor and deadpan delivery. Your comedy typically featured short, sometimes one-line jokes mixed with absurd elements and non sequitur",
            max_consecutive_auto_reply=3,
            human_input_mode="NEVER",
            code_execution_config=False,
            llm_config=llm_config,
            default_auto_reply="I used to do drugs. I still do, but I used to, too.",
            description="Mitch Hedberg was an American stand-up comedian known for his surreal humor and deadpan "
                        "delivery. His comedy typically featured short, sometimes one-line jokes mixed with absurd "
                        "elements and non sequiturs. Hedberg's comedy and onstage persona gained him a cult "
                        "following, with audience members sometimes shouting out the punchlines to his jokes before "
                        "he could finish them.",
        )
        self.greg_giraldo = ConversableAgent(
            name="GregGiraldo",
            system_message="You are the comedian Greg Giraldo. You are known for your acerbic style of humor and your appearances on Comedy Central's roasts. You are a former lawyer who turned to comedy full-time.",
            max_consecutive_auto_reply=3,
            human_input_mode="NEVER",
            code_execution_config=False,
            llm_config=llm_config,
            default_auto_reply="I'm not a good person, but I would like to be better.",
            description="Greg Giraldo was an American stand-up comedian, television personality, and lawyer. He is known for his acerbic style of humor and his appearances on Comedy Central's roasts. Giraldo was a former lawyer who turned to comedy full-time, and he was known for his sharp wit and biting commentary on a wide range of topics."
        )

        self.group_chat_with_introductions = GroupChat(
            agents=[
                self.user_proxy,
                self.mitch_hedberg,
                self.greg_giraldo,
            ],
            messages=[],
            max_round=10,
            send_introductions=True,
        )
        self.group_chat_manager_with_intros = GroupChatManager(
            groupchat=self.group_chat_with_introductions,
            llm_config=llm_config,
        )

    def set_queue(self, queue: Queue):
        self.queue = queue

    def run(
            self,
            message: str,
            stream: bool = False,
    ) -> ChatResult:

        if stream:
            # currently this streams the entire chat history, but you may want to return only the last message or a
            # summary
            index_counter = {"index": 0}
            queue = self.queue

            def streamed_print_received_message_with_queue_and_index(
                    self, *args, **kwargs
            ):
                streamed_print_received_message_with_queue = partial(
                    streamed_print_received_message,
                    queue=queue,
                    index=index_counter["index"],
                )
                bound_method = types.MethodType(
                    streamed_print_received_message_with_queue, self
                )
                result = bound_method(*args, **kwargs)
                index_counter["index"] += 1
                return result

            self.group_chat_manager_with_intros._print_received_message = types.MethodType(
                streamed_print_received_message_with_queue_and_index,
                self.group_chat_manager_with_intros,
            )

        chat_history = self.user_proxy.initiate_chat(
            self.group_chat_manager_with_intros, message=message,
        )
        if stream:
            self.queue.put("[DONE]")
        # currently this returns the entire chat history, but you may want to return only the last message or a summary
        return chat_history
