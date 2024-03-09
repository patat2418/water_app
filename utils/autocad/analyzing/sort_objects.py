import re
import pandas as pd
from entities import entities
from utils import eq
from pyautocad import Autocad, APoint, aDouble
from utils.autocad.autocad_analyzing import acad

    # Function to extract values from obj.Layer using the provided pattern and default value
def extract_value(pattern:str, default:float|bool, obj)-> float|bool:
    if pattern == 'type-':
        search_pattern = rf'(?:[_]){pattern}\(([^)]+)\)'
    else:
        search_pattern = rf'(?:[_]){pattern}(\d*\.*\d+)'
    try:
        return float(re.search(search_pattern, obj.Layer).group(1))
    except ValueError:
        return re.search(search_pattern, obj.Layer).group(1)
    except Exception as e:
        print(e)

        return default  # Return None if extraction fails
    
def create_tables()-> tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    pipes_table = pd.DataFrame(columns=['pipe #', 'start', 'end', 'pipe type',
        'nominal dia', 'id (mm)', 'length (m)', 'static head (endZ-startZ)', 
        'flow', 'consumption', 'minimum pressure required', 'velocity', 'head loss', 'total head loss', 'Pressure at end of pipe', 
        'start with', 'end with', 'costs per meter', 'total costs'])
    pumps_table = pd.DataFrame(columns=['pump #', 'center', 'flow' , 'head','efficiency','start num','power','wetpit min volume','connect to pipe'])
    channels_table = pd.DataFrame(columns=['channel #', 'start', 'end', 'length (m)', 'static head (endZ-startZ)', 'slope',
        'manning coeficent','flow' ,'velocity', 'water depth', 'max flow rates', 'max water depth',
        'geometry: bottom width','geometry: bank slope', 'geometry: channel depth', 'geometry: channel width', 
        'geometry: free board', 'start with', 'end with'])
    return pipes_table, pumps_table, channels_table
    
def sort_objects() -> tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    
    pipes_table, pumps_table, channels_table =create_tables()
    i = 0
    j = 0
    k = 0 
    # channels = {}
    for obj in acad.iter_objects_fast():

        if obj.ObjectName == "AcDbLine":
            
            if obj.Layer.startswith('Pipe_'):
                sort_pipes(pipes_table, i, obj)
                i += 1
            if obj.Layer.startswith('Channel_'):
                sort_channels(channels_table, j, obj)
                j += 1
        if (obj.Layer.startswith('Pump')) & (obj.ObjectName == "AcDbCircle"):
            sort_pumps(pumps_table, k, obj)
            k += 1
    pipes_table.set_index(pipes_table['pipe #'],inplace=True)
    pumps_table.set_index(pumps_table['pump #'],inplace=True)
    channels_table.set_index(channels_table['channel #'],inplace=True)
    return pipes_table, pumps_table, channels_table


def sort_pipes(pipes_table:pd.DataFrame, i:int, obj):
    '''
    Layer template:

    Pipe_type-(Steel)_nd-20_flow-200_MPressure-20
    type = Pipe type
    nd = Nominal diameter
    flow = consumptioin in junction
    MPressure = minimum pressure at junction
    '''  
    def pipes_raise_error(msg):
        raise TypeError(msg)   
    pipe_name = 'Pipe '+ str(i+1)

    # Define simplified patterns and corresponding variables in a dictionary
    patterns = {
        'pipe_type': {'pattern': r'type-', 'default':False},
        'nominal_diameter': {'pattern': r'nd-', 'default': False},
        'consumption': {'pattern': r'flow-', 'default': 0},
        'flow_rate': {'pattern': r'q-', 'default': 0},
        'min_pressure': {'pattern': r'MPressure-', 'default': 0},
    }

    # Loop through patterns and extract values
    extracted_values = {}
    for key, value in patterns.items():
        extracted_value = extract_value(value['pattern'], value['default'], obj)
        extracted_values[key] = extracted_value

    if not extracted_values['pipe_type']:
        pipes_raise_error("Pipe type is requierd!")
    elif not extracted_values['nominal_diameter']:
        pipes_raise_error("Nominal diameter is requierd!")
    pipe_type = extracted_values['pipe_type']
    nominal_diameter = extracted_values['nominal_diameter']
    consumption = extracted_values['consumption']
    flow_rate = extracted_values['flow_rate']
    min_pressure = extracted_values['min_pressure']
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

def sort_channels(channels_table:pd.DataFrame, j:int, obj):
    
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
    
    channel_name = 'Channel '+ str(j+1)
 
    # Define simplified patterns and corresponding variables in a dictionary
    patterns = {
        'bank_slope': {'pattern': r'm-', 'default': 0},
        'bottom_width': {'pattern': r'b-', 'default': 0},
        'max_water_depth': {'pattern': r'mwd-', 'default': False},
        'flow_rate': {'pattern': r'q-', 'default': 0},
        'manning_coefficient': {'pattern': r'n-', 'default': 0.035},
        'channel_depth': {'pattern': r'cd-', 'default': ""},
        'free_board': {'pattern': r'fb-', 'default': 0.25}
    }

    # Loop through patterns and extract values
    extracted_values = {}
    for key, value in patterns.items():
        extracted_value = extract_value(value['pattern'], value['default'], obj)
        extracted_values[key] = extracted_value
    
    bank_slope = extracted_values['bank_slope']
    bottom_width = extracted_values['bottom_width']
    max_water_depth = extracted_values['max_water_depth']
    flow_rate = extracted_values['flow_rate']
    manning_coefficient = extracted_values['manning_coefficient']
    channel_depth = extracted_values['channel_depth']
    free_board = extracted_values['free_board']
    length=float(obj.Length)
    static_head=float(obj.Startpoint[2]-obj.Endpoint[2])
    channel_slope = static_head/length

    channel = entities.Channel(manning_coefficient=manning_coefficient,flow_rate=flow_rate,bank_slope=bank_slope,bottom_width=bottom_width,max_water_depth=max_water_depth,channel_slope=channel_slope)
    
    if channel_depth != "":
        max_water_depth = channel_depth - free_board

    if max_water_depth:
        max_flow_rate,max_velocity, max_wetted_perimeter, max_cross_sectional_area = eq.manning_eq_flow_from_water_level(max_water_depth,bottom_width,bank_slope,channel_slope,manning_coefficient)  
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

def sort_pumps(pumps_table:pd.DataFrame, k:int, obj):
    
    pump_name = 'Pump '+ str(k+1)     
    efficiency = 0.75 # Will change in the future 
    data = [pump_name,obj.Center,'',0,efficiency,'','','','']
    pumps_table.loc[len(pumps_table)] = data