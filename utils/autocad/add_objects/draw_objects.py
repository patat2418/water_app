import pandas as pd
from pyautocad import Autocad, APoint, aDouble
from utils.useful_functions import midpoint_betwen_to_points
from config.config import Config
import os, sys
sys.path.insert(1,os.getcwd())
from utils.autocad.autocad_analyzing import acad, layers_dict

def set_channel_data(channel: pd.Series, scale = 100 ):
    bottom_width = channel['geometry: bottom width']*scale
    bank_slope = channel['geometry: bank slope']
    water_depth = channel['water depth']*scale
    flow_rate = channel['flow']
    free_board =  channel['geometry: free board']*scale
    channel_depth = channel['geometry: channel depth']*scale
    max_water_depth = channel['max water depth']*scale
    max_flow_rate = channel['max flow rates']

    try:
        channel_depth = float(channel_depth)
        max_flow = ''
        bad_geometry_text = ''
    except:
        try:
                if max_water_depth:
                    channel_depth = float (max_water_depth)+float(free_board)
                    max_flow = f"the maximum allowed water level is: {round(max_water_depth,2)} cm @ Max flow rate of {round(max_flow_rate,2)}"
                    if (max_water_depth < water_depth):
                        bad_geometry_text ='Channel Geometry is not good for the designed water flow'
                else:
                    channel_depth = float(channel_depth)
                    max_flow = ''
                    bad_geometry_text = ''
        except:
                channel_depth = float (water_depth)+free_board
                max_flow = ''
                bad_geometry_text = ''
    
    side_steps = (channel_depth/scale)*float(bank_slope)*scale 
    water_side_steps = (water_depth/scale)*float(bank_slope)*scale
    max_water_side_steps = ((max_water_depth/scale)*float(bank_slope))*scale
    des_flow = f"the water level will be: {round(water_depth,2)} cm @ design flow rate {round(flow_rate,2)}"

    channel_data = {
        "bottom_width" : bottom_width,
        "bank_slope" : bank_slope,
        "water_depth" : water_depth,
        "flow_rate" : flow_rate,
        "free_board" : free_board,
        "channel_depth" : channel_depth,
        "max_water_depth" : max_water_depth,
        "max_flow_rate" : max_flow_rate,
        "channel_depth" : channel_depth,
        "side_steps" : side_steps,
        "water_side_steps" : water_side_steps,
        "max_water_side_steps" : max_water_side_steps,
        "max_flow" : max_flow,
        "bad_geometry_text" : bad_geometry_text,
        "des_flow": des_flow,
        }
    return channel_data

def draw_channel_geometry(channel: pd.Series, channel_data: dict, y_padding = 100, x_padding = 100):
    ps = APoint(channel['start'])
    pe = APoint(channel['end'])
    p3 = APoint(midpoint_betwen_to_points(pe,ps))

    p3.y += y_padding #Set (0,0) of section
    p3.z = 0

    p2 = APoint((p3.x - channel_data['side_steps']),(p3.y + channel_data['channel_depth']))
    p1 = APoint((p2.x-x_padding), p2.y)
    
    if channel_data['bottom_width'] != 0:
        p4 = APoint((p3.x + channel_data['bottom_width']),p3.y)
        p5 = APoint((p4.x + channel_data['side_steps']),(p4.y + channel_data['channel_depth']))
        p6 = APoint((p5.x+x_padding),p5.y)
        p7 = APoint((p4.x + channel_data['water_side_steps']), (p4.y + channel_data['water_depth']))
        p8 = APoint((p4.x + channel_data['max_water_side_steps']), (p4.y + channel_data['max_water_depth']))
    else:
        p4 = APoint((p3.x + channel_data['side_steps']),(p3.y + channel_data['channel_depth']))
        p5 = APoint((p4.x+x_padding),p4.y)
        p6 = p5
        p7 = APoint((p3.x + channel_data['water_side_steps']), (p3.y + channel_data['water_depth']))
        p8 = APoint((p3.x + channel_data['max_water_side_steps']), (p3.y + channel_data['max_water_depth']))
    p9 = APoint((p3.x - channel_data['water_side_steps']),(p3.y + channel_data['water_depth']))
    if channel_data['max_water_depth']:
        p10 = APoint((p3.x - channel_data['max_water_side_steps']),(p3.y + channel_data['max_water_depth']))
    else:
         p10=APoint(0,0)
    
    ##### draw channel geometry ####
    acad.model.AddLine(p1,p2)
    acad.model.AddLine(p2,p3)
    acad.model.AddLine(p3,p4)
    acad.model.AddLine(p4,p5)
    acad.model.AddLine(p5,p6)

    return (p7,p8,p9,p10)

def draw_channel_water(channel: pd.Series, channel_data: dict, water_points: APoint ):
    p7,p8,p9,p10 = water_points
    water_line = acad.model.AddLine(p7,p9)
    water_text_point = APoint(midpoint_betwen_to_points(p7,p9))
    water_text_point.x -= Config.MARGIN
    text = acad.model.Addtext(channel_data['des_flow'],water_text_point,Config.TEXT_SIZE)

    if channel_data['max_water_depth']:
        max_water_line = acad.model.AddLine(p8,p10)
        max_water_text_point = APoint(midpoint_betwen_to_points(p8,p10))
        max_water_text_point.y -= Config.PADDING
        max_water_text_point.x -= Config.MARGIN
        text = acad.model.Addtext(channel_data['max_flow'],max_water_text_point,Config.TEXT_SIZE)

        if (channel_data['max_water_depth'] < channel_data['water_depth']):
            max_water_text_point.y -= Config.PADDING*5
            max_water_text_point.x -= Config.MARGIN
            text1 = acad.model.Addtext(channel_data['bad_geometry_text'],max_water_text_point,Config.TEXT_SIZE*2)
            text1.color = 1

def add_channel_section(channel: pd.Series):

    channel_data = set_channel_data(channel)
    acad.ActiveDocument.ActiveLayer = layers_dict['channel_layer']
    water_points = draw_channel_geometry(channel, channel_data)
    acad.ActiveDocument.ActiveLayer = layers_dict['channel_water_layer']
    draw_channel_water(channel,channel_data,water_points)
