import os
import openpyxl
import requests
from bs4 import BeautifulSoup
import re


# 加载 Excel 文件
def load_excel(file_path):
    # 打开 Excel 文件
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active  # 选择活动表格
    return sheet


# 从 Excel 表格中提取链接和标题
def extract_data(sheet):
    data = []
    for row in sheet.iter_rows(min_row=2, max_col=2, values_only=True):  # 假设标题在第一列，链接在第二列
        title = row[0]
        link = row[1]
        if title and link and link.startswith("http"):  # 确保是有效的标题和 URL
            data.append((title, link))
    return data


# 提取网页正文内容，清除不必要的 HTML 标签
def extract_main_content(url):
    try:
        print(f"正在请求：{url}")  # 增加调试输出
        response = requests.get(url, timeout=10)  # 设置超时时间为10秒
        response.raise_for_status()  # 如果请求失败会抛出异常
        print(f"请求成功：{url}")  # 成功时输出

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找正文部分，假设内容可能在 <article>、<main> 或 <div id="Content"> 中
        content_div = soup.find(['article', 'main', 'div'], {'id': 'Content'})
        if not content_div:
            content_div = soup.find('body')  # 如果没有找到具体内容区域，就获取整个 body

        # 清除头部、尾部、广告、导航等不相关部分
        for element in content_div.find_all(['header', 'footer', 'aside', 'nav', 'script', 'style']):
            element.decompose()

        # 获取清理后的正文文本
        content = content_div.get_text(separator=' ', strip=True)

        return content

    except requests.exceptions.Timeout:
        print(f"请求超时，跳过链接 {url}")  # 超时处理
        return ""  # 如果请求超时，返回空内容，继续处理下一个链接
    except Exception as e:
        print(f"无法提取内容 ({url}): {e}")  # 捕获其他异常
        return ""


# 将正文保存为 TXT 文件
def save_link_to_txt(data, output_dir):
    # 创建保存路径
    os.makedirs(output_dir, exist_ok=True)

    for i, (title, link) in enumerate(data, 1):
        content = extract_main_content(link)
        if content:
            # 使用标题作为文件名，移除文件名中的非法字符
            safe_title = "".join([c if c.isalnum() or c in (' ', '_', '-') else '_' for c in title])
            filename = os.path.join(output_dir, f"{safe_title}.txt")

            # 保存文件
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"成功保存链接 {i} 到 {filename}")
        else:
            print(f"链接 {i} 没有提取到有效内容")


# 主函数
def main():
    excel_path = "E:\zy"  # 替换成你的 Excel 文件路径
    output_dir = "E:\zy\"  # 替换成你希望导出的文件夹路径

    sheet = load_excel(excel_path)
    data = extract_data(sheet)
    save_link_to_txt(data, output_dir)


if __name__ == "__main__":
    main()

