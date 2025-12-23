import os
import re
import nltk
import gensim
import pandas as pd
from gensim import corpora
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# 下载停用词
nltk.download('punkt')
nltk.download('stopwords')

# 自定义数据路径和保存路径
input_folder = 'E:\\zy'  # 输入文件夹路径
output_path = 'E:\\zy\'  # 输出结果路径


# 读取所有txt文件
def read_files(input_folder):
    texts = []
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as file:
                text = file.read().lower()  # 转为小写
                texts.append(text)
    return texts


# 文本预处理：去除停用词、数字和标点符号，保留带连字符的词语
def preprocess_text(texts):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    processed_texts = []

    for text in texts:
        # 使用正则表达式来保留字母和连字符的单词
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if re.match(r'^[A-Za-z-]+$', word)]  # 允许字母和连字符
        tokens = [word for word in tokens if word not in stop_words]  # 去掉停用词
        processed_texts.append(tokens)

    return processed_texts


# 生成词袋和字典
def create_corpus(processed_texts):
    dictionary = corpora.Dictionary(processed_texts)
    corpus = [dictionary.doc2bow(text) for text in processed_texts]
    return dictionary, corpus


# LDA模型训练
def lda_model(corpus, dictionary, num_topics=3):
    lda = gensim.models.LdaMulticore(corpus, num_topics=num_topics, id2word=dictionary, passes=10, workers=2)
    return lda


# 计算困惑度
def calculate_perplexity(lda, corpus):
    perplexity = lda.log_perplexity(corpus)  # 计算困惑度
    return perplexity


# 保存LDA模型的主题结果
def save_results(lda_model, perplexity, output_path):
    topics = []
    for i, topic in lda_model.print_topics(num_words=5):
        topics.append(f"Topic {i}: {topic}")

    # 保存结果到CSV
    df = pd.DataFrame(topics, columns=['Topic'])
    df['Perplexity'] = perplexity
    df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    print(f"Perplexity of the model: {perplexity}")


# 主函数
def main():
    texts = read_files(input_folder)
    processed_texts = preprocess_text(texts)
    dictionary, corpus = create_corpus(processed_texts)

    # 训练LDA模型
    lda = lda_model(corpus, dictionary)

    # 计算困惑度
    perplexity = calculate_perplexity(lda, corpus)

    # 保存结果和困惑度
    save_results(lda, perplexity, output_path)


if __name__ == '__main__':
    main()

