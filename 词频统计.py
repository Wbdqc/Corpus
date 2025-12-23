import os
from collections import Counter
import re

# 设置文件夹路径
folder_path = 'E:\zy\'  # 替换为你的文件夹路径

# 自定义保存路径
output_path = 'E:\zy\'  # 替换为你希望保存的文件路径

# 初始化一个 Counter 对象来存储所有文件中的词频
word_counter = Counter()

# 遍历文件夹中的每个txt文件
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)

        # 打开文件并读取内容
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

            # 使用正则表达式去除非字母数字字符，并将所有字符转换为小写
            words = re.findall(r'\b\w+\b', text.lower())

            # 更新词频统计
            word_counter.update(words)

# 将词频统计结果保存到自定义路径的文件
with open(output_path, 'w', encoding='utf-8') as out_file:
    for word, freq in word_counter.most_common():
        out_file.write(f"{word}: {freq}\n")

print(f"词频统计完成，结果已保存到 {output_path}")

