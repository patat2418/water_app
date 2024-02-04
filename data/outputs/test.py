# import win32com.client as win32
# excel = win32.gencache.EnsureDispatch('Excel.Application')
# wb = excel.Workbooks.Open('acad-pipelines.xlsx')
# # Alternately, specify the full path to the workbook
# # wb = excel.Workbooks.Open(r'C:\myfiles\excel\workbook2.xlsx')
# excel.Visible = True
import os
b= f'{os.getcwd()}\\data\\outputs\\acad-pipelines.xlsx'
a = r"C:\\Users\\avner\\google drive\\Python\\Apps\\Avner autocad network solver\\data\\outputs\\acad-pipelines.xlsx"
# os.system(a)
os.startfile(b)