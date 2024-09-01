import sys
import os
from pyautocad import Autocad, APoint, aDouble
from math import *
import pandas as pd
import win32com.client
import re
sys.path.insert(1,os.getcwd())
from utils import eq
from utils import useful_functions as uf
from entities import entities
from utils.autocad import autocad_functions

print(entities.pipes_type_dict.keys())

# ##########################################################################################################################
# acad = Autocad(create_if_not_exists=True)

# def draw_a_pipe_from_app(pipetype:str, nd:int, consumption='0',min_pressure='0', start_elv="" ,end_elv=""):

#     def create_layer(pipetype:str, nd:str, consumption:str, min_pressure:str) -> str:
#         '''Pipe_type-(Steel)_nd-20_flow-200_MPressure-20'''
#         layer_name = f"Pipe_type-({pipetype})_nd-{str(nd)}_flow-{str(consumption)}_MPressure-{str(min_pressure)}"
#         acad.ActiveDocument.Layers.Add(layer_name)
#         return layer_name

#     layer_name = create_layer(pipetype, nd, consumption, min_pressure)
#     acad.prompt('Selcet Pipe start point:')
#     start = APoint(acad.doc.Utility.GetPoint())
#     acad.prompt('Selcet Pipe end point:')
#     end = APoint(acad.doc.Utility.GetPoint())
#     try:
#         start[2] = float(start_elv)
#         # print(1)
#     except:
#         pass
    
#     try:
#         end[2] = float(end_elv)
#         # print(2)
#     except:
#         pass

#     new_pipe = acad.model.AddLine(start,end)
#     new_pipe.Layer = layer_name

# def make_a_pipe_from_app(pipetype:str, nd:int, consumption='0', min_pressure='0') -> None:

#     def create_layer(pipetype:str, nd:str, consumption:str, min_pressure:str) -> str:
#         '''Pipe_type-(Steel)_nd-20_flow-200_MPressure-20'''
#         layer_name = f"Pipe_type-({pipetype})_nd-{str(nd)}_flow-{str(consumption)}_MPressure-{str(min_pressure)}"
#         acad.ActiveDocument.Layers.Add(layer_name)
#         return layer_name

#     for obj in acad.get_selection("please select new pipe:"):
#         # print(obj.Layer)
#         layer_name = create_layer(pipetype, nd, consumption, min_pressure)
#         obj.Layer = layer_name

# pipes_table = pd.DataFrame(columns=['pipe #', 'start', 'end', 'pipe type',
#         'nominal dia', 'id (mm)', 'length (m)', 'static head (endZ-startZ)', 
#         'flow', 'consumption', 'minimum pressure required', 'velocity', 'head loss', 'total head loss', 'Pressure at end of pipe', 
#         'start with', 'end with', 'costs per meter', 'total costs'])

# # draw_a_pipe_from_app(pipetype='Steel', nd='20', consumption='300',min_pressure='10', start_elv="" ,end_elv="")
# make_a_pipe_from_app(pipetype='PE100-12.5', nd='400', consumption='300',min_pressure='20')

# i = 0
# for obj in acad.iter_objects_fast():

#     if obj.ObjectName == "AcDbLine":
#         if obj.Layer.startswith('Pipe_'):
#             '''
#             Layer template:

#             Pipe_type-(Steel)_nd-20_flow-200_MPressure-20
#             type = Pipe type
#             nd = Nominal diameter
#             flow = consumptioin in junction
#             MPressure = minimum pressure at junction
#             '''  
#             i += 1
#             pipe_name = 'Pipe '+ str(i)
            
#             try:
#                 pipe_type = re.search(r'(?:[_])type-\(([^)]+)\)',obj.Layer).group(1)
#             except:
#                 raise TypeError("Pipe type is requierd!")
#             try:
#                 nominal_diameter = float(re.search(r'(?:[_])nd-(\d*\.*\d+)',obj.Layer).group(1))
#             except:
#                 raise TypeError("Nominal diameter is requierd!")
#             try:
#                 consumption = float(re.search(r'(?:[_])dn-(\d*\.*\d+)',obj.Layer).group(1))
#             except:
#                 consumption = 0
#             try:
#                 consumption = float(re.search(r'(?:[_])flow-(\d*\.*\d+)',obj.Layer).group(1))
#             except:
#                 consumption = 0
#             try:
#                 min_pressure = float(re.search(r'(?:[_])MPressure-(\d*\.*\d+)',obj.Layer).group(1))
#             except:
#                 min_pressure = 0

#             print(f'''##############################################
#                 pipe name = {pipe_name}
#                 pipe type = {pipe_type}
#                 nominal diameter = {nominal_diameter}
#                 consumption = {consumption}
#                 min_pressure = {min_pressure}
#             ''')
#             # input('press a key')
#             length=obj.Length
#             static_head=obj.Endpoint[2]-obj.Startpoint[2]
#             pipe = entities.Pipe(pipetype=pipe_type,nominal_dia=float(nominal_diameter),length=length,static_head=static_head)
#             pipe.inside_dia = pipe.inside_dia_from_nominal(nd=pipe.nominal_dia)

#             pipes_type_table = entities.pipes_type_dict[pipe_type]
#             costs_per_meter = pipes_type_table[pipes_type_table['ND'] == int(nominal_diameter)]['prices'].values[0]
#             total_costs = costs_per_meter*length

#             data = [pipe_name,obj.Startpoint,obj.Endpoint,pipe_type,nominal_diameter,pipe.inside_dia,pipe.length,
#                         pipe.static_head,"",float(consumption),min_pressure,"",
#                         "","","","","",costs_per_meter,total_costs]
#             pipes_table.loc[len(pipes_table)] = data
#             pipes_table.set_index(pipes_table['pipe #'],inplace=True)

# with pd.ExcelWriter('data\\outputs\\acad-pipelines-tests.xlsx') as writer:

#     pipes_table.to_excel(writer,sheet_name='Pipes',index=False)
# os.startfile('data\\outputs\\acad-pipelines-tests.xlsx')

################################################################################################################################


# k = 1
# for obj in acad.iter_objects_fast():
    
#     if (obj.Layer.startswith('Consumer_')):
#         '''
#         Layer template:
#         flow = consumptioin in junction
#         pressure = minimum pressure at junction
#         '''
#         consumer_name = 'Consumer' + str(k)
#         k += 1
#         try:
#             consumption = float(re.search(r'(?:[_])flow-(\d+)',obj.Layer).group(1))
#         except:
#             consumption = 0
#         try:
#             min_pressure = float(re.search(r'(?:[_])pressure-(\d+)',obj.Layer).group(1))
#         except:
#             min_pressure = 0

#         counsumer = entities.CounsumerJunction(flow=flow, min_pressure=min_pressure)
        
        



# import imp
# import pandas as pd
# import os
# from utils import dfgui
# # import numpy as np
# # import matplotlib.pyplot as plt
# # # import plotly.graph_objects as go
# # import plotly.express as px
# # from sympy import symbols, solve

# # # a = pd.read_excel(f'{os.getcwd()}\\data\\info\\pipes.xlsx',sheet_name="Steel").fillna(value=0)
# # a = pd.read_excel('data\\info\\pipes.xlsx',sheet_name="Steel").fillna(value=0)
# # print(type(a))
# # dfgui.show(a)

# import win32com.client as win32
# excel = win32.gencache.EnsureDispatch('Excel.Application')
# wb = excel.Workbooks.Open('data\\outputs\\acad-pipelines.xlsx')
# # Alternately, specify the full path to the workbook
# # wb = excel.Workbooks.Open(r'C:\myfiles\excel\workbook2.xlsx')
# excel.Visible = True




# # from utils.eq import area






# # print(area("fomo"))
# # class Channel:
# #     def __init__ (self, manning_coefficient = 0.035 ,channel_type='triangle', channel_depth=1, water_depth=0.8):
# #         self.manning_coefficient = manning_coefficient
# #         self.channel_type = channel_type # pipe,triangle,trapezoid,rectangular
# #         self.channel_depth = channel_depth
# #         self.water_depth = water_depth
# #         if self.channel_type == 'triangle':
# #             self.bottom_width = 0
# #             self.bank_slope = int(input('Please input channel bank slope: '))
# #             self.top_width = self.bottom_width + (channel_depth * self.bank_slope * 2)


# # a = Channel()
# # print(a.top_width)

# # pipe_table = pd.read_excel('pipes.xlsx',sheet_name="PE100-12.5").fillna(value=0)

# # print(pipe_table.head())
# # dia1 = .625

# # pd.to_numeric(pipe_table['Id'],errors='coerce',downcast='float')
# # pipe_table['Id'] = pipe_table['Id']/1000
# # result_inside_diamter = pipe_table[pipe_table['Id']-dia1 > 0]['Id'].min()
# # nominal_diameter = pipe_table[pipe_table['Id']==result_inside_diamter]['ND']

# # print (nominal_diameter)#,wall_thickness)
# # print(result_inside_diamter)

# # pd.to_numeric(pipe_table['Id'],errors='coerce',downcast='float')
# # pipe_table['Id'][0]=0



# # nd = 12
# # # result_inside_diamter = pipe_table[pipe_table['Id']-dia1 > 0]['Id'].min()
# # # nominal_diameter = pipe_table[pipe_table['Id']==result_inside_diamter]['ND']
# # # wall_thickness = pipe_table[pipe_table['Id']==result_inside_diamter]['wall thickness']
# # # # print (pipe_table)
# # # print(nominal_diameter.values[0])
# # # print(result_inside_diamter)
# # # print(wall_thickness.values[0]) # Return a tupple of (ND of the pipe in inche , id in mm, wall thickness in mm)

# # # new_inside_dia = pipe_table[pipe_table['ND']==nominal_diameter.values[0]]['wall thickness'].min()
# # # new_inside_dia1 = pipe_table[(pipe_table['wall thickness']==new_inside_dia) & (pipe_table['ND']==nominal_diameter.values[0])]['Id'].values[0]
# # # print(new_inside_dia1)

# # new_inside_dia = pipe_table[pipe_table['ND']==nd]['wall thickness'].min()
# # new_inside_dia1 = pipe_table[(pipe_table['wall thickness']==new_inside_dia) & (pipe_table['ND']==nd)]['Id'].values[0]
# # # print(pipe_table.columns)
# # print(new_inside_dia1)
# # a = pipe_table['ND'].drop_duplicates()
# # print(a)

# # print(list(pipe_table[pipe_table['Id']!= 0]['ND'].values))

# # pump1.tdh(pipe=pipe1)

# # points = {'Flow':[40,45,50,55,60,65,70,75,80,85,90,95,100,105],
# #  'Head' : [110,110,109,108,107,106,104,101,99,95,92,90,79.4,77]}
# # op = pd.DataFrame(points)
# # y = np.polyfit(op['Flow'],op['Head'],2)
# # print( "{0}x^2 + {1}x +{2}".format(*y))
# # print(y)
# # z = 95

# # new_head= y[0]*(z**2) + y[1]*z + y[2]
# # print(new_head)


# # pd.to_numeric(op['Flow'],errors='coerce',downcast='float')
# # op = op.astype(float)
# # # plt.plot(op['Flow'],op['Head'])
# # # plt.show()  
# # a = op['Flow'].iloc[-1]
# # # print(op['Flow'][len(op['Flow'])-1])
# # # print(type(op['Flow'].iloc[-1].value))
# # print(a)
# # print(type(a))
# # a = float(a)
# # print(type(a))
# # max_flow = int(a*1.15)
# # max_flow = int(float(op['Flow'].iloc[-1])*1.15)
# # # print(max_flow)
# # fig = px.Figure()

# # fig.add_trace(
# #     px.Scatter(
# #         x=op['Flow'],
# #         y=op['Head'],
# #         name='Pump corve'
# #     ))

# # fig.add_trace(
# #     px.Scatter(
# #         x=[0, 1, 2, 3, 4, 5],
# #         y=[1, 0.5, 0.7, -1.2, 0.3, 0.4]

# #     ))

# # fig.show()
# # # help(go.FigureWidget)

# # x = symbols('x')
# # new_head= y[0]*(x**2) + y[1]*x + y[2]
# # sol = solve(new_head)
# # print(sol)
# # tmp_dt = pd.DataFrame({'Flow':[sol[1]],'Head':[0]})
# # op = op.append(tmp_dt)
# # print(op)
# # op.iplot


# # h = symbols('h')

# # a 