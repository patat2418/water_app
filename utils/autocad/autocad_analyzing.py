import sys
import os
from pyautocad import Autocad, APoint
from math import *
import pandas as pd
import win32com.client
import re

# from utils.autocad.add_objects.add_text import add_channels_text, add_pipes_text, add_pumps_text
sys.path.insert(1,os.getcwd())
from utils import eq
from utils import useful_functions as uf
from entities import entities
from utils.autocad import pipes_network_sytems

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

def dwg_objects_sorting():
    '''
    running on the dwg and sorting it's objects:
    '''
    i = 0
    j = 0
    k = 0
    
    pipes_table = pd.DataFrame(columns=['pipe #', 'start', 'end', 'pipe type',
        'nominal dia', 'id (mm)', 'length (m)', 'static head (endZ-startZ)', 
        'flow', 'consumption', 'minimum pressure required', 'velocity', 'head loss', 'total head loss', 'Pressure at end of pipe', 
        'start with', 'end with', 'costs per meter', 'total costs'])
    pumps_table = pd.DataFrame(columns=['pump #', 'center', 'flow' , 'head','efficiency','start num','power','wetpit min volume','connect to pipe'])
    channels_table = pd.DataFrame(columns=['channel #', 'start', 'end', 'length (m)', 'static head (endZ-startZ)', 'slope',
                                        'manning coeficent','flow' ,'velocity', 'water depth', 'max flow rates', 'max water depth',
                                        'geometry: bottom width','geometry: bank slope', 'geometry: channel depth', 'geometry: channel width', 
                                        'geometry: free board', 'start with', 'end with'])
    
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
                    bank_slope = float(re.search(r'(?:[_])m-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    #Create default values - rectangle channel
                    bank_slope = 0
                try:
                    bottom_width = float(re.search(r'(?:[_])b-(\d*\.*\d+)',obj.Layer).group(1))
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

                Pipe_type-(Steel)_nd-20_flow-200_MPressure-20
                type = Pipe type
                nd = Nominal diameter
                flow = consumptioin in junction
                MPressure = minimum pressure at junction
                '''  
                i += 1
                pipe_name = 'Pipe '+ str(i)
                
                try:
                    pipe_type = re.search(r'(?:[_])type-\(([^)]+)\)',obj.Layer).group(1)
                except:
                    raise TypeError("Pipe type is requierd!")
                try:
                    nominal_diameter = float(re.search(r'(?:[_])nd-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    raise TypeError("Nominal diameter is requierd!")
                # try:
                #     consumption = float(re.search(r'(?:[_])dn-(\d*\.*\d+)',obj.Layer).group(1))
                # except:
                #     consumption = 0
                try:
                    consumption = float(re.search(r'(?:[_])flow-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    consumption = 0
                try:
                    min_pressure = float(re.search(r'(?:[_])MPressure-(\d*\.*\d+)',obj.Layer).group(1))
                except:
                    min_pressure = 0

                # print(f'''##############################################
                #     pipe name = {pipe_name}
                #     pipe type = {pipe_type}
                #     nominal diameter = {nominal_diameter}
                #     consumption = {consumption}
                #     min_pressure = {min_pressure}
                # ''')
                # input('press a key')
                length=obj.Length
                static_head=obj.Endpoint[2]-obj.Startpoint[2]
                pipe = entities.Pipe(pipetype=pipe_type,nominal_dia=float(nominal_diameter),length=length,static_head=static_head)
                pipe.inside_dia = pipe.inside_dia_from_nominal(nd=pipe.nominal_dia)

                pipes_type_table = entities.pipes_type_dict[pipe_type]
                costs_per_meter = pipes_type_table[pipes_type_table['ND'] == int(nominal_diameter)]['prices'].values[0]
                total_costs = costs_per_meter*length

                data = [pipe_name,obj.Startpoint,obj.Endpoint,pipe_type,nominal_diameter,pipe.inside_dia,pipe.length,
                            pipe.static_head,"",float(consumption),min_pressure,"",
                            "","","","","",costs_per_meter,total_costs]
                pipes_table.loc[len(pipes_table)] = data
                pipes_table.set_index(pipes_table['pipe #'],inplace=True)

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
    
# def add_text_to_dwg(pipes_table: pd.DataFrame,pumps_table: pd.DataFrame, channels_table: pd.DataFrame):

#     add_channels_text(acad, channels_table, layers_dict)
#     add_pipes_text(acad, pipes_table, layers_dict)
#     add_pumps_text(acad, pumps_table, layers_dict)

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

    from utils.autocad import pipes_network_sytems

    pipes_table = pd.DataFrame()
    pumps_table = pd.DataFrame()
    channels_table = pd.DataFrame()
    
    pipes_table, pumps_table, channels_table = dwg_objects_sorting()
    is_pipe_conected(pipes_table,pumps_table)

    ###### pump restart
    pump_number = pumps_table['pump #'][0]
    pump_flow = pipes_table['consumption'].sum()  
    pumps_table['flow'][pump_number] = pump_flow
    pump1 = entities.Pump(rated_flow=pump_flow)

    
    ### Pipes data ###
    
    junctions_list= list(pipes_table[pipes_table['end with'].str.contains(',', na=False)]['pipe #'])
        
    for junction in junctions_list:
        
        pass

    previous_pipe_number = 0

    

    for pipe in range(0,len(pipes_table.index)):

        if pipe == 0:
            new_pipe_number = pipes_table[pipes_table['start with'] == pump_number]['end with'].index[0]
            flow_rate = pump_flow
 
        else:
            new_pipe_number = pipes_table['end with'][previous_pipe_number]
            flow_in = float(pipes_table['flow'][previous_pipe_number])
            consumption = float(pipes_table['consumption'][previous_pipe_number])
            flow_rate = flow_in - consumption

        # if new_pipe_number

        pipetype = pipes_table['pipe type'][new_pipe_number]
        nominal_dia = pipes_table['nominal dia'][new_pipe_number]
        inside_dia = pipes_table['id (mm)'][new_pipe_number]
        length = pipes_table['length (m)'][new_pipe_number]
        static_head = pipes_table['static head (endZ-startZ)'][new_pipe_number]
    
        pipe1 = entities.Pipe(pipetype=pipetype,nominal_dia=nominal_dia,inside_dia=inside_dia,length=length,static_head=static_head,flow_rate=flow_rate)

        velocity = pipe1.velocity()
        head_loss = pipe1.major_head_loss()
        total_headloss = pipe1.total_head_loss()

        pipes_table['flow'][new_pipe_number] = flow_rate 
        pipes_table['velocity'][new_pipe_number] = velocity
        pipes_table['head loss'][new_pipe_number] = head_loss
        pipes_table['total head loss'][new_pipe_number] = total_headloss

        previous_pipe_number = new_pipe_number
    
    minimum_pressure = pipes_network_sytems.add_pressure_at_end_of_pipe(pipes_table)

    with pd.ExcelWriter('data\\outputs\\acad-pipelines.xlsx') as writer:
        pipes_table.to_excel(writer,sheet_name='Pipes',index=False)
        pumps_table.to_excel(writer,sheet_name='Pumps',index=False)
        channels_table.to_excel(writer,sheet_name='Channels',index=False)    
    os.startfile('data\\outputs\\acad-pipelines.xlsx')    



if __name__=='__main__':
    import re
    pipes_table = pd.DataFrame()
    pumps_table = pd.DataFrame()
    channels_table = pd.DataFrame()
    eco_pipes_table = pipes_table.copy()
    eco_pumps_table = pumps_table.copy()

    acad = Autocad(create_if_not_exists=True)
    
    k = 0 

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
    # Define simplified patterns and default values in a dictionary
                patterns = {
                    'bank_slope': {'pattern': r'm-', 'default': 0},
                    'bottom_width': {'pattern': r'b-', 'default': 0},
                    'max_water_depth': {'pattern': r'mwd-', 'default': False},
                    'flow_rate': {'pattern': r'q-', 'default': 0},
                    'manning_coefficient': {'pattern': r'n-', 'default': 0.035},
                    'channel_depth': {'pattern': r'cd-', 'default': ""},
                    'free_board': {'pattern': r'fb-', 'default': 0.25}
                }

                # Function to extract values from obj.Layer using the provided pattern
                def extract_value(pattern, obj):
                    search_pattern = rf'(?:[_]){pattern}(\d*\.*\d+)'
                    try:
                        return float(re.search(search_pattern, obj.Layer).group(1))
                    except:
                        return patterns[pattern]['default']

                # Create a dictionary to store the extracted values
                extracted_values = {}

                # Loop through patterns and extract values
                for key, value in patterns.items():
                    extracted_value = extract_value(value['pattern'], obj)
                    if key == 'channel_depth':
                        print(f"Channel depth {extracted_value}")
                    # Store the extracted value in the dictionary
                    extracted_values[key] = extracted_value
            #     pipes_table, pumps_table = dwg_objects_sorting(acad=acad)
    print(extracted_value)

            # # print(pumps_table)
