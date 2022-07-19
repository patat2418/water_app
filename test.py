import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import plotly.graph_objects as go
import plotly.express as px
from sympy import symbols, solve

from utils.eq import area

print(area("fomo"))
# class Channel:
#     def __init__ (self, manning_coefficient = 0.035 ,channel_type='triangle', channel_depth=1, water_depth=0.8):
#         self.manning_coefficient = manning_coefficient
#         self.channel_type = channel_type # pipe,triangle,trapezoid,rectangular
#         self.channel_depth = channel_depth
#         self.water_depth = water_depth
#         if self.channel_type == 'triangle':
#             self.bottom_width = 0
#             self.bank_slope = int(input('Please input channel bank slope: '))
#             self.top_width = self.bottom_width + (channel_depth * self.bank_slope * 2)


# a = Channel()
# print(a.top_width)

# pipe_table = pd.read_excel('pipes.xlsx',sheet_name="PE100-12.5").fillna(value=0)

# print(pipe_table.head())
# dia1 = .625

# pd.to_numeric(pipe_table['Id'],errors='coerce',downcast='float')
# pipe_table['Id'] = pipe_table['Id']/1000
# result_inside_diamter = pipe_table[pipe_table['Id']-dia1 > 0]['Id'].min()
# nominal_diameter = pipe_table[pipe_table['Id']==result_inside_diamter]['ND']

# print (nominal_diameter)#,wall_thickness)
# print(result_inside_diamter)

# pd.to_numeric(pipe_table['Id'],errors='coerce',downcast='float')
# pipe_table['Id'][0]=0



# nd = 12
# # result_inside_diamter = pipe_table[pipe_table['Id']-dia1 > 0]['Id'].min()
# # nominal_diameter = pipe_table[pipe_table['Id']==result_inside_diamter]['ND']
# # wall_thickness = pipe_table[pipe_table['Id']==result_inside_diamter]['wall thickness']
# # # print (pipe_table)
# # print(nominal_diameter.values[0])
# # print(result_inside_diamter)
# # print(wall_thickness.values[0]) # Return a tupple of (ND of the pipe in inche , id in mm, wall thickness in mm)

# # new_inside_dia = pipe_table[pipe_table['ND']==nominal_diameter.values[0]]['wall thickness'].min()
# # new_inside_dia1 = pipe_table[(pipe_table['wall thickness']==new_inside_dia) & (pipe_table['ND']==nominal_diameter.values[0])]['Id'].values[0]
# # print(new_inside_dia1)

# new_inside_dia = pipe_table[pipe_table['ND']==nd]['wall thickness'].min()
# new_inside_dia1 = pipe_table[(pipe_table['wall thickness']==new_inside_dia) & (pipe_table['ND']==nd)]['Id'].values[0]
# # print(pipe_table.columns)
# print(new_inside_dia1)
# a = pipe_table['ND'].drop_duplicates()
# print(a)

# print(list(pipe_table[pipe_table['Id']!= 0]['ND'].values))

# pump1.tdh(pipe=pipe1)

# points = {'Flow':[40,45,50,55,60,65,70,75,80,85,90,95,100,105],
#  'Head' : [110,110,109,108,107,106,104,101,99,95,92,90,79.4,77]}
# op = pd.DataFrame(points)
# y = np.polyfit(op['Flow'],op['Head'],2)
# print( "{0}x^2 + {1}x +{2}".format(*y))
# print(y)
# z = 95

# new_head= y[0]*(z**2) + y[1]*z + y[2]
# print(new_head)


# pd.to_numeric(op['Flow'],errors='coerce',downcast='float')
# op = op.astype(float)
# # plt.plot(op['Flow'],op['Head'])
# # plt.show()  
# a = op['Flow'].iloc[-1]
# # print(op['Flow'][len(op['Flow'])-1])
# # print(type(op['Flow'].iloc[-1].value))
# print(a)
# print(type(a))
# a = float(a)
# print(type(a))
# max_flow = int(a*1.15)
# max_flow = int(float(op['Flow'].iloc[-1])*1.15)
# # print(max_flow)
# fig = px.Figure()

# fig.add_trace(
#     px.Scatter(
#         x=op['Flow'],
#         y=op['Head'],
#         name='Pump corve'
#     ))

# fig.add_trace(
#     px.Scatter(
#         x=[0, 1, 2, 3, 4, 5],
#         y=[1, 0.5, 0.7, -1.2, 0.3, 0.4]

#     ))

# fig.show()
# # help(go.FigureWidget)

# x = symbols('x')
# new_head= y[0]*(x**2) + y[1]*x + y[2]
# sol = solve(new_head)
# print(sol)
# tmp_dt = pd.DataFrame({'Flow':[sol[1]],'Head':[0]})
# op = op.append(tmp_dt)
# print(op)
# op.iplot


# h = symbols('h')

# a 