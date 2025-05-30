import pandas as pd
import re

# === 读取 Excel ===
df = pd.read_excel("demo male counterfactual v2.xlsx")
df.columns = ['ID', 'essay', 'original_word', 'counterfactual_word']

# === 构建词汇对照表（全局 B ➝ C 映射） ===
word_map = dict(zip(df['original_word'].str.lower(), df['counterfactual_word']))

# === 获取所有 unique 句子，确保无缺失并转为字符串 ===
unique_essays = df['essay'].dropna().astype(str).unique()

# === 保留大小写格式的替换函数 ===
def match_case(original, replacement):
    if original.isupper():
        return replacement.upper()
    elif original[0].isupper():
        return replacement.capitalize()
    else:
        return replacement.lower()

# === 替换函数：精准匹配、高亮版本 ===
def replace_with_highlight(text, word_map):
    def replacer(match):
        original = match.group(0)
        replacement = word_map.get(original.lower(), original)
        replaced = match_case(original, replacement)
        return f"<span style='background-color:yellow;font-weight:bold;'>{replaced}</span>"

    pattern = r'\b(' + '|'.join(re.escape(w) for w in word_map) + r')\b'
    return re.sub(pattern, replacer, text, flags=re.IGNORECASE)

# === 替换函数：纯文本版本 ===
def replace_plain(text, word_map):
    def replacer(match):
        original = match.group(0)
        replacement = word_map.get(original.lower(), original)
        return match_case(original, replacement)

    pattern = r'\b(' + '|'.join(re.escape(w) for w in word_map) + r')\b'
    return re.sub(pattern, replacer, text, flags=re.IGNORECASE)

# === 批量处理 ===
results = []
html_table_rows = ""

for text in unique_essays:
    highlighted = replace_with_highlight(text, word_map)
    plain = replace_plain(text, word_map)

    results.append({
        "original_text": text,
        "counterfactual_plain": plain
    })

    html_table_rows += f"<tr><td>{text}</td><td>{highlighted}</td></tr>\n"

# === 保存纯文本 Excel ===
df_plain = pd.DataFrame(results)
df_plain.to_excel("malecounterfactualessay_plain.xlsx", index=False)

# === 构建并保存 HTML 文件 ===
html_str = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Counterfactual Highlight</title>
<style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 10px; vertical-align: top; }}
    th {{ background-color: #f2f2f2; }}
</style>
</head>
<body>
<h2>Counterfactual Text Highlighting</h2>
<table>
<tr><th>Original Essay</th><th>Counterfactual with Highlight</th></tr>
{html_table_rows}
</table>
</body>
</html>
"""

with open("malecounterfactualessay_highlighted.html", "w", encoding="utf-8") as f:
    f.write(html_str)

print("✅ 完成：生成了纯文本 Excel 和高亮 HTML 文件")
