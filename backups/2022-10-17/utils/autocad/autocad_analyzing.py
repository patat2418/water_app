import sys
import os
from pyautocad import Autocad, APoint, aDouble
from math import *
import pandas as pd
import win32com.client

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

grid_layer.color = 7
grid_text_layer.color = 7
pipe_layer.color = 5
pipe_guideline_layer.color = 8
pipe_text_layer.color = 7
energy_line_layer.color = 6
pump_text_layer = 7


def dwg_objects_sorting(acad):
    '''
    running on the dwg and sorting it's objects:
    '''
    i = 0
    j = 0
    pipes_table = pd.DataFrame(columns=['pipe #', 'start', 'end', 'pipe type',
        'nominal dia', 'id (mm)', 'length (m)', 'static head (endZ-startZ)', 
        'flow', 'consumption', 'velocity', 'head loss', 'total head loss', 'start with', 'end with', 'costs per meter', 'total costs'])
    pumps_table = pd.DataFrame(columns=['pump #', 'center', 'flow' , 'head','efficiency','start num','power','wetpit min volume','connect to pipe'])

    for obj in acad.iter_objects_fast():

        # print("Type of object: " + obj.ObjectName)
        
        if obj.ObjectName == "AcDbLine":
            
            if obj.Layer.startswith('Pipe_'):
                # if obj.Startpoint in pipes_table & obj
                pipe_name = 'Pipe '+ str(i+1)
                i += 1
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
                            "","","","",costs_per_meter,total_costs]
                pipes_table.loc[len(pipes_table)] = data

        if (obj.Layer.startswith('Pump')) & (obj.ObjectName == "AcDbCircle"):
            pump_name = 'Pump '+ str(j+1)
            j += 1
            # print(pipes_table['consumption'].sum())
            # flow = pipes_table['consumption'].sum()
            # pump = entities.Pump(rated_flow=flow)
            efficiency = 0.75 # Will change in the futere 
            # wetpit = pump.min_wet_pit(flow,8)
            data = [pump_name,obj.Center,'',0,efficiency,'','','','']
            pumps_table.loc[len(pumps_table)] = data
            #'pump #', 'center', 'flow' , 'head','efficiency','start num','power','wetpit min volume','connect to pipe'
    # pipes_table['start']

    pipes_table.set_index(pipes_table['pipe #'],inplace=True)
    pumps_table.set_index(pumps_table['pump #'],inplace=True)
    return pipes_table, pumps_table

def is_pipe_conected(pipes_table,pumps_table):
    for i in range (len(pipes_table)):
        start_with_pipe_name = ''
        end_with_pipe_name = ''
    #     print(f'i={i}')
        i_start_at = pipes_table['start'].iloc[i]
        i_end_at = pipes_table['end'].iloc[i]
        # print(i_start_at[0])
        # if pipes_table[pipes_table['start']
        if not (pipes_table[pipes_table['end'] == i_start_at].empty):
    #         print(f'pipe {i+1} is connected at point {a1}!')
            i_start_with = pipes_table[pipes_table['end'] == i_start_at]
            start_with_pipe_name = ', '.join(i_start_with['pipe #'])
            pipes_table['start with'].iloc[i] = start_with_pipe_name
        else:
            if not (pumps_table[pumps_table['center'] == i_start_at].empty):
                i_start_with = pumps_table[pumps_table['center'] == i_start_at]
                # print (i_start_with)
                start_with_pump_name = ', '.join(i_start_with['pump #'])
                # print(f'pump name:{start_with_pump_name}')
                pipes_table['start with'].iloc[i] = start_with_pump_name
                # print(pipes_table['pipe #'].iloc[i])
                pumps_table['connect to pipe'][start_with_pump_name] = pipes_table['pipe #'].iloc[i]


        if not (pipes_table[pipes_table['start'] == i_end_at].empty):
    #         print(f'pipe {i+1} is delivered to point {a2}!')
            i_end_with = pipes_table[pipes_table['start'] == i_end_at]
            end_with_pipe_name = ', '.join(i_end_with['pipe #'])
            pipes_table['end with'].iloc[i] = end_with_pipe_name
    
def add_text_to_dwg(pipes_table,pumps_table,acad):
    
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
    for i in range(len(pipes_table)):
    
        p1 = APoint(pipes_table['start'][i])

        vertex_text1 = f'Vertex number: {i+1}'
        vertex_text2 = f'Z={p1.z}'
        vertex_text3 = f'consumption = {pipes_table["consumption"][i]}'
        text = acad.model.Addtext(vertex_text1,p1,2.5)
        p1.y -= 4
        text = acad.model.Addtext(vertex_text2,p1,2.5)
        p1.y -= 4
        text = acad.model.Addtext(vertex_text3,p1,2.5)

        if i == (len(pipes_table)-1):
            
            p4 = APoint(pipes_table['end'][i])
            vertex_text1 = f'Vertex number: {i+2}'
            vertex_text2 = f'Z={p4.z}'
            vertex_text3 = f'consumption = {pipes_table["consumption"][i]}'
            text = acad.model.Addtext(vertex_text1,p4,2.5)
            p4.y -= 4
            text = acad.model.Addtext(vertex_text2,p4,2.5)
            p4.y -= 4
            text = acad.model.Addtext(vertex_text3,p4,2.5)

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

####################### def - make_a_sec_grid (acad, pipes_table, x_steps, y_steps)
def make_a_sec_grid (acad, pipes_table, x_steps, y_steps):
    
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


####################### Def - draw_pipe_sec (acad, pipes_table)
def draw_pipe_sec (acad, pipes_table,min_y,max_y):
    
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

# acad = Autocad(create_if_not_exists=True)
# pipes_table, pumps_table = dwg_objects_sorting(acad=acad)

# print(pumps_table)
