"""
19/09/2024
weihua
合并全部的论语文本
"""
import os

def merge_txt_files(folder_path, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')

folder_path = 'Lunyu_text'
output_file = 'all_lunyu.txt'
merge_txt_files(folder_path, output_file)