import os
import pandas as pd
import ollama
import subprocess

# === 🧠 Llama Agent ===
class BaseLlamaAgent:
    def __init__(self, name, personality, task_description, model='llama2:7b', temperature=0.4, top_k=5):
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

    def chat(self, input_text, codebook=None, role_description=None, previous_turn=None, output_format=None):
        base_content = f"Input:\n{input_text}"
        if codebook:
            base_content = f"Codebook:\n{codebook}\n\n{base_content}"
        if previous_turn:
            base_content += f"\n###\nThe previous turn said: {previous_turn}"
        if output_format:
            base_content += f"\n\nPlease format your output as follows:\n{output_format}"

        messages = [
            {'role': 'system', 'content': self.make_system_prompt(role_description)},
            {'role': 'user', 'content': base_content}
        ]

        response = ollama.chat(
            model=self.model,
            messages=messages,
            options=self.options
        )
        return response['message']['content']

# === 🔄 路径设置 ===
repo_path = r"D:\benchmark experiment\llm-gender-bias-in-education-benchmarking"
prompt_file = os.path.join(repo_path, "prompts", "generated_prompts.csv")
output_file = os.path.join(repo_path, "responses", "llama_responses.csv")

# === 🛠️ 确保 responses 目录存在 ===
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# === 📥 加载数据 ===
df = pd.read_csv(prompt_file)
if "prompt" not in df.columns:
    raise ValueError("❌ 未找到 'prompt' 列，请检查 CSV 文件。")

# === 🧠 初始化 Llama Agent ===
agent = BaseLlamaAgent(
    name="Sage",
    personality="careful and analytical",
    task_description="Evaluate student essays and provide structured feedback.",
    model="llama2:7b"
)

# === 🚀 批量生成响应 ===
responses = []
for i, prompt in enumerate(df["prompt"]):
    print(f"📝 正在处理第 {i+1} 条 prompt...")
    try:
        response = agent.chat(input_text=prompt)
        responses.append(response)
    except Exception as e:
        responses.append(f"[Error] {e}")
        print(f"⚠️ 第 {i+1} 条出错：{e}")

# === 💾 保存结果 ===
df["llama_response"] = responses
df.to_csv(output_file, index=False)
print(f"✅ 所有响应已保存至：{output_file}")

# === 🐙 可选：Git 推送 ===
try:
    os.chdir(repo_path)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "🤖 Add llama2:7b responses"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 改动已推送至 GitHub。")
except Exception as e:
    print(f"⚠️ Git 推送失败：{e}")
