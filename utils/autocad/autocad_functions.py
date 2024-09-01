import sys
import os
import win32com.client
import pandas as pd
from pyautocad import Autocad, APoint, aDouble

sys.path.insert(1,os.getcwd())
from utils import eq
from utils import useful_functions as usf
from entities import entities
from utils.autocad import autocad_functions

acad = Autocad(create_if_not_exists=True)

# https://help.autodesk.com/view/OARX/2022/ENU/?guid=GUID-1E17B5E6-92FC-433C-97B7-760A0BEB73AC

#### init ####

# entities.pipes_type_dict = pd.read_excel('data\\info\\pipes.xlsx',sheet_name=None)
# entities.pipes_type_lower = [x.lower() for x in entities.pipes_type_dict.keys()]
# pipes_type_table = pd.ExcelFile('data\\info\\pipes.xlsx').sheet_names
# pipes_type_table_l = [x.lower() for x in pipes_type_table]



def get_string_from_prompt(prompt_str):
    user_input = acad.doc.Utility.GetString(1,prompt_str)
    return user_input

def get_keyword_from_prompt(prompt_str,var_list):
    acad.doc.Utility.GInitializeUserInput (1, var_list)
    user_input = acad.doc.Utility.GetKeyword(prompt_str + var_list)
    return user_input

def create_a_pipe_layer (pipetype:str, nd:str, consumption:str, min_pressure:str) -> str:
        '''Pipe_type-(Steel)_nd-20_flow-200_MPressure-20'''
        layer_name = f"Pipe_type-({pipetype})_nd-{str(nd)}_flow-{str(consumption)}_MPressure-{str(min_pressure)}"
        acad.ActiveDocument.Layers.Add(layer_name)
        return layer_name

def make_a_pipe_from_app(pipetype:str, nd:int, consumption='0', min_pressure='0') -> None:

    # def create_layer(pipetype:str, nd:str, consumption:str, min_pressure:str) -> str:
    #     '''Pipe_type-(Steel)_nd-20_flow-200_MPressure-20'''
    #     layer_name = f"Pipe_type-({pipetype})_nd-{str(nd)}_flow-{str(consumption)}_MPressure-{str(min_pressure)}"
    #     acad.ActiveDocument.Layers.Add(layer_name)
    #     return layer_name

    for obj in acad.get_selection("please select new pipe:"):
        # print(obj.Layer)
        layer_name = create_a_pipe_layer(pipetype, nd, consumption, min_pressure)
        obj.Layer = layer_name

def draw_a_pipe_from_app(pipetype:str, nd:int, consumption='0', start_elv="" ,end_elv="",min_pressure='0'):

    # def create_layer(pipetype:str, nd:str, consumption:str, min_pressure:str) -> str:
    #     '''Pipe_type-(Steel)_nd-20_flow-200_MPressure-20'''
    #     layer_name = f"Pipe_type-({pipetype})_nd-{str(nd)}_flow-{str(consumption)}_MPressure-{str(min_pressure)}"
    #     acad.ActiveDocument.Layers.Add(layer_name)
    #     return layer_name

    layer_name = create_a_pipe_layer(pipetype, nd, consumption, min_pressure)
    acad.prompt('Selcet Pipe start point:')
    start = APoint(acad.doc.Utility.GetPoint())
    acad.prompt('Selcet Pipe end point:')
    end = APoint(acad.doc.Utility.GetPoint())
    try:
        start[2] = float(start_elv)
        # print(1)
    except:
        pass
    
    try:
        end[2] = float(end_elv)
        # print(2)
    except:
        pass

    new_pipe = acad.model.AddLine(start,end)
    
    new_pipe.Layer = layer_name
    new_pipe.color = 4

def make_a_pump_from_app(efficiency:str, starts_per_hour:str):

    def create_layer(efficiency:str, starts_per_hour:str) -> str:
        layer_name = f"Pump_{efficiency}_{starts_per_hour}"
        acad.ActiveDocument.Layers.Add(layer_name)
        return layer_name

    
    for obj in acad.get_selection("please select new pump:"):
        
        layer_name = create_layer(efficiency, starts_per_hour)

        obj.Layer = layer_name
        


def make_a_pipe(pipe_name: str ): ## _from_prompt
    
    def get_user_pipe_type():
                
        pipetype = get_string_from_prompt(f'{pipe_name}Enter pipe type: + {entities.pipes_type_dict.keys()}:')
        
        if (pipetype.lower() not in entities.pipes_type_lower):
            
            while True:

                if pipetype.lower() == 's':
                    pipetype = 'Steel'
                    break

                if pipetype.lower() in [x.lower().replace('pe100-','') for x in entities.pipes_type_dict.keys()]:
                    pipetype = f'PE100-{pipetype}'
                    break

                pipetype = autocad_functions.get_string_from_prompt(f'WRONG INPUT!\nEnter pipe type: + {entities.pipes_type_dict.keys()}:')
                
                if pipetype.lower() in entities.pipes_type_lower:
                    break
        if pipetype == 'steel':
            pipetype.capitalize()
        return pipetype

    def get_user_nominal_diameter(pipetype):
        
        pipe_diameter_table1 = usf.pipe_diameter_table(pipetype)
        nominal_dia = autocad_functions.get_string_from_prompt(f'{pipe_name}Enter Nominal Diameter: + {pipe_diameter_table1}:')
        while nominal_dia not in pipe_diameter_table1:

            nominal_dia = autocad_functions.get_string_from_prompt(f'WRONG INPUT!\nEnter Nominal Diameter: + {pipe_diameter_table1}:')
        
        return nominal_dia

    def get_user_consumption ():
        consumption = autocad_functions.get_string_from_prompt(f'Enter End Consumption in m^3/hr:')
        while True:
            try:
                float (consumption)
                break
            except:
                consumption = autocad_functions.get_string_from_prompt(f'Error!!\nEnter End Consumption in m^3/hr:')
        return consumption

    def create_layer(pipetype:str, nd:int, consumption:str) -> str:
        layer_name = f"{pipetype}_{nd}_{consumption}"
        acad.ActiveDocument.Layers.Add(layer_name)
        return layer_name

    for obj in acad.get_selection("please select new pipe:"):
        print(obj.Layer)
        pipetype = get_user_pipe_type()
        nd = get_user_nominal_diameter(pipetype)
        consumption = get_user_consumption()
        layer_name = create_layer(pipetype, nd, consumption)
        obj.Layer = layer_name


# make_a_pipe('1')
# print (a)
# draw_a_pipe_from_app('Steel', 12, 300,"12",12.3)
