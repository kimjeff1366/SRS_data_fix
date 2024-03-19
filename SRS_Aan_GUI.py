import PySimpleGUI as sg  
import re
import numpy as np
import os
#建立GUI窗口
layout = [
[sg.Text('选择原始数据文件')],
[sg.In(),sg.FileBrowse()],
[sg.Text("请输入SRS文件名")],  
[sg.InputText()],
[sg.Text('选择SRS文件存储位置')],
[sg.In(),sg.FolderBrowse()],
[sg.Button("提交")]
          ]    
window = sg.Window("SRS数据处理程序", layout)   
while True:  
    event, values = window.read()  
    if event == sg.WINDOW_CLOSED:  
        break  
    if event == "提交":
        file_path=values[0]  
        srs_file_name = values[1] 
        storage_location=values[2] 
#打开文件
        with open(file_path, 'r') as file:
            content = file.read()
#匹配初始时刻，赋到FT
        pattern_FT = r'Time of first sample\s+:\s*(-\d+\.\d+)' 
        matches = re.search(pattern_FT, content)
        if matches:
            FT = float(matches.group(1))
        else:
            FT = None
#匹配时间间隔，赋到DT
        pattern_DT = r"Sampling interval\s*:\s*([0-9\.E-]+)"
        matches = re.search(pattern_DT, content)
        if matches:
            DT = float(matches.group(1))
        else:
            DT = None
#匹配数据个数，赋到N
        pattern_N = r"Number of samples\s*:\s*(\d+)"
        matches = re.search(pattern_N, content)
        if matches:
            N = int(matches.group(1))
        else:
            N = None
# 提取第二列数据
        with open(file_path, 'r') as file:
            lines = file.readlines()
        data = []
        for line in lines:
            if re.match(r"[-+]?\d+\.\d+[eE][-+]?\d+", line): 
                data.append(float(line.strip()))  
#连接组成二维数组at
        Time_sieries = [FT + i * DT for i in range(N)]
        at = np.column_stack((Time_sieries, data))
#截取时间从0到0.2s的部分除以9.81，组成新的二维数组at_subset_g
        mask = (at[:,0] >= 0) & (at[:,0] <= 0.2)
        at_subset = at[mask]
        at_subset_g=np.copy(at_subset)
        at_subset_g[:,1]=at_subset[:,1]/9.81
        GT=[]
        if DT==5e-5:
            for i in range(0,len(at_subset_g),2):
                GT.append(at_subset_g[i])
        else:
            GT=at_subset_g
        GT = np.array(GT)
#输出
        folder_path = storage_location
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, srs_file_name)
        SRS_data=GT[:,1]
        f_SRS_data = [format(num, '.5f') for num in SRS_data]
        with open(file_path, 'w') as file:
            pass
        np.savetxt(file_path, f_SRS_data, fmt='%s',delimiter='\n')
#在文件开头和结尾加上要求的符号
        with open(file_path, 'r') as file:
            content = file.readlines()
        content.insert(0, '"*"\n')
        content.append('"."\n')
        content[-1] = content[-1].rstrip('\n')
        with open(file_path, 'w') as file:
            file.writelines(content)
#弹窗
        sg.popup(f"SRS文件： {srs_file_name}已生成!")  
        print('文件名为：',srs_file_name)
        print('存储位置为：',storage_location)
window.close()