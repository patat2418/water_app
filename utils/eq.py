import sys
import math
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import plotly.graph_objects as go
import os

sys.path.insert(1,os.getcwd())
from consts import global_consts

#### Pipe eq: ####
def area(inside_dia:float) -> float:

    '''
    if the inside_dia value is bigger than 10 
    it assuming that the units are in mm.
    if it's less then that value the units are in m
    '''
    
    if inside_dia > 10 :
        inside_dia = inside_dia/1000
    area: float = math.pi*(inside_dia**2)/4
    return(area)

def headloss(flow_rate:float,cw:int,inside_dia:float,length:float) -> float:
    """return the major head loss or friction loss 

    Args:
        flow_rate (float): the flowrate in m^3/hr
        cw (int): roughness coefficient
        inside_dia (float): if the inside_dia value is bigger than 10 
                            it assuming that the units are in mm.
                            if it's less then that the units are in m
        length (float): the length of the pipe in m

    Returns:
        float: _description_
    """
    '''
    
    '''

    if inside_dia > 10 :
        inside_dia = inside_dia/1000

    c1 = 1.131*(10**9)
    c2 = 1.852
    c3 = -4.87
    headloss = c1*((flow_rate/cw)**c2)*((inside_dia*1000)**c3)*length
    return headloss

def velocity_energy (velocity:float) ->float:
    """return the velocity energy of the water from it's velocity

    Args:
        velocity (float): velocity in m/s

    Returns:
        velocity_energy(float): velocity energy in m
    """
    velocity_energy = (float(velocity)**2)/(2*global_consts.g)
    return velocity_energy

#### Channels eq ####

def manning_cross_sectional_area_eq(b:float,h:float,m:float) ->float:
    return b*h+m*h**2

def manning_wetted_perimeter_eq (b:float,h:float,m:float)->float:
    return b+2*h*math.sqrt(m**2+1)

def manning_eq_water_level_from_flow (flow_rate:float,bottom_width:float,bank_slope:float,channel_slope:float,manning_coefficient:float) -> float:
    
    def water_depth_eq(cross_sectional_area:float,j:float,n:float,wetted_perimeter:float) -> float:
        return (((cross_sectional_area)**(5/3))*math.sqrt(j))/(n*(wetted_perimeter)**(2/3))

    q = flow_rate/3600
    b = bottom_width
    m = bank_slope
    j = channel_slope
    n = manning_coefficient

    threshold = 0.001
    upper = 100
    lower = 0
    h = (upper + lower)/2

    cross_sectional_area = manning_cross_sectional_area_eq(b,h,m)
    wetted_perimeter = manning_wetted_perimeter_eq (b,h,m)
    water_depth = water_depth_eq(cross_sectional_area,j,n,wetted_perimeter)


    while (abs(q-water_depth) > threshold) :

        dif = q-water_depth

        if dif < 0:
            upper = h
            h = (upper + lower)/2
        elif dif > 0:
            lower = h
            h = (upper + lower)/2

        cross_sectional_area = manning_cross_sectional_area_eq(b,h,m)
        wetted_perimeter = manning_wetted_perimeter_eq (b,h,m)
        water_depth = water_depth_eq(cross_sectional_area,j,n,wetted_perimeter)

    hydraulic_radius = cross_sectional_area/wetted_perimeter
    velocity:float = (1/manning_coefficient)*hydraulic_radius**(2/3)*math.sqrt(j)

    return h,cross_sectional_area, wetted_perimeter, hydraulic_radius, velocity

def manning_eq_flow_from_water_level(water_depth,bottom_width:float,bank_slope:float,channel_slope:float,manning_coefficient:float):
    
    h = water_depth
    b = bottom_width
    m = bank_slope
    j = channel_slope
    n = manning_coefficient

    cross_sectional_area = manning_cross_sectional_area_eq(b=b,h=h,m=m)
    wetted_perimeter = manning_wetted_perimeter_eq (b,h,m)
    flow_from_depth = (cross_sectional_area**(5/3)*math.sqrt(j))/(n*(wetted_perimeter)**(2/3))
    velocity = flow_from_depth/cross_sectional_area

    return flow_from_depth, velocity, wetted_perimeter,cross_sectional_area

# max_flow_rate,max_velocity, max_wetted_perimeter, max_cross_sectional_area = manning_eq_flow_from_water_level(0.3,bottom_width=0,bank_slope=3, channel_slope=0.003772429209668295,manning_coefficient=0.035)
# print (max_flow_rate)

def pipe_max_partly_flow(inside_dia:float, manning_coefficient, slope, max_precent_of_filling=0.8):
    theta = math.acos(1-2*max_precent_of_filling) # 0.8 is max allowed percent of filling
    
    a_co = (theta-math.sin(2*theta)/2)*inside_dia**2/4
    pipe_flow_area = inside_dia**2/4*(theta-math.sin(2*theta)/2)
    wetted_perimeter = inside_dia*theta
    hydraulic_radius = inside_dia/4*(1-math.sin(2*theta)/(2*theta))
    top_width = inside_dia*math.sin(theta)
    velocity = (slope**0.5/manning_coefficient)*(pipe_flow_area/wetted_perimeter)**(2/3)
    max_flow_rate = velocity*pipe_flow_area 
    
    froude_number = velocity*(top_width/(global_consts.g*a_co*math.cos(math.atan(slope))))**0.5
    tractive_force = hydraulic_radius*slope
    velocity_head = (velocity**2)/(2*global_consts.g)
    
    return max_flow_rate*3600,velocity

# h,cross_sectional_area, wetted_perimeter, hydraulic_radius, velocity = manning_eq_water_level_from_flow (700,0,3,0.004,0.035)
# print(h,'\n',cross_sectional_area,'\n', wetted_perimeter,'\n', hydraulic_radius,'\n', velocity)




# def pipe_partly_flow2(inside_dia:float, manning_coefficient:float, slope:float, flow:float):
    
    # def real_manning_co(percent_of_full_depth, manning_coefficient_full):
         
    #     if percent_of_full_depth< 0.03:
    #         n_to_nfull = 1+percent_of_full_depth/0.3
    #     elif percent_of_full_depth< 0.1:
    #         n_to_nfull = 1.1+(percent_of_full_depth-0.03)*(12/7)
    #     elif percent_of_full_depth< 0.2:
    #         n_to_nfull = 1.22 + (percent_of_full_depth-0.1)*0.6
    #     elif percent_of_full_depth< 0.3:
    #         n_to_nfull = 1.29
    #     elif percent_of_full_depth< 0.5:
    #         n_to_nfull = 1.29 + (percent_of_full_depth-0.3)*0.2
    #     else:
    #         n_to_nfull = 1.25 - (percent_of_full_depth-0.5)*0.5
        
    #     real_manning_coefficient = n_to_nfull * manning_coefficient_full
        # return real_manning_coefficient, n_to_nfull


    # pipe_max_flow = pipe_max_partly_flow(inside_dia, manning_coefficient, slope)[0]
    # if pipe_max_flow < flow:
    #     print("This pipe isn't big enough to deliver this flow rate in those conditions!")
    #     return
    
    # threshold = 0.0001
    # upper = inside_dia
    # lower = 0
    # y = (upper + lower)/2 #water depth
    # percent_of_full_depth = y/inside_dia
    # pipe_flow = pipe_max_partly_flow(inside_dia, manning_coefficient, slope,max_precent_of_filling=percent_of_full_depth)[0]
    
    # while (abs(flow - pipe_flow) > threshold) :
    #     # print(flow,'\n',pipe_flow)
    #     dif = flow - pipe_flow
    #     print(type(dif),'=',dif)
    #     if dif < 0:
    #         upper = y
    #         y = (upper + lower)/2
    #     elif dif > 0:
    #         lower = y
    #         y = (upper + lower)/2

    #     percent_of_full_depth = y/inside_dia
    #     # new_manning_coefficient = real_manning_co(percent_of_full_depth, manning_coefficient)[0]
    #     pipe_flow = pipe_max_partly_flow(inside_dia, manning_coefficient, slope,max_precent_of_filling=percent_of_full_depth)[0]
    # print('water depth =',y,'\ny/D=',percent_of_full_depth)
    # return y
    
if __name__ == '__main__':
    print(pipe_max_partly_flow(inside_dia=0.250, manning_coefficient=0.013, slope=0.005, max_precent_of_filling=0.8))