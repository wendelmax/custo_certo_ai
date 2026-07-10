import os
import warnings
from dotenv import load_dotenv

OPENAI_COMPATIBLE_PROVIDERS = {
    "OPENAI_API_KEY":             {"base_url": None,                                "name": "OpenAI"},
    "GROQ_API_KEY":               {"base_url": "https://api.groq.com/openai/v1",    "name": "Groq"},
    "HYPER_API_KEY":              {"base_url": "https://api.hyper.charm.land/v1",   "name": "Hyper"},
    "OPENROUTER_API_KEY":         {"base_url": "https://openrouter.ai/api/v1",      "name": "OpenRouter"},
    "CEREBRAS_API_KEY":           {"base_url": "https://api.cerebras.ai/v1",        "name": "Cerebras"},
    "ALIBABA_SINGAPORE_API_KEY":  {"base_url": "https://api-inference.alibaba.com/v1",             "name": "Alibaba SG"},
    "ALIBABA_US_API_KEY":         {"base_url": "https://api-inference.us.alibaba.com/v1",          "name": "Alibaba US"},
    "ZAI_API_KEY":                {"base_url": "https://api.z.ai/v1",                "name": "Z.ai"},
    "MINIMAX_API_KEY":            {"base_url": "https://api.minimaxi.com/v1",        "name": "MiniMax"},
    "SYNTHETIC_API_KEY":          {"base_url": "https://api.synthetic.com/v1",       "name": "Synthetic"},
    "HF_TOKEN":                   {"base_url": "https://api-inference.huggingface.co/v1",          "name": "HuggingFace"},
    "AVIAN_API_KEY":              {"base_url": "https://api.avian.io/v1",            "name": "Avian"},
    "MOONSHOT_API_KEY":           {"base_url": "https://api.moonshot.cn/v1",         "name": "Moonshot"},
    "IONET_API_KEY":              {"base_url": "https://api.io.net/v1",              "name": "io.net"},
    "VERCEL_API_KEY":             {"base_url": "https://gateway.vercel.ai/v1",       "name": "Vercel"},
    "OPENCODE_API_KEY":           {"base_url": "https://api.opencode.ai/v1",         "name": "OpenCode"},
    "AZURE_OPENAI_API_KEY":       {"base_url": None,                                 "name": "Azure OpenAI"},
    "AWS_ACCESS_KEY_ID":          {"base_url": None,                                 "name": "Bedrock"},
    "VERTEXAI_PROJECT":           {"base_url": None,                                 "name": "VertexAI"},
}


def detect_openai_provider() -> dict | None:
    for env_var, config in OPENAI_COMPATIBLE_PROVIDERS.items():
        api_key = os.getenv(env_var)
        if api_key:
            base_url = os.getenv("OPENAI_BASE_URL") or config["base_url"]
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            return {
                "api_key": api_key,
                "base_url": base_url,
                "model": model,
                "provider": config["name"],
            }
    return None


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

        provider = detect_openai_provider()
        gemini_key = os.getenv("GEMINI_API_KEY")

        # Tentar Gemini primeiro
        if gemini_key:
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
                warnings.warn(f"Gemini API call failed: {e}. Trying alternative provider...")

        # Tentar OpenAI ou qualquer provider compatível
        if provider:
            try:
                from openai import OpenAI
                kwargs = {"api_key": provider["api_key"]}
                if provider["base_url"]:
                    kwargs["base_url"] = provider["base_url"]
                client = OpenAI(**kwargs)
                response = client.chat.completions.create(
                    model=provider["model"],
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ]
                )
                if self.verbose:
                    print(f"[Agent: {self.role}] Completed task using {provider['provider']} ({provider['model']}).")
                return response.choices[0].message.content
            except Exception as e:
                if provider["provider"] == "OpenAI":
                    raise RuntimeError(f"OpenAI API failed: {e}")
                raise RuntimeError(f"{provider['provider']} API failed: {e}")

        raise RuntimeError(
            "No API keys found. Set GEMINI_API_KEY or any OpenAI-compatible key "
            "(e.g. OPENAI_API_KEY, GROQ_API_KEY, HYPER_API_KEY)."
        )

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
