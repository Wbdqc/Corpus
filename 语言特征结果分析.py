import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用于中文显示
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

def analyze_translations():
    """
    分析AI译文与人工译文的Biber维度得分差异
    """
    # 设置输入和输出路径
    input_file = r"E:\zy\biber_dimension_scores.csv"
    output_dir = r"E:\zy"

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 读取数据
    df = pd.read_csv(input_file)

    # 分离数据
    ai_data = df[df['file_name'].str.contains('DeepSeek')]
    human_data = df[~df['file_name'].str.contains('DeepSeek')]

    # 确保成功分离
    if len(ai_data) == 0:
        raise ValueError("未找到AI译文数据（文件名应包含'DeepSeek'）")
    if len(human_data) == 0:
        raise ValueError("未找到人工译文数据")

    # 计算描述性统计
    dimensions = [col for col in df.columns if col.startswith('dim')]
    human_stats = human_data[dimensions].describe().loc[['mean', 'std', 'min', 'max', '25%', '50%', '75%']].T
    human_stats.columns = ['人工均值', '标准差', '最小值', '最大值', '25分位', '中位数', '75分位']

    # 合并统计信息
    ai_scores = ai_data[dimensions].squeeze()
    comparison_df = pd.DataFrame({
        'AI得分': ai_scores,
        '人工均值': human_stats['人工均值'],
        '差异': ai_scores - human_stats['人工均值'],
        '与人工均值的标准差': (ai_scores - human_stats['人工均值']) / human_stats['标准差'],
        '人工范围': human_stats.apply(lambda x: f"[{x['最小值']:.3f}, {x['最大值']:.3f}]", axis=1),
        '低于AI值的人工样本占比': [np.mean(human_data[dim] < ai_scores[dim]) for dim in dimensions]
    })

    # 保存统计分析结果
    stats_output = output_path / "statistical_analysis.csv"
    comparison_df.to_csv(stats_output, index=True)
    print(f"统计分析结果已保存至: {stats_output}")

    # 可视化分析
    plt.style.use('ggplot')

    # 1. 雷达图比较
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'polar': True})
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()

    # 完成环形
    ai_values = ai_scores.tolist()
    ai_values.append(ai_values[0])
    human_values = comparison_df['人工均值'].tolist()
    human_values.append(human_values[0])
    angles_complete = angles + [angles[0]]

    # 绘图
    ax.plot(angles_complete, ai_values, 'o-', linewidth=2, label='AI译文', markersize=8)
    ax.plot(angles_complete, human_values, 's-', linewidth=2, label='人工平均', markersize=8)

    # 添加填充区域表示人工范围
    min_values = comparison_df.index.map(lambda dim: human_stats.loc[dim, '最小值']).tolist()
    max_values = comparison_df.index.map(lambda dim: human_stats.loc[dim, '最大值']).tolist()
    min_values.append(min_values[0])
    max_values.append(max_values[0])
    ax.fill(angles_complete, min_values, alpha=0.1, color='green', label='人工范围(最小值)')
    ax.fill(angles_complete, max_values, alpha=0.1, color='blue', label='人工范围(最大值)')

    # 设置标签
    ax.set_xticks(angles)
    ax.set_xticklabels(dimensions, fontsize=12)
    ax.set_title('译文风格维度对比', fontsize=16, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1), fontsize=12)

    # 保存雷达图
    radar_output = output_path / "radar_comparison.png"
    plt.savefig(radar_output, bbox_inches='tight')
    print(f"雷达图已保存至: {radar_output}")
    plt.close()

    # 2. 差异柱状图
    plt.figure(figsize=(12, 6))
    comparison_df['差异'].plot(kind='bar', color=np.where(comparison_df['差异'] >= 0, 'skyblue', 'salmon'))
    plt.axhline(0, color='gray', linewidth=0.8)
    plt.title('AI译文与人工平均在各维度的差异', fontsize=16)
    plt.ylabel('差异值 (AI - 人工平均)', fontsize=12)
    plt.xlabel('维度', fontsize=12)
    plt.xticks(rotation=45, ha='right')

    # 添加差异数值标签
    for i, diff in enumerate(comparison_df['差异']):
        plt.text(i, diff + 0.01 * np.sign(diff), f"{diff:.3f}",
                 ha='center', va='bottom' if diff >= 0 else 'top', fontsize=10)

    # 保存差异图
    diff_output = output_path / "dimension_differences.png"
    plt.savefig(diff_output, bbox_inches='tight')
    print(f"差异柱状图已保存至: {diff_output}")
    plt.close()

    # 3. 相关矩阵热力图 (仅人工译文)
    plt.figure(figsize=(10, 8))
    corr_matrix = human_data[dimensions].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt=".2f",
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
    plt.title('人工译文各维度相关性热力图', fontsize=16)
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)

    # 保存热力图
    heatmap_output = output_path / "correlation_heatmap.png"
    plt.savefig(heatmap_output, bbox_inches='tight')
    print(f"相关热力图已保存至: {heatmap_output}")
    plt.close()

    # 4. 各维度分布箱线图
    plt.figure(figsize=(12, 8))
    human_long = human_data.melt(id_vars='file_name', value_vars=dimensions,
                                 var_name='dimension', value_name='score')
    sns.boxplot(x='dimension', y='score', data=human_long)

    # 添加AI译文点
    for i, dim in enumerate(dimensions):
        plt.scatter(i, ai_scores[dim], s=100, color='red', marker='D', edgecolor='black',
                    label='AI译文' if i == 0 else None)

    plt.title('各维度得分分布比较（人工译文箱线图 + AI译文点）', fontsize=16)
    plt.xlabel('维度', fontsize=12)
    plt.ylabel('得分', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend()

    # 保存箱线图
    boxplot_output = output_path / "dimension_distribution.png"
    plt.savefig(boxplot_output, bbox_inches='tight')
    print(f"维度分布图已保存至: {boxplot_output}")
    plt.close()

    print(f"所有分析结果已保存至: {output_path.absolute()}")


if __name__ == "__main__":
    try:
        analyze_translations()
        print("分析完成！")
    except Exception as e:
        print(f"分析过程中出错: {e}")
        print("请确保输入文件格式正确（CSV格式，包含file_name, dim1, dim2, ...列）")

        print("文件名中AI译文应包含'DeepSeek'以便识别")
