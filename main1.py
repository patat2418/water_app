import sys
import os
# Importing necessary methods from pyautocad library to draw a polygon:
from pyautocad import Autocad, APoint, aDouble
# os.X_OK: Checks if path can be executed:
from os import X_OK
# Importing math library to compute coordinates for a polygon:
from math import *
import pandas as pd
import win32com.client

sys.path.insert(1,os.getcwd())
from utils import eq, init
from utils.autocad import autocad_functions,pipes_network_sytems,autocad_analyzing



eco_pipes_table = pd.DataFrame()
eco_pumps_table = pd.DataFrame()

acad = Autocad(create_if_not_exists=True)



# pipes_table = pd.read_excel('acad-pipelines.xlsx').fillna(value="")
pipes_table, pumps_table = autocad_analyzing.dwg_objects_sorting(acad=acad)
autocad_analyzing.is_pipe_conected(pipes_table,pumps_table)

pipes_network_sytems.simple_network(pipes_table,pumps_table)

eco_pipes_table = pipes_table.copy()
eco_pumps_table = pumps_table.copy()

pipes_network_sytems.pipes_from_flow_and_velocity (eco_pipes_table, eco_pumps_table, des_velocity=2.5)

autocad_analyzing.add_text_to_dwg(pipes_table,pumps_table,acad)

x_steps = 500
y_steps = 5
min_x,max_x,min_y,max_y = autocad_analyzing.make_a_sec_grid(pipes_table,x_steps,y_steps)
autocad_analyzing.draw_pipe_sec(pipes_table,min_y,max_y)


### write back to excel
with pd.ExcelWriter('data\\outputs\\acad-pipelines.xlsx') as writer:

    pipes_table.to_excel(writer,sheet_name='Pipes',index=False)
    
    pumps_table.to_excel(writer,sheet_name='Pumps',index=False)

    eco_pipes_table.to_excel(writer,sheet_name='eco Pipes',index=False)
    
    eco_pumps_table.to_excel(writer,sheet_name='eco Pumps',index=False)





# print(pipes_table.columns)

    #     data = [pipe_name,obj.Startpoint,obj.Endpoint,pipetype,nd,pipe.inside_dia,pipe.length,
    #                 pipe.static_head,pipe.flow_rate,velocity,pipe.major_headloss,pipe.total_headloss]
    #     pipes_table.loc[len(pipes_table)] = data

        # # print(pipe.inside_dia)
        # print(pipe.length)
        # print(pipe.static_head)
        # pipe.flow_rate = 1000
        # print(pipe.area())
        # print(pipe.velocity())
        # print(pipe.major_head_loss())
        # flow_rate_list, head_list, tdh_points = pipe.tdh()
        # print(tdh_points)
    # if obj.ObjectName == "AcDb2dPolyline":  
    #     obj.ObjectName = "pasp"
# print(acad.Xlist)
# print(pipes_table)