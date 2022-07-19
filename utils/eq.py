
import sys
# from ast import operator
# import random
import math
# from typing_extensions import Self
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sympy import symbols, solve

# Importing a file from a diffrent (backword) folder 
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1,'C:/Users/avner/google drive/Python/Avner water app1/main_project/consts')
import global_consts

def area(inside_dia:float|int):
    area: float = math.pi*(inside_dia**2)/4
    return(area)

def headloss(flow_rate:float,cw:int,inside_dia:float,length:float):
    c1 = 1.131*(10**9)
    c2 = 1.852
    c3 = -4.87
    return c1*((flow_rate/cw)**c2)*((inside_dia*1000)**c3)*length

def manning_eq (flow_rate:float,bottom_width:float,bank_slope:float,channel_slope:float,manning_coefficient:float):
    
    def water_depth_eq(cross_sectional_area,j,n,wetted_perimeter):
        return (((cross_sectional_area)**(5/3))*math.sqrt(j))/(n*(wetted_perimeter)**(2/3))

    def cross_sectional_area_eq(b,h,m):
        return b*h+m*h**2

    def wetted_perimeter_eq (b,h,m):
        return b+2*h*math.sqrt(m**2+1)

    q = flow_rate/3600
    b = bottom_width
    m = bank_slope
    j = channel_slope
    n = manning_coefficient
  
    threshold = 0.001
    upper = 100
    lower = 0
    h = (upper + lower)/2

    cross_sectional_area = cross_sectional_area_eq(b,h,m)
    wetted_perimeter = wetted_perimeter_eq (b,h,m)
    water_depth = water_depth_eq(cross_sectional_area,j,n,wetted_perimeter)

 
    while (abs(q-water_depth) > threshold) :
 
        dif = q-water_depth

        if dif < 0:
            upper = h
            h = (upper + lower)/2
        elif dif > 0:
            lower = h
            h = (upper + lower)/2

        cross_sectional_area = cross_sectional_area_eq(b,h,m)
        wetted_perimeter = wetted_perimeter_eq (b,h,m)
        water_depth = water_depth_eq(cross_sectional_area,j,n,wetted_perimeter)

    hydraulic_radius = cross_sectional_area/wetted_perimeter
    velocity:float = (1/manning_coefficient)*hydraulic_radius**(2/3)*math.sqrt(j)

    return h,cross_sectional_area, wetted_perimeter, hydraulic_radius, velocity

def pipe_max_partly_flow(inside_dia:float, manning_coefficient, slope, max_precent_of_filling=0.8):
    theta = math.acos(1-2*max_precent_of_filling) # 0.8 is max allowed percent of filling
    
    #region inside_dia calcs
    a_co = (theta-math.sin(2*theta)/2)*inside_dia**2/4
    pipe_flow_area = inside_dia**2/4*(theta-math.sin(2*theta)/2)
    wetted_perimeter = inside_dia*theta
    hydraulic_radius = inside_dia/4*(1-math.sin(2*theta)/(2*theta))
    top_width = inside_dia*math.sin(theta)

    tractive_force = hydraulic_radius*slope
    
    velocity = (slope**0.5/manning_coefficient)*(pipe_flow_area/wetted_perimeter)**(2/3)
    
    velocity_head = (velocity**2)/(2*global_consts.g)
    max_flow_rate = velocity*pipe_flow_area

    return max_flow_rate,velocity

# def pipe_partly_flow(inside_dia, manning_coefficient, slope):
    
    
#     threshold = 0.001
#     upper = inside_dia
#     lower = 0
#     h = (upper + lower)/2
 
#     while (abs(q-water_depth_eq) > threshold) :
 
#         dif = q-water_depth_eq

#         if dif < 0:
#             upper = h
#             h = (upper + lower)/2
#         elif dif > 0:
#             lower = h
#             h = (upper + lower)/2

#         precent_of_filling = h/inside_dia
#         theta = math.acos(1-2*precent_of_filling) # 0.8 is max allowed percent of filling
#         a_co = (theta-math.sin(2*theta)/2)*inside_dia**2/4
#         g = 9.806
#         flow_area = inside_dia**2/4*(theta-math.sin(2*theta)/2)
#         wetted_perimeter = inside_dia*theta
#         hydraulic_radius = inside_dia/4*(1-math.sin(2*theta)/(2*theta))
#         top_width = inside_dia*math.sin(theta)
#         tractive_force = hydraulic_radius*slope
#         velocity = (slope**0.5/manning_coefficient)*(flow_area/wetted_perimeter)**(2/3)
#         max_flow_rate = velocity*flow_area
#     return max_flow_rate,velocity

# pipe_max_partly_flow(inside_dia=0.4236, manning_coefficient=0.013, slope=0.05)

# h,cross_sectional_area_eq,wetted_perimeter_eq,hydraulic_radius,velocity = manning_eq (7200,1.5,0,0.05,0.035)
# print(wetted_perimeter_eq)
print(global_consts.g)