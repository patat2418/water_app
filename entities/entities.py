from ast import operator
import random
import math
# from typing_extensions import Self
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import plotly.graph_objects as go
from sympy import symbols, solve
from utils import eq

class Pipe:
    
    def __init__ (self,pipetype="PE100-16",nominal_dia=0,inside_dia=0,length=1,cw=130,minor_headloss=0,major_headloss=0,static_head=0,total_headloss=0,flow_rate=0):
        
        self.pipetype = pipetype # List of pipe type: ["Steel","PE100-16","PE100-12.5","PE100-10"]
        self.inside_dia = inside_dia # Inside diameter
        self.nominal_dia = nominal_dia
        self.length = length # Pipe length
        self.cw = cw
        self.minor_headloss = minor_headloss
        self.major_headloss = major_headloss
        self.static_head = static_head
        self.total_headloss = total_headloss
        self.flow_rate = flow_rate
        self.pipe_table = pd.read_excel('pipes.xlsx',sheet_name=self.pipetype).fillna(value=0)
        # print(self.pipe_table.head())


    def inside_diameter(self,area):
        return (math.sqrt((4*area)/math.pi))
    
    def area (self):
        return eq.area(self.inside_dia)
    
    def area_from_velocity (self,velocity):
        return (self.flow_rate/3600)/(velocity)
        
    def velocity (self):
        return round((self.flow_rate/3600)/(self.area()),2)

    def flow_rate_calc(self,velocity=0):
        if velocity != 0:
            flow = velocity*self.area()*3600
        return flow

    def major_head_loss(self):

        headloss = eq.headloss(self.flow_rate,self.cw,self.inside_dia,self.length)
        return headloss

    def calc_minor_head_loss(self):
        pass

    def total_head_loss (self):
        velocity_energy = (float(self.velocity())**2)/(2*9.18)

        return float(self.static_head)+(velocity_energy+float(self.major_head_loss())+float(self.minor_headloss))

    def select_pipe_dia_from_velocity(self,des_vel):
        
        if des_vel == 0:
            return 

        dia1 = self.inside_diameter(self.area_from_velocity(des_vel))*1000
        # print (dia1)
        # print(self.pipetype)
        if self.pipetype == "Steel":
            # print(self.pipe_table.head())
            pd.to_numeric(self.pipe_table['Id'],errors='coerce',downcast='float')
            self.pipe_table['Id'][0]=0
            result_inside_diameter = self.pipe_table[self.pipe_table['Id']-dia1 > 0]['Id'].min()
            nominal_diameter = self.pipe_table[self.pipe_table['Id']==result_inside_diameter]['ND']
            # wall_thickness = self.pipe_table[self.pipe_table['Id']==result_inside_diameter]['wall thickness']
            min_wt = self.pipe_table[self.pipe_table['ND']==nominal_diameter.values[0]]['wall thickness'].min()
            inside_diameter = self.pipe_table[(self.pipe_table['wall thickness']==min_wt) & (self.pipe_table['ND']==nominal_diameter.values[0])]['Id'].values[0]
            return (nominal_diameter.values[0], inside_diameter,min_wt) # Return a tupple of (ND of the pipe in inche , id in mm, wall thickness in mm)

        else:
            pd.to_numeric(self.pipe_table['Id'],errors='coerce',downcast='float')
            result_inside_diameter = self.pipe_table[self.pipe_table['Id']-dia1 > 0]['Id'].min()
            nominal_diameter = self.pipe_table[self.pipe_table['Id']==result_inside_diameter]['ND']
            # wall_thickness = pipe_table[pipe_table['Id']==result_inside_diamter]['wall thickness']
            return (nominal_diameter.values[0], result_inside_diameter,0)
            
    def inside_dia_from_nominal (self, nd):
        self.pipe_table = pd.read_excel('pipes.xlsx',sheet_name=self.pipetype)
        if self.pipetype == "Steel":
            pd.to_numeric(self.pipe_table['Id'],errors='coerce',downcast='float')
            self.pipe_table['Id'][0]=0
            min_wt = self.pipe_table[self.pipe_table['ND']==nd]['wall thickness'].min()
            inside_diameter = self.pipe_table[(self.pipe_table['wall thickness']==min_wt) & (self.pipe_table['ND']==nd)]['Id'].values[0]
            return inside_diameter
        else:
            pd.to_numeric(self.pipe_table['Id'],errors='coerce',downcast='float')
            inside_diameter = self.pipe_table[self.pipe_table['ND']==nd]['Id']
            return inside_diameter.values[0]
    

    def wall_thickness (self,nd):
        wall_thickness_list = list(self.pipe_table[self.pipe_table['ND']==nd]['wall thickness'].values)
        # print(wall_thickness_list)
        return wall_thickness_list

    def pipe_diameter_table (self):
        self.pipe_table = pd.read_excel('pipes.xlsx',sheet_name=self.pipetype).fillna(value=0)
        if self.pipetype == 'Steel':
            a = list(self.pipe_table['ND'].drop_duplicates().values)
            b = [str(x) for x in a]
            return b
        else:
            # print(self.pipe_table[(self.pipe_table['Id']!= 0) or ()])
            a = list(self.pipe_table[self.pipe_table['Id']!= 0]['ND'].values)
            b = [str(x) for x in a]
            return b

class Channel:
    def __init__ (self, manning_coefficient = 0.035 ,channel_type='triangle', channel_depth=1, flow_rate = 0, channel_slope=0):
        self.manning_coefficient = manning_coefficient
        self.channel_type = channel_type # pipe,triangle,trapezoid,rectangular
        self.channel_depth = channel_depth
        self.flow_rate = flow_rate
        self.channel_slope = channel_slope
        if self.channel_type == 'triangle':
            self.bottom_width = 0            
        if (self.channel_type == 'rectangular') or (self.channel_type == 'pipe'):
            self.bank_slope = 0
        else:
            self.bank_slope = float(input('Please input channel bank slope: '))
        
        self.top_width = self.bottom_width + (channel_depth * self.bank_slope * 2)

        self.water_depth,self.cross_sectional_area,self.wetted_perimeter = eq.water_level_from_manning (self.flow_rate,self.bottom_width,self.bank_slope,self.channel_slope,self.manning_coefficient)

class Pump:
    
    def __init__ (self,operation_points=pd.DataFrame(),duty_point=(0,0),frequency_converters=False, frequency=50):
        self.operation_points =operation_points
        self.duty_point = duty_point
        self.frequency_converters=frequency_converters
        self.frequency=frequency

    def power(self, flow_rate,head,eff=1):
        return (((flow_rate/3.6)*head)/102)/eff

    def min_wet_pit(self,flow_rate,starts_num):
        cycle_time = 60/starts_num/60
        print(cycle_time)
        return (flow_rate*cycle_time/4)

    # def pump_chart(self):
    #     plt.plot(self.operation_points['Flow'],self.operation_points['Head'])
    #     plt.show()

    def tdh (self, pipe=Pipe(), max_flow=1000):

        
        # if not self.operation_points.empty:
        #     max_flow = int(float(op['Flow'].iloc[-1])*1.15)
        tdh_points = []
        for i in range(0,max_flow,max_flow//14):
            pipe1 = pipe
            pipe1.flow_rate = i
            # print(f'Flow: {i}\nheadloss: {pipe1.total_head_loss()}')
            tdh_points.append((i,pipe1.total_head_loss()))
        flow_rate_list, head_list =zip(*tdh_points)
        # plt.plot(flow_rate_list,head_list)
        # plt.show()   
        return flow_rate_list, head_list
    
    # def system_chart(self,pipe=Pipe(),max_flow=1000):
        
    #     flow_rate_list, head_list = self.tdh(pipe)
    #     x = symbols('x')

    #     op_eq = np.polyfit(self.operation_points['Flow'],self.operation_points['Head'],2)
    #     tdh_eq = np.polyfit(flow_rate_list,head_list,2)
    #     eq = (op_eq[0]-tdh_eq[0])*(x**2)+(op_eq[1]-tdh_eq[1])*x+(op_eq[2]-tdh_eq[2])
    #     operation_point_head = solve(eq)
    #     operation_point_flow = solve(tdh_eq[0])*(x**2)+tdh_eq[1]*x+tdh_eq[2]-operation_point_head
    #     # self.operation_points['Flow'].append(operation_point)
    #     # self.operation_points['Head'].append()
    #     fig = go.Figure()
    #     fig.layout.title = 'Pump and tdh graph'
    #     fig.add_trace(
    #         go.Scatter(
    #             x=self.operation_points['Flow'],
    #             y=self.operation_points['Head'],
    #             name='Pump corve',
    #             # trendline="ols"
    #         ))

    #     fig.add_trace(
    #         go.Scatter(
    #             x=flow_rate_list, 
    #             y=head_list,
    #             name='tdh',
    #             # trendline="ols"
    #         ))
        
    #             fig.add_trace(
    #         go.Scatter(
    #             x=flow_rate_list, 
    #             y=head_list,
    #             name='tdh',
    #         ))

    #     fig.show()



class Network:

    def __init__ (self, pipes=[Pipe()],pump=Pump(),total_flow=1000):
        self.pipes = pipes
        self.pump = pump
        self.total_flow = total_flow
    
def parallel_pipes(pipe1=Pipe(), pipe2=Pipe(), total_flow=1000):
    
    dif,threshold = (0.000001,0.000001)
    lower = 0
    upper = total_flow
    value = (lower + upper)/2

    while abs(dif) >= threshold:    
        pipe1.flow_rate = value
        pipe2.flow_rate = total_flow - value
        a = pipe1.major_head_loss()
        b = pipe2.major_head_loss()
        dif = b-a
        if dif < 0:
            upper = value
            value = (lower + upper)/2
        elif dif > 0:
            lower = value
            value = (lower + upper)/2
    pipe1.major_headloss = pipe1.major_head_loss()
    pipe2.major_headloss = pipe2.major_head_loss()
    return pipe1,pipe2


# pipe1 = Pipe(inside_dia=1,length=100,minor_headloss=0,static_head=50,flow_rate=430,cw=110)
# pipe2 = Pipe(inside_dia=0.253,length=35,minor_headloss=0,static_head=0,flow_rate=625,cw=110)

# points = {'Flow':[40,45,50,55,60,65,70,75,80,85,90,95,100,105],
#  'Head' : [110,110,109,108,107,106,104,101,99,95,92,90,79.4,77]}
# op = pd.DataFrame(points)
# pump1 = Pump(operation_points=op)
# pump2 = Pump()
# # print(pump2.operation_points)
# fig = plt.figure(figsize=(8,2))

# ax = fig.add_axes([0,0,1,1])
# ax.plot(pump1.tdh(pipe=pipe1))
# ax.plot( pump1.pump_chart())

# ax.set_title('Title')
# ax.set_xlabel('X Lable')
# ax.set_ylabel('Y Lable')

# ax.legend(loc=10)


# pump1.tdh(pipe=pipe1)
# pump1.pump_chart()
# pump1.system_chart(pipe=pipe1)

# pipe1,pipe2 = parallel_pipes(pipe1,pipe2,1500)
# print(pipe1.flow_rate, ' and ', pipe1.major_headloss)
# print(pipe2.flow_rate, ' and ', pipe2.major_headloss)

# print (pipe1.pipe_table['wall thickness'].unique())

# print(pipe1.major_head_loss())
# print(pipe2.major_head_loss())
# print(pipe1.total_head_loss())
# print(pipe2.total_head_loss())
# print(pipe1.pipetype)
# print(pipe1.area_from_velocity(2.5))
# print(pipe1.inside_diameter(pipe1.area_from_velocity(2.5)))
# # print(a.total_head_loss()+2.75)
# # print(a.major_head_loss(200))
# print(pipe1.area())
# # print(a.velocity(200))
# # # # print(a.flow_rate(2.78))
# b = Pump()
# flow_rates,headlist = b.tdh(pipe=a)
# # print(b.power(700,100))
# # print(b.min_wet_pit(700,10))
# pipe1.select_pipe_dia_from_velocity(2)

# nd, id ,wt= pipe1.select_pipe_dia_from_velocity(2)
# print (f"ND = {nd} mm with wall thickness of {wt}")
# print(f'ID = {id} mm')

# print(pipe1.inside_dia_from_nominal (315))

# print(a.wall_thickness(20)[0])
# wt_list =list[a.wall_thickness(20)]
# wt_list = [x.split()[1] for x in list[a.wall_thickness(20).value]]
# print (wt_list)

# tst = pd.DataFrame()
# # print(tst)
# # print(type(tst))
# print (pipe1.pipetype)
# print (pipe1.pipe_diameter_table())

# x = np.linspace(0,5,11)
# y = x ** 2
# plt.plot(x,y)
# plt.show()

channel1 = Channel(flow_rate=7200,channel_slope=0.05)
print(channel1.cross_sectional_area)