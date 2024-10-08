import sys
import os
import win32com.client
import pandas as pd
from pyautocad import Autocad, APoint, aDouble

sys.path.insert(1,os.getcwd())
from utils import eq
from utils import useful_functions as uf
from entities import entities
from utils.autocad import autocad_functions

acad = Autocad(create_if_not_exists=True)

# https://help.autodesk.com/view/OARX/2022/ENU/?guid=GUID-1E17B5E6-92FC-433C-97B7-760A0BEB73AC

#### init ####

# entities.pipes_type_dict = pd.read_excel('data\\info\\pipes.xlsx',sheet_name=None)
# entities.pipes_type_lower = [x.lower() for x in entities.pipes_type_dict.keys()]
# pipes_type_table = pd.ExcelFile('data\\info\\pipes.xlsx').sheet_names
# pipes_type_table_l = [x.lower() for x in pipes_type_table]


def get_string_from_prompt(acad,prompt_str):
    user_input = acad.doc.Utility.GetString(1,prompt_str)
    return user_input

def get_keyword_from_prompt(acad,prompt_str,var_list):
    acad.doc.Utility.GInitializeUserInput (1, var_list)
    user_input = acad.doc.Utility.GetKeyword(prompt_str + var_list)
    return user_input

def make_a_pipe(acad,pipe_name: str ):
    
    def get_user_pipe_type():
        
        
        pipetype = get_string_from_prompt(acad,f'{pipe_name}Enter pipe type: + {entities.pipes_type_dict.keys()}:')
        
        if (pipetype.lower() not in entities.pipes_type_lower):
            
            while True:

                if pipetype.lower() == 's':
                    pipetype = 'Steel'
                    break

                if pipetype.lower() in [x.lower().replace('pe100-','') for x in entities.pipes_type_dict.keys()]:
                    pipetype = f'PE100-{pipetype}'
                    break

                pipetype = autocad_functions.get_string_from_prompt(acad,f'WRONG INPUT!\nEnter pipe type: + {entities.pipes_type_dict.keys()}:')
                
                if pipetype.lower() in entities.pipes_type_lower:
                    break
        if pipetype == 'steel':
            pipetype.capitalize()
        return pipetype

    def pipe_diameter_table (pipetype: str) -> list:
        if pipetype == 'Steel':
            a = list(entities.pipes_type_dict[pipetype]['ND'].drop_duplicates().values)
            b = [str(x) for x in a]
            return b
        else:
            # print(pipe_table[(pipe_table['Id']!= 0) or ()])
            a = list(entities.pipes_type_dict[pipetype][entities.pipes_type_dict[pipetype]['Id'] > 0]['ND'])
            b = [str(x) for x in a]
            return b

    def get_user_nominal_diameter(pipetype):
        
        pipe_diameter_table1 = uf.pipe_diameter_table(pipetype)
        nominal_dia = autocad_functions.get_string_from_prompt(acad,f'{pipe_name}Enter Nominal Diameter: + {pipe_diameter_table1}:')
        while nominal_dia not in pipe_diameter_table1:

            nominal_dia = autocad_functions.get_string_from_prompt(acad,f'WRONG INPUT!\nEnter Nominal Diameter: + {pipe_diameter_table1}:')
        
        return nominal_dia

    def get_user_consumption ():
        consumption = autocad_functions.get_string_from_prompt(acad,f'Enter End Consumption in m^3/hr:')
        while True:
            try:
                float (consumption)
                break
            except:
                consumption = autocad_functions.get_string_from_prompt(acad,f'Error!!\nEnter End Consumption in m^3/hr:')
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


# make_a_pipe(acad,'1')
# print (a)
