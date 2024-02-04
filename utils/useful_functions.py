import sys
import os
import pandas as pd

sys.path.insert(1,os.getcwd())
# from utils import eq, init
# from utils.autocad import autocad_functions,pipes_network_sytems,autocad_analyzing
from entities import entities

#### INIT ####
# entities.pipes_type_dict = pd.read_excel('data\\info\\pipes.xlsx',sheet_name=None)

#######
def float_tuple_from_str(string_tuple:tuple[str])->tuple[float]:
    '''
    string_tuple = '(1.0,2.0,3.0)'
    float_tuple = (1.0,2.0,3.0)
    '''

    float_tuple = tuple(map(float, string_tuple.strip('()').split(',')))
    return float_tuple

def is_float(string:str)-> bool :
    try:
        float(string)
        return True
    except ValueError:
        return False

def is_float_message(string:str, name:str)-> str:
    msg = ""
    if not is_float(string):
        msg = f'{name}: expected to be a number instead got: {string}'
    return msg

def midpoint_betwen_to_points(p1:tuple,p2:tuple)->tuple:
    p3 = tuple([(p1[i]+p2[i])/2 for i,cor in enumerate(p1)])
    return p3

def round_by_base(x, base):
    return base * round(x/base)

def round_to_next_i(n,i) -> int:
    if n >= 0:
        rounded_n = n + (i - n) % i
    else:
        rounded_n = n - (i + n) % i
    return int(rounded_n)

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

