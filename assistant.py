from openai import OpenAI
import json

client = OpenAI()

assistant = client.beta.assistants.create(
    name="Han Solo",
    instructions="You are a Personal Assistant to a Land Development business.",
    model="gpt-3.5-turbo-1106",
    tools=[{"type": "code_interpreter", "type": "retrieval"}],
)
