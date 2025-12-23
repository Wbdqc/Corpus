import os
import glob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

# 加载spaCy英文模型
nlp = spacy.load("en_core_web_trf")


class BiberAnalyzer:
    def __init__(self):
        # 词汇表和停用词
        self.stop_words = set(stopwords.words('english'))
        self.modal_verbs = {'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would'}
        self.conjuncts = {'however', 'therefore', 'moreover', 'furthermore', 'nevertheless', 'consequently',
                          'otherwise', 'meanwhile'}

    def preprocess(self, text):
        """文本预处理：去除标点符号，并进行小写化"""
        text = re.sub(r'[^\w\s]', '', text.lower())
        return word_tokenize(text)

    def analyze_text(self, text):
        """分析单篇文本的所有维度"""
        # 使用spaCy进行高级分析
        doc = nlp(text)

        # 基础统计
        word_count = len([token.text for token in doc if not token.is_punct])
        sentence_count = len(list(doc.sents))

        # 如果文本为空，返回所有维度为0
        if word_count == 0:
            return {f"dim{i}": 0 for i in range(1, 7)}

        # 维度计算
        dim1 = self._dimension_1(doc, word_count)
        dim2 = self._dimension_2(doc, word_count)
        dim3 = self._dimension_3(doc, word_count)
        dim4 = self._dimension_4(doc, word_count)
        dim5 = self._dimension_5(doc, word_count)
        dim6 = self._dimension_6(doc, sentence_count)

        return {
            "dim1": dim1,
            "dim2": dim2,
            "dim3": dim3,
            "dim4": dim4,
            "dim5": dim5,
            "dim6": dim6
        }

    # 维度计算方法 (与之前保持一致)
    def _dimension_1(self, doc, word_count):
        """维度1: Involved vs Informational"""
        noun_count = sum(1 for token in doc if token.pos_ == 'NOUN')
        verb_count = sum(1 for token in doc if token.pos_ == 'VERB')
        pronoun_count = sum(1 for token in doc if token.pos_ == 'PRON')
        adj_count = sum(1 for token in doc if token.pos_ == 'ADJ')
        avg_word_len = np.mean([len(token.text) for token in doc if not token.is_punct])
        return (verb_count + pronoun_count - noun_count - adj_count - avg_word_len) / word_count

    def _dimension_2(self, doc, word_count):
        """维度2: Narrative vs Non-Narrative"""
        past_tense_count = sum(1 for token in doc if token.tag_ == 'VBD')
        third_person_pronouns = sum(1 for token in doc if
                                    token.text.lower() in {'he', 'him', 'his', 'she', 'her', 'it', 'they', 'them',
                                                           'their'})
        return (past_tense_count + third_person_pronouns) / word_count

    def _dimension_3(self, doc, word_count):
        """维度3: Context-Independent vs Context-Dependent"""
        nominalizations = sum(
            1 for token in doc if token.pos_ == 'NOUN' and token.text.endswith(('tion', 'ment', 'ness', 'ity')))
        adverb_count = sum(1 for token in doc if token.pos_ == 'ADV')
        return (nominalizations - adverb_count) / word_count

    def _dimension_4(self, doc, word_count):
        """维度4: Overt Expression of Persuasion"""
        # 使用自定义的模态动词和连接词
        modal_count = sum(1 for token in doc if token.text.lower() in self.modal_verbs)
        conjunct_count = sum(1 for token in doc if token.text.lower() in self.conjuncts)
        # 计算维度4的得分
        dim4_score = (modal_count + conjunct_count) / word_count
        return dim4_score

    def _dimension_5(self, doc, word_count):
        """维度5: Abstract vs Non-Abstract"""
        passive_count = self._count_passive_voice(doc)
        conjunct_count = sum(1 for token in doc if token.text.lower() in self.conjuncts)
        return (passive_count + conjunct_count) / word_count

    def _dimension_6(self, doc, sentence_count):
        """维度6: On-line Informational Elaboration"""
        postmodification_count = self._count_postmodifications(doc)
        return postmodification_count / sentence_count  # 按句子标准化

    def _count_passive_voice(self, doc):
        """计算被动语态数量"""
        passive_count = sum(
            1 for token in doc if token.dep_ == "auxpass" or (token.tag_ == "VBN" and token.dep_ == "ROOT"))
        return passive_count

    def _count_postmodifications(self, doc):
        """计算名词短语后置修饰数量"""
        postmod_count = sum(1 for noun_chunk in doc.noun_chunks if
                            any(child.dep_ in {"prep", "relcl", "acl"} for child in noun_chunk.root.children))
        return postmod_count

    def analyze_files_in_directory(self, folder_path):
        """分析文件夹中的所有txt文件"""
        files = glob.glob(os.path.join(folder_path, '*.txt'))
        results = []
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                dim_scores = self.analyze_text(text)
                results.append({
                    "file_name": os.path.basename(file_path),
                    **dim_scores
                })
        return pd.DataFrame(results)

    def visualize_dimensions(self, results_df):
        """可视化维度分析结果"""
        plt.figure(figsize=(14, 10))

        # 维度分布直方图
        plt.subplot(2, 2, 1)
        for dim in [f"dim{i}" for i in range(1, 7)]:
            sns.kdeplot(results_df[dim], label=f"Dimension {dim[-1]}")
        plt.title("Biber Dimension Score Distributions")
        plt.xlabel("Score")
        plt.legend()

        # 按类别的维度对比
        plt.subplot(2, 2, 2)
        if "category" in results_df.columns:
            category_dim = results_df.groupby("category")[[f"dim{i}" for i in range(1, 7)]].mean()
            sns.heatmap(category_dim, annot=True, cmap="coolwarm",
                        linewidths=.5, cbar_kws={'label': 'Average Score'})
            plt.title("Average Dimension Scores by Category")

        # 维度间相关性
        plt.subplot(2, 2, 3)
        corr_matrix = results_df[[f"dim{i}" for i in range(1, 7)]].corr()
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm",
                    vmin=-1, vmax=1, center=0, fmt=".2f")
        plt.title("Correlation Between Dimensions")

        # 按来源的维度对比
        plt.subplot(2, 2, 4)
        if "source" in results_df.columns:
            source_dim = results_df.groupby("source")[[f"dim{i}" for i in range(1, 7)]].mean()
            source_dim.plot(kind="bar", stacked=True, colormap="viridis")
            plt.title("Dimension Composition by Source")
            plt.ylabel("Average Score")
            plt.legend(title="Dimension", bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.savefig("biber_dimension_analysis.png", dpi=300)
        plt.show()

    def save_results(self, results_df, output_path):
        """保存分析结果到指定路径"""
        results_df.to_csv(output_path, index=False)


# 使用示例
if __name__ == "__main__":
    # 1. 设置文件夹路径（包含多个txt文件）
    folder_path = 'E:\zy\'

    # 2. 设置自定义输出路径
    output_path = 'E:/zy/biber_dimension_scores.csv'

    # 3. 初始化分析器
    analyzer = BiberAnalyzer()

    # 4. 分析文件夹中的所有txt文件
    results = analyzer.analyze_files_in_directory(folder_path)

    # 5. 查看结果
    print("Biber Dimension Analysis Results:")
    print(results)

    # 6. 可视化结果
    analyzer.visualize_dimensions(results)

    # 7. 保存结果到指定路径
    analyzer.save_results(results, output_path)

