import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# 下载 NLTK 所需数据
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# 设置输入和输出文件夹路径
input_folder = "E:/zy/"  # 原始 txt 文件所在文件夹
output_folder = "E:/zy/"  # 清洗后文件保存路径

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)


# 英文清洗函数：小写化 + 分词 + 去标点 + 去停用词 + 词形还原
def clean_english(text):
    text = text.lower()  # 转小写
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    text = re.sub(r'\s+', ' ', text)  # 去除多余空白字符
    words = word_tokenize(text)  # 分词
    stop_words = set(stopwords.words('english'))  # 获取英文停用词
    lemmatizer = WordNetLemmatizer()  # 初始化词形还原器
    # 去停用词 + 词形还原 + 过滤单字符词
    cleaned_words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return ' '.join(cleaned_words)


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
            cleaned_text = clean_english(text)

            # 将清洗后的文本保存到新文件
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(cleaned_text)

            print(f"✅ 已处理：{filename}")


# 执行批量处理
process_files(input_folder, output_folder)
print("📂 批量英文文件清洗完成！")

