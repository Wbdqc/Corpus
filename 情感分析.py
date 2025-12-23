import os
from textblob import TextBlob

# 设置文件夹路径和输出文件路径
folder_path = 'E:\\zy'  # 你存放txt文件的文件夹路径
output_file = 'E:\\zy'  # 输出文件路径

# 获取文件夹中所有的txt文件
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

# 打开输出文件以写入分析结果
try:
    with open(output_file, 'w', encoding='utf-8') as output:
        output.write("文件名\t情感极性\t情感主观性\t情感判断\t积极词汇\t中性词汇\t消极词汇\n")

        # 遍历所有的txt文件并进行情感分析
        for txt_file in txt_files:
            file_path = os.path.join(folder_path, txt_file)

            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            # 使用TextBlob进行情感分析
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # 极性
            subjectivity = blob.sentiment.subjectivity  # 主观性

            # 情感判断
            if polarity > 0:
                sentiment = '积极'
            elif polarity == 0:
                sentiment = '中性'
            else:
                sentiment = '消极'

            # 提取文本中的积极、中性和消极词汇
            positive_words = []
            neutral_words = []
            negative_words = []

            # 分词并对每个词进行情感分析
            for word in text.split():
                word_blob = TextBlob(word)
                word_polarity = word_blob.sentiment.polarity
                if word_polarity > 0:
                    positive_words.append(word)
                elif word_polarity == 0:
                    neutral_words.append(word)
                else:
                    negative_words.append(word)

            # 将结果写入输出文件
            output.write(f"{txt_file}\t{polarity}\t{subjectivity}\t{sentiment}\t"
                         f"{', '.join(positive_words)}\t{', '.join(neutral_words)}\t{', '.join(negative_words)}\n")

    print(f"情感分析已完成，结果保存在'{output_file}'中。")
except PermissionError as e:
    print(f"权限错误：{e}. 请确保文件夹路径和文件名正确，并且你有写入权限。")

