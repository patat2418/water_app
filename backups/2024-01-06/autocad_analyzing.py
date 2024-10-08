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

acad = Autocad(create_if_not_exists=True)

#### init ####
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
channel_text_layer.color = 5
channel_layer.color = 38
channel_water_layer.color = 5
channel_max_water_layer.color = 4


def dwg_objects_sorting():
    '''
    running on the dwg and sorting it's objects:
    '''
    i = 0
    j = 0
    k = 0
    
    pipes_table = pd.DataFrame(columns=['pipe #', 'start', 'end', 'pipe type',
        'nominal dia', 'id (mm)', 'length (m)', 'static head (endZ-startZ)', 
        'flow', 'consumption', 'velocity', 'head loss', 'total head loss', 'Pressure at end of pipe', 
        'start with', 'end with', 'costs per meter', 'total costs'])
    pumps_table = pd.DataFrame(columns=['pump #', 'center', 'flow' , 'head','efficiency','start num','power','wetpit min volume','connect to pipe'])
    channels_table = pd.DataFrame(columns=['channel #', 'start', 'end', 'length (m)', 'static head (endZ-startZ)', 'slope',
                                        'manning coeficent','flow' ,'velocity', 'water depth', 'max flow rates', 'max water depth',
                                        'geometry: bottom width','geometry: bank slope', 'geometry: channel depth', 'geometry: channel width', 
                                        'geometry: free board', 'start with', 'end with'])
    # channels_table = pd.DataFrame(columns=['Consumer #', 'Consumption', 'Min pressure' ])


    for obj in acad.iter_objects_fast():

        if obj.ObjectName == "AcDbLine":

            ##### Channels data: #####
                
            if obj.Layer.startswith('Channel_'):
                '''
                Layer template:
                m = bank slope
                b = bottom width
                n = manning coefficient
                q = flow rate
                mwd = Max Water Depth allowed
                cd = desgined Channel Depth
                fb = Free board

                '''
                
                
                channel_name = 'Channel '+ str(k+1)
                k += 1
                # print(channel_name)
                try:
                    bank_slope = float(re.search(r'(?:[_])m-(\d+)',obj.Layer).group(1))
                except:
                    #Create default values - rectangle channel
                    bank_slope = 0
                try:
                    bottom_width = float(re.search(r'(?:[_])b-(\d+)',obj.Layer).group(1))
                except:
                    #Create default values - Triangle channel
                    bottom_width = 0
                try:
                    max_water_depth = float(re.search(r'(?:[_])mwd-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    max_water_depth = False
                try:
                    flow_rate = float(re.search(r'(?:[_])q-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    flow_rate = 0
                try:
                    manning_coefficient = float(re.search(r'(?:[_])n-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    #Create default values
                    manning_coefficient = 0.035
                try:
                    channel_depth = float(re.search(r'(?:[_])cd-(\d*\.*\d+)',obj.Layer).group(1))
                    print(f"Channel depth {channel_depth}")
                except:
                    #Create default values
                    channel_depth = ""
                try:
                    free_board = float(re.search(r'(?:[_])fb-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    #Create default values
                    free_board = 0.25
                
                length=float(obj.Length)
                static_head=float(obj.Startpoint[2]-obj.Endpoint[2])
                channel_slope = static_head/length

                channel = entities.Channel(manning_coefficient=manning_coefficient,flow_rate=flow_rate,bank_slope=bank_slope,bottom_width=bottom_width,max_water_depth=max_water_depth,channel_slope=channel_slope)
                
                if channel_depth != "":
                    max_water_depth = channel_depth - free_board

                if max_water_depth:
                    max_flow_rate,max_velocity, max_wetted_perimeter, max_cross_sectional_area = eq.manning_eq_flow_from_water_level(max_water_depth,bottom_width,bank_slope,channel_slope,manning_coefficient)
                    print(f'the max flow rate is: {max_flow_rate*3600} m^3/hr, but the desgin is for {flow_rate} m^3/hr')
                    # if (max_water_high < channel.water_depth):
                        # print('Channel Geometry not good for that water flow')  
                else:
                    max_flow_rate=''
                    max_velocity=''
                    max_wetted_perimeter=''
                    max_cross_sectional_area=''

                data = [channel_name,obj.Startpoint,obj.Endpoint,length, static_head,channel.channel_slope ,
                                            manning_coefficient ,channel.flow_rate,channel.velocity,channel.water_depth,
                                            max_flow_rate*3600,max_water_depth,bottom_width,channel.bank_slope,
                                            channel_depth, '',free_board, '','']
                channels_table.loc[len(channels_table)] = data

            ##### Pipes data: #####
                
            if obj.Layer.startswith('Pipe_'):
                '''
                Layer template:

                Pipe_#Pipe_type#_#Nominal_diameter#_Consumption
                try:
                    max_water_depth = float(re.search(r'(?:[_])mwd-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    max_water_depth = False
                '''

                i += 1
                pipe_name = 'Pipe '+ str(i)
                
                tmp,pipetype, nd , consumption= obj.Layer.split('_')
                length=obj.Length
                static_head=obj.Endpoint[2]-obj.Startpoint[2]
                pipe = entities.Pipe(pipetype=pipetype,nominal_dia=float(nd),length=length,static_head=static_head)
                pipe.inside_dia = pipe.inside_dia_from_nominal(nd=pipe.nominal_dia)

                pipes_type_table = entities.pipes_type_dict[pipetype]
                costs_per_meter = pipes_type_table[pipes_type_table['ND'] == int(nd)]['prices'].values[0]
                total_costs = costs_per_meter*length

                data = [pipe_name,obj.Startpoint,obj.Endpoint,pipetype,nd,pipe.inside_dia,pipe.length,
                            pipe.static_head,"",float(consumption),"",
                            "","","","","",costs_per_meter,total_costs]
                pipes_table.loc[len(pipes_table)] = data

            ##### Pumps data: #####
        if (obj.Layer.startswith('Pump')) & (obj.ObjectName == "AcDbCircle"):
            j += 1
            pump_name = 'Pump '+ str(j)
            
            efficiency = 0.75 # Will change in the future 
            data = [pump_name,obj.Center,'',0,efficiency,'','','','']
            pumps_table.loc[len(pumps_table)] = data

    pipes_table.set_index(pipes_table['pipe #'],inplace=True)
    pumps_table.set_index(pumps_table['pump #'],inplace=True)
    channels_table.set_index(channels_table['channel #'],inplace=True)
    return pipes_table, pumps_table, channels_table

def is_pipe_conected(pipes_table: pd.DataFrame,pumps_table: pd.DataFrame):
    
    for i in range (len(pipes_table)):
        start_with_pipe_name = ''
        end_with_pipe_name = ''
        i_start_at = pipes_table['start'].iloc[i]
        i_end_at = pipes_table['end'].iloc[i]
        
        if not (pipes_table[pipes_table['end'] == i_start_at].empty):
            i_start_with = pipes_table[pipes_table['end'] == i_start_at]
            start_with_pipe_name = ', '.join(i_start_with['pipe #'])
            pipes_table['start with'].iloc[i] = start_with_pipe_name
        else:
            if not (pumps_table[pumps_table['center'] == i_start_at].empty):
                i_start_with = pumps_table[pumps_table['center'] == i_start_at]
                start_with_pump_name = ', '.join(i_start_with['pump #'])
                pipes_table['start with'].iloc[i] = start_with_pump_name
                pumps_table['connect to pipe'][start_with_pump_name] = pipes_table['pipe #'].iloc[i]


        if not (pipes_table[pipes_table['start'] == i_end_at].empty):
            i_end_with = pipes_table[pipes_table['start'] == i_end_at]
            end_with_pipe_name = ', '.join(i_end_with['pipe #'])
            pipes_table['end with'].iloc[i] = end_with_pipe_name
    
def add_text_to_dwg(pipes_table: pd.DataFrame,pumps_table: pd.DataFrame, channels_table: pd.DataFrame):
    
    ### Channel writing info:
    acad.ActiveDocument.ActiveLayer = channel_text_layer
    for i in range(len(channels_table)):

        p1 = APoint(channels_table['start'][i])
        p2 = APoint(channels_table['end'][i])

        p3 = APoint(uf.midpoint_betwen_to_points(p2,p1))
        
        #Vertex text
        vertex_text1 = f'Vertex number: {i+1}'
        vertex_text2 = f'Z={p1.z}'

        text = acad.model.Addtext(vertex_text1,p1,2.5)
        p1.y -= 4
        text = acad.model.Addtext(vertex_text2,p1,2.5)

        if i == (len(channels_table)-1):
            
            p4 = APoint(channels_table['end'][i])
            vertex_text1 = f'Vertex number: {i+2}'
            vertex_text2 = f'Z={p4.z}'
            
            text = acad.model.Addtext(vertex_text1,p4,2.5)
            p4.y -= 4
            text = acad.model.Addtext(vertex_text2,p4,2.5)

        #Channel text
        p3.y += 80

        channel_name = str(channels_table['channel #'][i])
        text = acad.model.Addtext(channel_name,p3,2.5)
        p3.y -= 4

        length = f"length: {round(channels_table['length (m)'][i],2)} m"
        text = acad.model.Addtext(length,p3,2.5)
        p3.y -= 4

        slope = f"slope: {round(float(channels_table['slope'][i]*100),2)} %"
        text = acad.model.Addtext(slope,p3,2.5)
        p3.y -= 4

        des_flow = f"the water level will be: {round(float(channels_table['water depth'][i]*100),2)} cm @ design flow rate {round(float(channels_table['flow'][i]),2)}"
        text = acad.model.Addtext(des_flow,p3,2.5)
        p3.y -= 4

        if channels_table['max water depth'][i]:
            max_flow = f"the max allowed water level is: {round(float(channels_table['max water depth'][i]*100),2)} cm @ flow rate {round(float(channels_table['max flow rates'][i]),2)}"
            text = acad.model.Addtext(max_flow,p3,2.5)
            p3.y -= 4

        # Channel sec
        ### data ###
        bottom_width = channels_table['geometry: bottom width'][i]*100
        bank_slope = channels_table['geometry: bank slope'][i]
        water_depth = channels_table['water depth'][i]*100
        flow_rate = channels_table['flow'][i]
        free_board =  channels_table['geometry: free board'][i]*100
        channel_depth = channels_table['geometry: channel depth'][i]*100
        max_water_depth = channels_table['max water depth'][i]*100
        max_flow_rate = channels_table['max flow rates'][i]

        try:
            channel_depth = float(channel_depth)
        except:
            try:
                    if max_water_depth:
                            channel_depth = float (max_water_depth)+float(free_board)

                    else:
                            channel_depth = float(channel_depth)
            except:
                    channel_depth = float (water_depth)+free_board
        
        side_steps = (channel_depth/100)*float(bank_slope)*100 
        water_side_steps = (water_depth/100)*float(bank_slope)*100
        max_water_side_steps = ((max_water_depth/100)*float(bank_slope))*100
        
        ############ Draw sec

        acad.ActiveDocument.ActiveLayer = channel_layer
        
        ps = APoint(channels_table['start'][i])
        pe = APoint(channels_table['end'][i])
        p3 = APoint(uf.midpoint_betwen_to_points(pe,ps))

        p3.y += 100 #Set (0,0) of section
        p3.z = 0

        p2 = APoint((p3.x - side_steps),(p3.y + channel_depth))
        p1 = APoint((p2.x-100), p2.y)
        
        if bottom_width != 0:
            p4 = APoint((p3.x + bottom_width),p3.y)
            p5 = APoint((p4.x + side_steps),(p4.y + channel_depth))
            p6 = APoint((p5.x+100),p5.y)
            p7 = APoint((p4.x + water_side_steps), (p4.y + water_depth))
            p8 = APoint((p4.x + max_water_side_steps), (p4.y + max_water_depth))
        else:
            p4 = APoint((p3.x + side_steps),(p3.y + channel_depth))
            p5 = APoint((p4.x+100),p4.y)
            p6 = p5
            p7 = APoint((p3.x + water_side_steps), (p3.y + water_depth))
            p8 = APoint((p3.x + max_water_side_steps), (p3.y + max_water_depth))


        acad.model.AddLine(p1,p2)
        acad.model.AddLine(p2,p3)
        acad.model.AddLine(p3,p4)
        acad.model.AddLine(p4,p5)
        acad.model.AddLine(p5,p6)

        ############ Draw water levels

        acad.ActiveDocument.ActiveLayer = channel_water_layer
        
        p9 = APoint((p3.x - water_side_steps),(p3.y + water_depth))
        water_line = acad.model.AddLine(p7,p9)
        water_text_point = APoint(uf.midpoint_betwen_to_points(p7,p9))
        water_text_point.x -= 50
        des_flow = f"the water level will be: {round(water_depth,2)} cm @ design flow rate {round(flow_rate,2)}"
        text = acad.model.Addtext(des_flow,water_text_point,2.5)

        if max_water_depth:
                acad.ActiveDocument.ActiveLayer = channel_max_water_layer
                p10 = APoint((p3.x - max_water_side_steps),(p3.y + max_water_depth))
                max_water_line = acad.model.AddLine(p8,p10)
                max_water_text_point = APoint(uf.midpoint_betwen_to_points(p8,p10))
                max_water_text_point.x -= 50
                max_flow = f"the maximum allowed water level is: {round(max_water_depth,2)} cm @ Max flow rate of {round(max_flow_rate,2)}"
                text = acad.model.Addtext(max_flow,max_water_text_point,2.5)

                if (max_water_depth < water_depth):
                    
                    max_water_text_point.y -= 10
                    max_water_text_point.x -= 50
                    bad_geometry_text ='Channel Geometry is not good for the designed water flow'
                    text1 = acad.model.Addtext(bad_geometry_text,max_water_text_point,5)
                    text1.color = 1

    ### Pump writing info:
    # acad.ActiveDocument.ActiveLayer = pump_text_layer
    for i in range(len(pumps_table)):
        
        # print(float_tuple_from_excel( pumps_table['center'][i]))
        acad.ActiveDocument.ActiveLayer = pipe_text_layer
        p1 = APoint(pumps_table['center'][i])
        p1.y += 30
        pump_name = str(pumps_table['pump #'][i])
        text = acad.model.Addtext(pump_name,p1,2.5)
        
        p1.y -= 4
        flow = f"flow: {pumps_table['flow'][i]} m^3/hr"
        text = acad.model.Addtext(flow,p1,2.5)

        p1.y -= 4
        head = f"head: {round(pumps_table['head'][i],2)} m"
        text = acad.model.Addtext(head,p1,2.5)

### Pipe writing info:
        
    acad.ActiveDocument.ActiveLayer = pipe_text_layer
    pump_name = 'Pump 1'
    prev_pipe = pipes_table[pipes_table['start with'] == pump_name]['start with'].values[0]
    current_pipe = pipes_table[pipes_table['start with'] == pump_name]['pipe #'].values[0]
    next_pipe = pipes_table[pipes_table['start with'] == pump_name]['end with'].values[0]
    
    for i in range(len(pipes_table)): #range(len(pipes_table))

        ####### Vertex text #####
        p1 = APoint(pipes_table.loc[current_pipe,'start']) # p1 = APoint(pipes_table['start'][i])

        if i == 0:
            pressure = pumps_table.loc[pump_name,"head"]
            consumption = 0
        else:
            pressure = pipes_table.loc[prev_pipe,"Pressure at end of pipe"]
            consumption = f'{pipes_table.loc[prev_pipe,"consumption"]}'
        
        vertex_text1 = f'Vertex number: {i+1}'
        vertex_text2 = f'Z={p1.z}'
        vertex_text3 = f'P={round(pressure,2)}'
        vertex_text4 = f'H={round(p1.z + pressure,2)}'
        vertex_text5 = f'consumption = {consumption}'

        text = acad.model.Addtext(vertex_text1,p1,2.5)
        p1.y -= 4
        text = acad.model.Addtext(vertex_text2,p1,2.5)
        p1.y -= 4
        text = acad.model.Addtext(vertex_text3,p1,2.5)
        p1.y -= 4
        text = acad.model.Addtext(vertex_text4,p1,2.5)
        p1.y -= 4
        text = acad.model.Addtext(vertex_text5,p1,2.5)

        if i == (len(pipes_table)-1):
            p4 = APoint(pipes_table.loc[current_pipe,'end'])
            pressure = pipes_table.loc[current_pipe,"Pressure at end of pipe"]
            consumption = pipes_table.loc[current_pipe,"consumption"]
            vertex_text1 = f'Vertex number: {i+2}'
            vertex_text2 = f'Z={p4.z}'
            vertex_text3 = f'P={round(pressure ,2)}'
            vertex_text4 = f'H={round(p1.z + pressure,2)}'
            vertex_text5 = f'consumption = {pipes_table.loc[prev_pipe,"consumption"]}'
            
            text = acad.model.Addtext(vertex_text1,p4,2.5)
            p4.y -= 4
            text = acad.model.Addtext(vertex_text2,p4,2.5)
            p4.y -= 4
            text = acad.model.Addtext(vertex_text3,p4,2.5)
            p4.y -= 4
            text = acad.model.Addtext(vertex_text4,p4,2.5)
            p4.y -= 4
            text = acad.model.Addtext(vertex_text5,p4,2.5)

#         print(f''' ################################################################
#                i={i} from {len(pipes_table)};
#                vertex number = {vertex_text1};
#                pressure = {pressure};
#                consumption = {consumption};
#                current_pipe = {current_pipe};
#                next_pipe = {next_pipe};
#  ''')
#         input("press any key: ")
        prev_pipe = current_pipe
        current_pipe = next_pipe
        try: 
            next_pipe = (pipes_table[pipes_table['pipe #'] == current_pipe]['end with'].values[0])
        except:
            next_pipe = ''


        p2 = APoint(pipes_table['end'][i])
        p3 = APoint(uf.midpoint_betwen_to_points(p2,p1))
        
        p3.y += 80

        pipe_name = str(pipes_table['pipe #'][i])
        text = acad.model.Addtext(pipe_name,p3,2.5)
        
        p3.y -= 4
        
        if pipes_table['pipe type'][i] == 'Steel':
            units = '"'
        else:
            units = 'mm'

        pipe_type = f"{pipes_table['pipe type'][i]} %%C {pipes_table['nominal dia'][i]} {units}"
        text = acad.model.Addtext(pipe_type,p3,2.5)
        
        p3.y -= 4
        length = f"length: {round(pipes_table['length (m)'][i],2)} m"
        text = acad.model.Addtext(length,p3,2.5)

        p3.y -= 4
        flow = f"flow: {pipes_table['flow'][i]} m^3/hr"
        text = acad.model.Addtext(flow,p3,2.5)

        p3.y -= 4
        flow = f"Total head loss: {round(pipes_table['total head loss'][i],2)} m"
        text = acad.model.Addtext(flow,p3,2.5)

def make_a_sec_grid (pipes_table, x_steps, y_steps):
    
    max_y : int = uf.round_to_next_i(pipes_table['static head (endZ-startZ)'].max(),y_steps)+y_steps
    min_y : int = uf.round_to_next_i(pipes_table['static head (endZ-startZ)'].min(),y_steps)-y_steps

    min_x = 0
    max_x = uf.round_to_next_i(int(sum(pipes_table['length (m)'])),x_steps)

    py1 = APoint((0,min_y,0))
    py2 = APoint((max_x,min_y,0))
    py3 = APoint((-50,min_y,0))
    py4 = APoint((-30,min_y-5,0))

    px1 = APoint((0,min_y,0))
    px2 = APoint((0,min_y+y_steps/2,0))
    px3 = APoint((0,max_y,0))
    px4 = APoint((px1.x-1,px1.y-5,0))
    
    titles = ['Total length:','Pipe length:','Pipe type:','Inside diameter:', 'Flow:']
    # print(max_x,'\ty: ', min_y,' ', max_y)
    for y in range (min_y,max_y+y_steps,y_steps):

        acad.ActiveDocument.ActiveLayer = grid_layer
        main_horizntel_line = acad.model.AddLine(py1,py2)
        
        acad.ActiveDocument.ActiveLayer = grid_text_layer
        text = acad.model.Addtext(py1.y,py1,2.5)
        # text.Justify = 1 
                
        py1.y += y_steps
        py2.y += y_steps
        py3.y += y_steps

    for i in range(len (titles)):
        acad.ActiveDocument.ActiveLayer = grid_text_layer
        text = acad.model.Addtext(titles[i],py4,2.5)
        py4.y -= 5

    for x in range (min_x, max_x+1,x_steps):    

        acad.ActiveDocument.ActiveLayer = grid_layer
        tips_line = acad.model.AddLine(px1,px2)
        grid_vertical_line = acad.model.AddLine(px1,px3)
        grid_vertical_line.color = 8

        acad.ActiveDocument.ActiveLayer = grid_text_layer
        text = acad.model.Addtext(f'{x} m',px4,2.5)    

        px1.x += x_steps
        px2.x += x_steps
        px3.x += x_steps
        px4.x += x_steps
    
    return min_x, max_x, min_y, max_y

def draw_pipe_sec ( pipes_table,min_y,max_y):
    
    total_length = 0 # sum of all pipe_length to point
    pipe_end_head = pipes_table['total head loss'].sum()

    for i in range(len(pipes_table)):
        
        ### data ###
        pipe_invert_start = pipes_table['start'][i][2]
        pipe_invert_end = pipes_table['end'][i][2]
        pipe_length = pipes_table['length (m)'][i]
        pipe_type = pipes_table['pipe type'][i]    
        pipe_start_head = pipe_end_head
        pipe_end_head = pipe_start_head - pipes_table['total head loss'][i]


        if pipe_type == 'Steel':
            pipes_type_table = entities.pipes_type_dict[pipe_type]
            od = pipes_type_table[pipes_type_table["ND"] == int(pipes_table['nominal dia'][i])]['OD'].iloc[0]/1000 
            min_wt = pipes_type_table[pipes_type_table['ND']==pipes_table['nominal dia'][i]]['wall thickness'].min()/1000
        else:
            od = float(pipes_table['nominal dia'][i])/1000
            min_wt = ((float(pipes_table['nominal dia'][i]) - float(pipes_table['id (mm)'][i]))/2)/1000

        ############ Draw pipe

        acad.ActiveDocument.ActiveLayer = pipe_layer
        ### invert line ###   
        p1 = APoint(total_length,pipe_invert_start)
        p2 = APoint((total_length + pipe_length),pipe_invert_end)
        acad.model.AddLine(p1,p2)

        ### down out side line
        p3 = APoint(total_length,pipe_invert_start - min_wt)
        p4 = APoint((total_length + pipe_length),pipe_invert_end - min_wt)
        acad.model.AddLine(p3,p4) 
        
        ### up out side line
        p5 = APoint(total_length,pipe_invert_start - min_wt + od)
        p6 = APoint((total_length + pipe_length),pipe_invert_end - min_wt + od)
        acad.model.AddLine(p5,p6)
        if i == 0:
            pipe_od = p6.y 

        ### up inside side line
        p7 = APoint(total_length,pipe_invert_start - min_wt*2 + od)
        p8 = APoint((total_length + pipe_length),pipe_invert_end - min_wt*2 + od)
        acad.model.AddLine(p7,p8) 

        ### pipe guideline ###
        p9 = APoint(total_length,min_y)
        p10 = APoint(total_length,max_y)
        acad.model.AddLine(p9,p10)
        
        acad.ActiveDocument.ActiveLayer = pipe_text_layer
        p11 = APoint (total_length + pipe_length/2, min_y - 5)
        text = acad.model.Addtext(f'{round(total_length + pipe_length/2 ,2)} m' ,p11,2.5)
        p11.y -= 5
        text = acad.model.Addtext(f'{round(pipe_length,2)} m',p11 ,2.5)
        p11.y -= 5
        text = acad.model.Addtext(f'{pipe_type} %%c{pipes_table["nominal dia"][i]}' ,p11 ,2.5)
        p11.y -= 5
        text = acad.model.Addtext(f'{pipes_table["id (mm)"][i]}' ,p11 ,2.5)
        p11.y -= 5
        text = acad.model.Addtext(f'{pipes_table["flow"][i]} m^3/hr' ,p11 ,2.5)

        ### Energy line
        acad.ActiveDocument.ActiveLayer = energy_line_layer
        p12 = APoint(total_length,pipe_start_head + pipe_od)
        p13 = APoint(total_length + pipe_length,pipe_end_head + pipe_od)
        acad.model.AddLine(p12,p13)
        text = acad.model.Addtext(f'{round(p12.y)} m' ,p12 ,2.5)
        
        ####### Reset to next pipe #########
        total_length += pipe_length       

##### test area

if __name__=='__main__':


    pipes_table = pd.DataFrame()
    pumps_table = pd.DataFrame()
    channels_table = pd.DataFrame()
    
    pipes_table, pumps_table, channels_table = dwg_objects_sorting()
    is_pipe_conected(pipes_table,pumps_table)

    with pd.ExcelWriter('data\\outputs\\acad-pipelines.xlsx') as writer:
        pipes_table.to_excel(writer,sheet_name='Pipes',index=False)
        pumps_table.to_excel(writer,sheet_name='Pumps',index=False)
        channels_table.to_excel(writer,sheet_name='Channels',index=False)    
    os.startfile('data\\outputs\\acad-pipelines.xlsx')    


# acad = Autocad(create_if_not_exists=True)
# pipes_table, pumps_table = dwg_objects_sorting(acad=acad)

# print(pumps_table)
