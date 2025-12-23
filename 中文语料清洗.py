import os
import re
import jieba

# 设置输入和输出文件夹路径
input_folder = "E:\zy"  # 原始 txt 文件所在文件夹
output_folder = "E:\zy"  # 清洗后文件保存路径

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)


# 中文清洗函数：去除非中文字符 + jieba 分词 + 去除长度为1的词
def clean_chinese(text):
    text = re.sub(r'[^\u4e00-\u9fa5]', '', text)  # 只保留中文字符
    words = jieba.lcut(text)  # 使用jieba分词
    # 过滤掉空格和单个字符的词
    return ' '.join([w for w in words if len(w) > 1])


# 批量清洗文件函数
def process_files(input_folder, output_folder):
    # 获取文件夹中所有的 txt 文件
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):  # 只处理 txt 文件
            input_filepath = os.path.join(input_folder, filename)
            output_filepath = os.path.join(output_folder, filename)

            # 读取原始文件
            with open(input_filepath, "r", encoding="utf-8") as f:
                text = f.read()

            # 清洗文本
            cleaned_text = clean_chinese(text)

            # 将清洗后的文本保存到新文件
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(cleaned_text)

            print(f"✅ 已处理：{filename}")


# 执行批量处理
process_files(input_folder, output_folder)
print("📂 批量文件清洗完成！")

