import subprocess
import sys

# 自动安装 ollama，如果尚未安装
try:
    import ollama
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    import ollama

import os
import pandas as pd
import subprocess

# 🗂️ 设置路径（请根据实际路径调整）
repo_path = r"D:\benchmark experiment\llm-gender-bias-in-education-benchmarking"
prompt_csv_path = os.path.join(repo_path, "prompts", "generated_prompts.csv")
response_folder = os.path.join(repo_path, "responses_llama")
response_csv_path = os.path.join(response_folder, "generated_responses.csv")

# ✅ 确保输出文件夹存在
os.makedirs(response_folder, exist_ok=True)

# ✅ 读取 prompts
df = pd.read_csv(prompt_csv_path)

# ✅ 调用 LLaMA 模型
class BaseLlamaAgent:
    def __init__(self, name, personality, task_description, model='llama3', temperature=0.4, top_k=5):
        self.name = name
        self.personality = personality
        self.task_description = task_description
        self.model = model
        self.options = {
            'temperature': temperature,
            'top_k': top_k
        }

    def make_system_prompt(self, role=None):
        role_text = f" Your role: {role}" if role else ""
        return f"""
        You are {self.name}, a {self.personality} language model agent.{role_text}
        Your task: {self.task_description}
        Use any provided reference materials or definitions to perform your task.
        Be concise (2 sentences max per response), reflective, and justify your reasoning when appropriate.
        After your reasoning, conclude your response in the expected output format if specified.
        """

    def chat(self, input_text, role_description=None):
        messages = [
            {'role': 'system', 'content': self.make_system_prompt(role_description)},
            {'role': 'user', 'content': input_text}
        ]
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options=self.options
        )
        return response['message']['content']

# ✅ 实例化 Agent
agent = BaseLlamaAgent(
    name="Sage",
    personality="careful and analytical",
    task_description="Provide constructive feedback and evaluation on student writing"
)

# ✅ 遍历每条 prompt 调用模型
responses = []
for i, row in df.iterrows():
    prompt = row['prompt']
    try:
        print(f"🔍 Generating response for prompt {i+1}/{len(df)}")
        response = agent.chat(prompt)
        responses.append(response)
    except Exception as e:
        print(f"❌ Error for prompt {i}: {e}")
        responses.append("ERROR")

# ✅ 写入新列并保存
df["llama_response"] = responses
df.to_csv(response_csv_path, index=False)
print(f"✅ Responses saved to: {response_csv_path}")

# ✅ Git 提交并推送
os.chdir(repo_path)
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", "🤖 Add llama responses"])
subprocess.run(["git", "push"])
print("🚀 Responses pushed to GitHub.")