!pip install openai pandas
import os
import pandas as pd
import time
from getpass import getpass
from openai import OpenAI

openai_api_key = getpass("🔐 请输入你的 OpenAI API Key: ")
client = OpenAI(api_key=openai_api_key)

GITHUB_USERNAME = "Yishandu13"
GITHUB_REPO_NAME = "llm-gender-bias-in-education-benchmarking"
REPO_PATH = f"/content/{GITHUB_REPO_NAME}"

if not os.path.exists(REPO_PATH):
    from getpass import getpass
    GITHUB_TOKEN = getpass("🔐 输入 GitHub Token（用于克隆仓库）:")
    REPO_URL = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}.git"
    !git clone {REPO_URL}

# 切换到 repo
os.chdir(REPO_PATH)

# 读取 prompts CSV
df = pd.read_csv("prompts/generated_prompts.csv")

# ✅ 模型选择
model = "gpt-4o-mini"

# ✅ 存储响应
responses = []
error_count = 0

for i, prompt in enumerate(df["prompt"]):
    print(f"🚀 正在处理第 {i+1} 个 prompt...")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )

        content = response.choices[0].message.content
        responses.append(content)

    except Exception as e:
        error_count += 1
        print(f"❌ GPT 调用出错：{e}")
        responses.append(f"ERROR: {str(e)}")

# ✅ 添加新列
df["gpt_response"] = responses

# ===================== 💾 STEP 5: 保存 response 到 repo ========================
output_path = os.path.join(REPO_PATH, "responses")
os.makedirs(output_path, exist_ok=True)
response_file = os.path.join(output_path, "gpt4o_responses.csv")
df.to_csv(response_file, index=False)
print(f"✅ 所有 responses 已写入 {response_file}")

# ===================== 🚀 STEP 6: Git 提交并推送 ========================
!git config user.email "yishan.24@ucl.ac.uk"  # 替换为你的 GitHub 邮箱
!git config user.name "Yishandu13"              # 替换为你的 GitHub 用户名

!git add responses/gpt4o_responses.csv
!git commit -m "🤖 Add GPT-4o responses"
!git push origin main

print("✅ 成功推送到 GitHub！🎉")
print(f"⚠️ 出错总数：{error_count}")
