"""
Module for handling interactions with OpenAI's Assistants API, 
facilitating thread and message management.
"""

# Standard library imports
import json
import time

# Third-party imports
import openai

class OpenAIAssistant:
    """
    Class to interact with OpenAI's Assistants APIs, managing threads and messages.
    """

    def __init__(self, assistant_id) -> None:
        """
        Initialize the OpenAI assistant client with the provided assistant ID.
        """
        # gets API Key from environment variable OPENAI_API_KEY
        self.client = openai.OpenAI()
        self.assistant_id = assistant_id
        self.assistant = self.client.beta.assistants.retrieve(assistant_id)
        self.thread_locks = {}

    def _process_run_thread(self, thread_id):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )
        i = 0
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run.status == 'requires_action':
                # Accessing the required action's tool calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                print(tool_calls)
                if tool_calls:
                    # Assuming tool_calls is a list or a similar iterable of RequiredActionFunctionToolCall objects
                    function_call = tool_calls[0]  # If there's more than one, you might want to handle them all or choose one
                    arguments = json.loads(function_call.function.arguments)
                    return function_call.function.name, arguments  # Directly accessing the 'function' attribute
            elif run.status == 'completed':
                # Return None or an indication that the run completed without requiring a function call
                return None
            i += 1
            if i == 240:
                del self.thread_locks[thread_id]
                raise Exception("Timed out while waiting for thread to run.")
            time.sleep(0.5)

    def run_thread(self, thread_id):
        """
        Run a thread for a given ID, waiting until completion or timeout.
        """
        if thread_id not in self.thread_locks:
            self.thread_locks[thread_id] = []

        try:
            return self._process_run_thread(thread_id)
        finally:
            if len(self.thread_locks[thread_id]) > 0:
                for msg in self.thread_locks[thread_id]:
                    self.new_message(thread_id, msg)
                return self._process_run_thread(thread_id)
            del self.thread_locks[thread_id]

    def check_queue(self, thread_id):
        if thread_id in self.thread_locks:
            if len(self.thread_locks[thread_id]) > 0:
                for msg in self.thread_locks[thread_id]:
                    self.new_message(thread_id, msg)
                self.run_thread(thread_id)

    def _latest_bot_message(self, history):
        result = {}
        if history and history.data:
            latest_entry = history.data[0]
            msg = []
            for content in latest_entry.content:
                txt = content.text.value
                msg.append(txt)
            result['msg'] = "\n".join(msg)
            result['id'] = latest_entry.id
        else:
            # TODO: return {"msg": "", "id": openai_msg_id}
            result['msg'] = ""
            result['id'] = None
        return result

    def new_thread(self):
        """
        Create a new thread.
        """
        thread = self.client.beta.threads.create()
        return thread

    def new_message(self, thread_id, msg):
        """
        Create a new message in a specified thread.
        """
        if thread_id in self.thread_locks:
            self.thread_locks[thread_id].append(msg)
        else:
            try:
                self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=msg
                )
                return self.run_thread(thread_id)
            except openai.BadRequestError as err:
                if "Can't add messages to thread" in err.message:
                    # Extract the run_id from the error message
                    run_id = self._extract_run_id(err.message)
                    tool_outputs = []
                    print(run_id)
                    if run_id:
                        run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                        tool_calls = run.required_action.submit_tool_outputs.tool_calls
                        print(tool_calls)
                        if tool_calls:
                            tool_outputs.append({"tool_call_id": tool_calls[0].id, "output": msg})
                            # Submit all tool_outputs at the same time
                            self.submit_tool_outputs(tool_outputs, thread_id, run_id)
    
    def submit_tool_outputs(self, tool_outputs, thread_id, run_id):
        # Use the submit_tool_outputs_stream helper
        i = 0
        self.client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run.status == 'completed':
                # Return None or an indication that the run completed without requiring a function call
                return None
            else:
                print(run.status)
            i += 1
            if i == 120:
                #del self.thread_locks[thread_id]
                raise Exception("Timed out while waiting for thread to run.")
            time.sleep(0.5)

    def _extract_run_id(self, error_message):
        """
        Extract run_id from the error message.
        """
        import re
        match = re.search(r'run_(\w+)', error_message)
        if match:
            return match.group(0)  # Return the full run_id (e.g., run_Qokq2uimXksqhrgPwifoRww3)
        return None

    def _refresh_thread(self, thread_id):
        """
        Retrieve all messages from a specified thread.
        """
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages

    def get_last_message(self, thread_id) -> dict:
        latest = self._latest_bot_message(self._refresh_thread(thread_id))
        return latest
