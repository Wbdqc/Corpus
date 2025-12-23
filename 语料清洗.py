import os
import re
import jieba
import nltk
from docx import Document
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import wordsegment  # 导入新库
import zipfile  # 导入 zipfile 模块用于处理压缩包

# 下载 NLTK 和 wordsegment 所需数据
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
wordsegment.load()  # 加载 wordsegment 模型


# ============ 步骤 1: 提取 Word 文档文本 ============
def extract_text_from_docx(docx_path):
    """
    从 Word 文档中提取所有段落的文本。
    """
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])


# ============ 步骤 2: 中文清洗（含停用词处理）============
def clean_chinese(text, stopwords_source='chinese_stopwords.txt'):
    """
    清洗中文文本：去除特殊字符，分词，并去除停用词。
    支持从单个 .txt 文件、包含多个 .txt 文件的文件夹或 .zip 压缩包中加载停用词。
    """
    chinese_stop_words = set()

    try:
        if os.path.isfile(stopwords_source):
            if stopwords_source.endswith('.zip'):
                # 处理 .zip 压缩包
                with zipfile.ZipFile(stopwords_source, 'r') as zf:
                    for name in zf.namelist():
                        if name.endswith('.txt'):  # 只读取 .txt 文件
                            with zf.open(name) as f:
                                for line in f:
                                    chinese_stop_words.add(line.decode('utf-8').strip())
            else:
                # 处理单个 .txt 文件
                with open(stopwords_source, 'r', encoding='utf-8') as f:
                    for line in f:
                        chinese_stop_words.add(line.strip())
        elif os.path.isdir(stopwords_source):
            # 处理包含多个 .txt 文件的文件夹
            for filename in os.listdir(stopwords_source):
                if filename.endswith('.txt'):
                    filepath = os.path.join(stopwords_source, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            chinese_stop_words.add(line.strip())
        else:
            print(f"警告：停用词源 '{stopwords_source}' 无效或不存在。中文停用词处理将被跳过。")

    except FileNotFoundError:
        print(f"警告：未找到停用词源 '{stopwords_source}'。中文停用词处理将被跳过。")
    except Exception as e:
        print(f"读取停用词时发生错误：{e}。中文停用词处理将被跳过。")

    text = re.sub(r'[^\u4e00-\u9fa5]', '', text)  # 只保留中文字符
    words = jieba.lcut(text)  # 使用 jieba 进行分词

    # 去除停用词
    clean_words = [w for w in words if w.strip() and w not in chinese_stop_words]
    return ' '.join(clean_words)


# ============ 步骤 3: 英文清洗（含单词切分和词形还原）============
def clean_english_revised(text):
    """
    清洗英文文本：修复粘连词，去除标点，分词，去除停用词，并进行词形还原。
    """
    # 修复粘连词，例如 ruggeddangerous → rugged dangerous
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = text.lower()

    # 对可能粘连的词进行切分
    segmented_words = []
    for word in text.split():
        segmented_words.extend(wordsegment.segment(word))

    text = ' '.join(segmented_words)

    # 去除标点
    text = re.sub(r'[^\w\s]', '', text)

    # NLTK 分词
    words = word_tokenize(text)

    # 设置停用词
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    # 去停用词 + 词形还原
    clean_words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words and w.strip()]
    return ' '.join(clean_words)


# ============ 辅助函数: 获取文档路径 ============
def get_document_paths(source_path, doc_type='docx'):
    """
    从给定源获取文档路径列表。
    源可以是单个文件、目录或 zip 压缩包。
    """
    paths = []
    if os.path.isfile(source_path):
        if source_path.endswith(f'.{doc_type}'):
            paths.append(source_path)
        elif source_path.endswith('.zip'):
            with zipfile.ZipFile(source_path, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith(f'.{doc_type}'):
                        # 对于 zip 文件中的文件，我们需要一种方法来临时提取它们
                        # 或直接处理它们。为简单起见，我们假设对于 docx 文件，
                        # 不提取就无法直接处理。
                        # 目前，这只会列出 zip 中的路径。
                        # 在传递给 extract_text_from_docx 之前，需要实际提取。
                        # 在此示例中，我们将指示需要提取。
                        print(f"注意：文档 '{name}' 位于 zip 文件中。需要在处理前进行提取。")
                        # 要实际处理，您可以提取：
                        # zf.extract(name, path='temp_extracted_docs')
                        # paths.append(os.path.join('temp_extracted_docs', name))
                        pass  # 为保持简洁，此示例跳过实际提取
        else:
            print(f"警告：单个文件 '{source_path}' 不是 .{doc_type} 文件。已跳过。")
    elif os.path.isdir(source_path):
        for root, _, files in os.walk(source_path):
            for file in files:
                if file.endswith(f'.{doc_type}'):
                    paths.append(os.path.join(root, file))
    else:
        print(f"警告：文档源 '{source_path}' 无效或不存在。已跳过。")
    return paths


# ============ 步骤 4: 设置输入和输出路径 ============
# 请根据您的实际文件路径修改以下变量。
# 它们可以是：
# 1. 单个 .docx 文件的路径，例如：'E:\\zy'
# 2. 包含多个 .docx 文件的文件夹路径，例如：'E:\\zychinese_docs_folder'
# 3. 包含多个 .docx 文件的 .zip 压缩包路径，例如：'E:\\zy\\chinese_docs.zip'

chinese_input_source = 'E:\\zy\\chinese_raw.docx'  # 示例：一个文件夹
english_input_source = 'E:\\zy\\english_raw.docx'  # 示例：一个 zip 压缩包

output_dir = "E:\\zy\\cleaned_output\\"  # 创建一个专门的输出目录
os.makedirs(output_dir, exist_ok=True)

# 设置中文停用词源
# 您可以将其设置为：
# 1. 一个 .txt 文件的路径，例如：'E:\\zy\\chinese_stopwords.txt'
# 2. 一个包含多个 .txt 停用词文件的文件夹路径，例如：'E:\\zy\\chinese_stopwords_folder'
# 3. 一个包含多个 .txt 停用词文件的 .zip 压缩包路径，例如：'E:\\zy\\chinese_stopwords.zip'
chinese_stopwords_source = 'D:\PyCharm\\stopwords-master.zip'  # 默认示例为 .zip 压缩包

# ============ 步骤 5: 处理并保存 ============
print("开始处理文档...")

# 从源获取实际文档路径
chinese_docx_paths = get_document_paths(chinese_input_source, doc_type='docx')
english_docx_paths = get_document_paths(english_input_source, doc_type='docx')

# 处理中文文档
for docx_path in chinese_docx_paths:
    if not os.path.exists(docx_path):
        print(f"警告：未找到中文文档 '{docx_path}'。已跳过。")
        continue

    print(f"正在处理中文文档: {os.path.basename(docx_path)}")
    chinese_raw = extract_text_from_docx(docx_path)
    chinese_cleaned = clean_chinese(chinese_raw, stopwords_source=chinese_stopwords_source)

    # 以唯一名称保存结果
    output_filename = f"cleaned_chinese_{os.path.splitext(os.path.basename(docx_path))[0]}.txt"
    output_filepath = os.path.join(output_dir, output_filename)
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(chinese_cleaned)
    print(f"📄 中文清洗文本已保存至: {output_filepath}")

# 处理英文文档
for docx_path in english_docx_paths:
    if not os.path.exists(docx_path):
        print(f"警告：未找到英文文档 '{docx_path}'。已跳过。")
        continue

    print(f"正在处理英文文档: {os.path.basename(docx_path)}")
    english_raw = extract_text_from_docx(docx_path)
    english_cleaned = clean_english_revised(english_raw)

    # 以唯一名称保存结果
    output_filename = f"cleaned_english_{os.path.splitext(os.path.basename(docx_path))[0]}.txt"
    output_filepath = os.path.join(output_dir, output_filename)
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(english_cleaned)
    print(f"📄 英文清洗文本已保存至: {output_filepath}")

print("✅ Word 文档提取 + 中英文语料清洗完成！")

