import os
import warnings
from dotenv import load_dotenv

class Agent:
    def __init__(self, role: str, goal: str, backstory: str, verbose: bool = True, allow_delegation: bool = False):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.allow_delegation = allow_delegation

    def execute(self, task_description: str, context: str = "") -> str:
        load_dotenv()
        system_instruction = (
            f"You are playing the role of: {self.role}\n"
            f"Your Goal: {self.goal}\n"
            f"Your Backstory: {self.backstory}\n"
        )
        prompt = ""
        if context:
            prompt += f"Context from previous tasks:\n{context}\n\n"
        prompt += f"Task to perform:\n{task_description}"
        
        if self.verbose:
            print(f"\n[Agent: {self.role}] Starting task...")

        if os.getenv("GEMINI_API_KEY"):
            try:
                from google import genai
                client = genai.Client()
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=dict(system_instruction=system_instruction)
                )
                if self.verbose:
                    print(f"[Agent: {self.role}] Completed task using Gemini.")
                return response.text
            except Exception as e:
                warnings.warn(f"Gemini API call failed: {e}. Trying OpenAI...")

        if os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                client = OpenAI()
                response = client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ]
                )
                if self.verbose:
                    print(f"[Agent: {self.role}] Completed task using OpenAI.")
                return response.choices[0].message.content
            except Exception as e:
                raise RuntimeError(f"OpenAI API call failed: {e}")

        raise RuntimeError("No API keys found. Please set GEMINI_API_KEY or OPENAI_API_KEY.")

class Task:
    def __init__(self, description: str, expected_output: str, agent: Agent):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        self.output = None

class Crew:
    def __init__(self, agents: list, tasks: list, process=None):
        self.agents = agents
        self.tasks = tasks
        
    def kickoff(self) -> str:
        context = ""
        last_output = ""
        for i, task in enumerate(self.tasks):
            output = task.agent.execute(task.description, context)
            task.output = output
            last_output = output
            context += f"\n### Output from Task {i+1} ({task.agent.role}):\n{output}\n"
        return last_output
