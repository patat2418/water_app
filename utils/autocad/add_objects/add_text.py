
import pandas as pd
from pyautocad import Autocad, APoint, aDouble

import os, sys
sys.path.insert(1,os.getcwd())
from utils.autocad.autocad_analyzing import acad, layers_dict
from utils.autocad.add_objects.draw_objects import add_channel_section
from utils.autocad import autocad_analyzing 
from utils.useful_functions  import midpoint_betwen_to_points
from utils.autocad.pipes_network_sytems import branched_network
from utils.utils import calculate_max_distance, calculate_text_size, update_text_config
from config import config
# from utils.autocad.analyzing.sort_objects import sort_objects

### globals ###

def add_text_to_dwg(pipes_table: pd.DataFrame,pumps_table: pd.DataFrame, channels_table: pd.DataFrame):
    max_distance = calculate_max_distance(pipes_table)
    # text_height, padding, margin = calculate_text_size(max_distance)
    update_text_config(max_distance)

    add_channels_text(channels_table)
    add_pipes_text(pipes_table)
    add_pumps_text(pumps_table)

def add_text_to_cad(text_group:dict, p:APoint):
    for text in text_group.values():
        text = acad.model.Addtext(text,p, config.TEXT_SIZE)
        p.y -= config.TEXT_SIZE + config.PADDING 
### Channels ###
def add_channel_info_text(channel: pd.Series):
    
    channel_infos = {

        'name' : str(channel['channel #']),
        'length' : f"length: {round(channel['length (m)'],2)} m",
        'slope' : f"slope: {round(float(channel['slope']*100),2)} %",
        'des_flow' : f"the water level will be: {round(float(channel['water depth']*100),2)} cm @ design flow rate {round(float(channel['flow']),2)}",
    }

    p = APoint(midpoint_betwen_to_points(channel['start'], channel['end']))
    p.y -= config.MARGIN

    add_text_to_cad(channel_infos,p)

    if channel['max water depth']:
        max_flow = f"the max allowed water level is: {round(float(channel['max water depth']*100),2)} cm @ flow rate {round(float(channel['max flow rates']),2)}"
        text = acad.model.Addtext(max_flow,p,config.TEXT_SIZE)

def add_channel_vertex_text(channel: pd.Series, i: int, channel_name: str, last_one_flag: bool ):
    
    p = APoint(channel['start'])
    channel_vertexs_texts = {
        "name" : f'Vertex number: {i}',
        "z" : f'Z={p.z}',
    }

    add_text_to_cad(channel_vertexs_texts,p)
    if last_one_flag:
        
        i += 1
        channel_vertexs_texts["name"] = f'Vertex number: {i}'
        p = APoint(channel['end'])
        add_text_to_cad(channel_vertexs_texts,p)

def add_channels_text(channels_table: pd.DataFrame):
    
    last_one_flag = False
    i = 1

    for channel_name,channel in channels_table.iterrows():
        
        if i == (len(channels_table)):
            last_one_flag = True 

        acad.ActiveDocument.ActiveLayer = layers_dict['channel_text_layer']
        add_channel_vertex_text(channel, i,channel_name, last_one_flag)
        add_channel_info_text(channel) 
        add_channel_section(channel)
        i += 1

### Pipes ###

def add_pipes_text(pipes_table: pd.DataFrame, text_height=2.5):
    
    last_one_flag = False
    i = 1

    for pipe_name,pipe in pipes_table.iterrows():
        
        if i == (len(pipes_table)):
            last_one_flag = True 

        acad.ActiveDocument.ActiveLayer = layers_dict['pipe_text_layer']
        add_pipe_vertex_text(pipes_table, i, last_one_flag, text_height=text_height)
        add_pipe_info_text(pipe, text_height=text_height)         
        i += 1

def add_pipe_vertex_text(pipes_table: pd.DataFrame, i: int, last_one_flag: bool, text_height = 2.5, padding = 4):

    def update_pipe_vertex_texts(i:int, p:APoint, pressure:float, consumption:float, min_pressure:float) -> dict:
        return {
            "name" : f'Vertex number: {i}',
            "z" : f'Z={p.z}',
            "p" : f'P={round(pressure,2)}',
            "h" : f'H={round(p.z + pressure,2)}',
            "consumption" : f'Consumption = {consumption}',
            "minimum_pressure" : f'Minimum pressure at vertex = {min_pressure}',
            }

    pump_name = 'Pump 1'

    if i == 1:
        prev_pipe = pipes_table[pipes_table['start with'] == pump_name]['start with'].values[0]
        current_pipe = pipes_table[pipes_table['start with'] == pump_name]['pipe #'].values[0]
        pressure = pipes_table.loc[current_pipe,'total head loss'] + pipes_table.loc[current_pipe,"Pressure at end of pipe"]
        min_pressure = 0
        consumption = 0
    
    else:
        current_pipe = pipes_table['pipe #'][i-1]
        prev_pipe = pipes_table.loc[current_pipe,"start with"]
        pressure = pipes_table.loc[prev_pipe,"Pressure at end of pipe"]
        min_pressure = pipes_table.loc[prev_pipe,"minimum pressure required"]
        consumption = pipes_table.loc[prev_pipe,"consumption"]
        
    p = APoint(pipes_table.loc[current_pipe,'start'])
    pipe_vertexs_texts = update_pipe_vertex_texts(i, p, pressure, consumption, min_pressure)

    add_text_to_cad(pipe_vertexs_texts,p)

    # if last_one_flag:
    if pipes_table.loc[current_pipe,'end with'] == "":
        p = APoint(pipes_table.loc[current_pipe,'end'])
        pressure = pipes_table.loc[current_pipe,"Pressure at end of pipe"]
        min_pressure = pipes_table.loc[current_pipe,"minimum pressure required"]
        consumption = pipes_table.loc[current_pipe,"consumption"]
        i += 1
        pipe_vertexs_texts = update_pipe_vertex_texts(i, p, pressure, consumption, min_pressure)
        add_text_to_cad(pipe_vertexs_texts,p)


def add_pipe_info_text(pipe: pd.Series, margin = 80, padding = 4, text_height = 2.5) :
    
    if pipe['pipe type'] == 'Steel':
        units = '"'
    else:
        units = 'mm'

    pipe_info_text = {

        'name' : str(pipe['pipe #']),
        'pipe type' : f"{pipe['pipe type']} %%C {pipe['nominal dia']} {units}",
        'length' : f"length: {round(pipe['length (m)'],2)} m",
        'flow' : f"flow: {pipe['flow']} m^3/hr",
        'head_loss' : f"Total head loss: {round(pipe['total head loss'],2)} m"
    }

    p = APoint(midpoint_betwen_to_points(pipe['start'], pipe['end']))
    p.y += margin

    add_text_to_cad(pipe_info_text,p)


### Pumps ###
    
def add_pumps_text(pumps_table: pd.DataFrame):
    
    last_one_flag = False
    i = 1

    for pump_name,pump in pumps_table.iterrows():
        
        if i == (len(pumps_table)):
            last_one_flag = True 

        acad.ActiveDocument.ActiveLayer = layers_dict['pump_text_layer']
        add_pump_info_text(pump, pump_name)         
        i += 1

def add_pump_info_text(pump: pd.Series,pump_name:str) :
    
    pump_info_text = {

        'name' : pump_name,
        'flow' : f"flow: {pump['flow']} m^3/hr",
        'head' : f"head: {round(pump['head'],2)} m"
    }

    p = APoint(pump['center'])
    p.y += config.MARGIN

    add_text_to_cad(pump_info_text,p)

if __name__ == "__main__":
    import re
    from entities import entities
    from utils import eq
    def create_layers_dict() -> dict:
        grid_layer = acad.ActiveDocument.Layers.Add("grid")
        grid_text_layer = acad.ActiveDocument.Layers.Add("grid_text")
        pipe_layer = acad.ActiveDocument.Layers.Add("pipe")
        pipe_guideline_layer = acad.ActiveDocument.Layers.Add("pipe_guideline")
        pipe_text_layer = acad.ActiveDocument.Layers.Add("pipe_text")
        energy_line_layer = acad.ActiveDocument.Layers.Add("energy_line")
        pump_text_layer = acad.ActiveDocument.Layers.Add("pump_text")
        channel_text_layer = acad.ActiveDocument.Layers.Add("channel_text")
        channel_layer = acad.ActiveDocument.Layers.Add("channel")
        channel_water_layer = acad.ActiveDocument.Layers.Add("channel water")
        channel_max_water_layer = acad.ActiveDocument.Layers.Add("channel max water")

        grid_layer.color = 7
        grid_text_layer.color = 7
        pipe_layer.color = 5
        pipe_guideline_layer.color = 8
        pipe_text_layer.color = 7
        energy_line_layer.color = 6
        pump_text_layer.color = 7
        pump_text_layer.color = 7
        channel_text_layer.color = 7
        channel_layer.color = 38
        channel_water_layer.color = 5
        channel_max_water_layer.color = 4
        
        layers_dict = {
        "grid_layer" : grid_layer,
        "grid_text_layer" : grid_text_layer,
        "pipe_layer" : pipe_layer,
        "pipe_guideline_layer" : pipe_guideline_layer,
        "pipe_text_layer" : pipe_text_layer,
        "energy_line_layer" : energy_line_layer,
        "pump_text_layer" : pump_text_layer,
        "channel_text_layer" : channel_text_layer,
        "channel_layer" : channel_layer,
        "channel_water_layer" : channel_water_layer,
        "channel_max_water_layer" : channel_max_water_layer,
        }
        return layers_dict
    acad = Autocad(create_if_not_exists=True)
    # pipes_table, pumps_table, channels_table = autocad_analyzing.dwg_objects_sorting()
    # autocad_analyzing.is_pipe_conected(pipes_table,pumps_table)
    # branched_network(pipes_table,pumps_table)
    # layers_dict = create_layers_dict(acad)
    # # add_channels_text(acad, channels_table, layers_dict)
    # add_pipes_text(acad,pipes_table,layers_dict)
    # with pd.ExcelWriter('data\\outputs\\acad-pipelines.xlsx') as writer:

    #     pipes_table.to_excel(writer,sheet_name='Pipes',index=False)
        
    #     pumps_table.to_excel(writer,sheet_name='Pumps',index=False)

    #     # eco_pipes_table.to_excel(writer,sheet_name='eco Pipes',index=False)
        
    #     # eco_pumps_table.to_excel(writer,sheet_name='eco Pumps',index=False)

    #     channels_table.to_excel(writer,sheet_name='Channels',index=False)

    # os.startfile('data\\outputs\\acad-pipelines.xlsx')

    # channels_table = pd.DataFrame()
    channels_table = pd.DataFrame(columns=['channel #', 'start', 'end', 'length (m)', 'static head (endZ-startZ)', 'slope',
                                        'manning coeficent','flow' ,'velocity', 'water depth', 'max flow rates', 'max water depth',
                                        'geometry: bottom width','geometry: bank slope', 'geometry: channel depth', 'geometry: channel width', 
                                        'geometry: free board', 'start with', 'end with'])
    
    # sort_objects(acad, channels_table)
    print(channels_table)
    with pd.ExcelWriter('data\\outputs\\test.xlsx') as writer:

        # pipes_table.to_excel(writer,sheet_name='Pipes',index=False)
        
        # pumps_table.to_excel(writer,sheet_name='Pumps',index=False)

        # eco_pipes_table.to_excel(writer,sheet_name='eco Pipes',index=False)
        
        # eco_pumps_table.to_excel(writer,sheet_name='eco Pumps',index=False)

        channels_table.to_excel(writer,sheet_name='Channels',index=False)

    os.startfile('data\\outputs\\test.xlsx')

    # k = 0 
    # # channels = {}
    # for obj in acad.iter_objects_fast():

    #     if obj.ObjectName == "AcDbLine":

    #         ##### Channels data: #####
                
    #         if obj.Layer.startswith('Channel_'):
    #             '''
    #             Layer template:
    #             m = bank slope
    #             b = bottom width
    #             n = manning coefficient
    #             q = flow rate
    #             mwd = Max Water Depth allowed
    #             cd = desgined Channel Depth
    #             fb = Free board

    #             '''
                
                
    #             channel_name = 'Channel '+ str(k+1)
    #             k += 1

    #             # Define simplified patterns and corresponding variables in a dictionary
    #             patterns = {
    #                 'bank_slope': {'pattern': r'm-', 'default': 0},
    #                 'bottom_width': {'pattern': r'b-', 'default': 0},
    #                 'max_water_depth': {'pattern': r'mwd-', 'default': False},
    #                 'flow_rate': {'pattern': r'q-', 'default': 0},
    #                 'manning_coefficient': {'pattern': r'n-', 'default': 0.035},
    #                 'channel_depth': {'pattern': r'cd-', 'default': ""},
    #                 'free_board': {'pattern': r'fb-', 'default': 0.25}
    #             }

    #             # Function to extract values from obj.Layer using the provided pattern and default value
    #             def extract_value(pattern:dict, default:float|bool, obj):
                    
    #                 search_pattern = rf'(?:[_]){pattern}(\d*\.*\d+)'
    #                 try:
    #                     return float(re.search(search_pattern, obj.Layer).group(1))
    #                 except:
    #                     return default  # Return None if extraction fails

    #             # Loop through patterns and extract values
    #             extracted_values = {}
    #             for key, value in patterns.items():
    #                 extracted_value = extract_value(value['pattern'], value['default'], obj)
    #                 extracted_values[key] = extracted_value
                
    #             bank_slope = extracted_values['bank_slope']
    #             bottom_width = extracted_values['bottom_width']
    #             max_water_depth = extracted_values['max_water_depth']
    #             flow_rate = extracted_values['flow_rate']
    #             manning_coefficient = extracted_values['manning_coefficient']
    #             channel_depth = extracted_values['channel_depth']
    #             free_board = extracted_values['free_board']
    #             length=float(obj.Length)
    #             static_head=float(obj.Startpoint[2]-obj.Endpoint[2])
    #             channel_slope = static_head/length

    #             channel = entities.Channel(manning_coefficient=manning_coefficient,flow_rate=flow_rate,bank_slope=bank_slope,bottom_width=bottom_width,max_water_depth=max_water_depth,channel_slope=channel_slope)
                
    #             if channel_depth != "":
    #                 max_water_depth = channel_depth - free_board

    #             if max_water_depth:
    #                 max_flow_rate,max_velocity, max_wetted_perimeter, max_cross_sectional_area = eq.manning_eq_flow_from_water_level(max_water_depth,bottom_width,bank_slope,channel_slope,manning_coefficient)
    #                 print(f'the max flow rate is: {max_flow_rate*3600} m^3/hr, but the desgin is for {flow_rate} m^3/hr')
    #                 # if (max_water_high < channel.water_depth):
    #                     # print('Channel Geometry not good for that water flow')  
    #             else:
    #                 max_flow_rate=''
    #                 max_velocity=''
    #                 max_wetted_perimeter=''
    #                 max_cross_sectional_area=''

    #             data = [channel_name,obj.Startpoint,obj.Endpoint,length, static_head,channel.channel_slope ,
    #                                         manning_coefficient ,channel.flow_rate,channel.velocity,channel.water_depth,
    #                                         max_flow_rate*3600,max_water_depth,bottom_width,channel.bank_slope,
    #                                         channel_depth, '',free_board, '','']
    #             channels_table.loc[len(channels_table)] = data

    #         #     extracted_values['length'] = float(obj.Length)
    #         #     extracted_values['static_head'] = float(obj.Startpoint[2]-obj.Endpoint[2])
    #         #     static_head=float(obj.Startpoint[2]-obj.Endpoint[2])
    #         #     channel_slope = static_head/length

    #         #     channel = entities.Channel(manning_coefficient=manning_coefficient,flow_rate=flow_rate,bank_slope=bank_slope,bottom_width=bottom_width,max_water_depth=max_water_depth,channel_slope=channel_slope)
                
    #         #     if channel_depth != "":
    #         #         max_water_depth = channel_depth - free_board

    #         #     if max_water_depth:
    #         #         max_flow_rate,max_velocity, max_wetted_perimeter, max_cross_sectional_area = eq.manning_eq_flow_from_water_level(max_water_depth,bottom_width,bank_slope,channel_slope,manning_coefficient)
    #         #         print(f'the max flow rate is: {max_flow_rate*3600} m^3/hr, but the desgin is for {flow_rate} m^3/hr')
    #         #         # if (max_water_high < channel.water_depth):
    #         #             # print('Channel Geometry not good for that water flow')  
    #         #     else:
    #         #         max_flow_rate=''
    #         #         max_velocity=''
    #         #         max_wetted_perimeter=''
    #         #         max_cross_sectional_area=''

    #         #     data = [channel_name,obj.Startpoint,obj.Endpoint,length, static_head,channel.channel_slope ,
    #         #                                 manning_coefficient ,channel.flow_rate,channel.velocity,channel.water_depth,
    #         #                                 max_flow_rate*3600,max_water_depth,bottom_width,channel.bank_slope,
    #         #                                 channel_depth, '',free_board, '','']
    #         #     channels_table.loc[len(channels_table)] = data

    #         # #     pipes_table, pumps_table = dwg_objects_sorting(acad=acad)
    # print(channels_table)