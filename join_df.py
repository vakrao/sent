import sys
import os 
import pandas as pd 
import numpy as np
import copy

def join_files_in_folder(folder):
    dir_list = os.listdir(folder)
    df_list = []
    for i, file_name in enumerate(dir_list):
        file_path = os.path.join(folder, file_name)
        if os.path.isfile(file_path):
            print(file_path)
            df_ = pd.read_csv(file_path,sep=",",encoding='utf-8')
            df_list.append(df_)
    concatenated_df = pd.concat(df_list, ignore_index=True)
    return concatenated_df      

if __name__ == "__main__":
    exp_folder = sys.argv[1]
    exp_type = sys.argv[2]
    full_folder =  f"{exp_folder}/{exp_type}/"
    output_file = f"{exp_folder}_{exp_type}.csv"
    concatenated_df = join_files_in_folder(full_folder)
    concatenated_df.to_csv(output_file, index=False)