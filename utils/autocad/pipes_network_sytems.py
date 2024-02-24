from pprint import pprint
import sys
import os
import pandas as pd
sys.path.insert(1,os.getcwd())
from entities import entities

# def next_branches_not_tested(branches_tree:dict):
    # # found_not_tested_branch = False
    # # Iterate over the main dictionary
    # for pipe, branches in branches_tree.items():
    #     # Iterate over the branches for each pipe
    #     for branch, branch_info in branches.items():
    #         # Check if the branch is not tested
    #         if not branch_info['tested']:
    #             branch_info['tested'] = True
    #             print(f"Branch '{branch}' under '{pipe}' is not tested.")
    #             return branch_info['pipes'][0]
        # found_not_tested_branch = False
    # Iterate over the main dictionary
def next_branches_not_tested(branches_df:pd.DataFrame)->str:
    not_tested_branches = branches_df[~branches_df['Tested']]
    if not not_tested_branches.empty:
        next_pipe = not_tested_branches.iloc[0]['Pipes'][0]
        branch_num = not_tested_branches.iloc[0]['Branch']
        # branches_df.at[not_tested_branches.index[0], 'Tested'] = True
        branches_df.loc[(branches_df['Pipe'] == not_tested_branches.index[0]) & (branches_df['Branch'] == branch_num), 'Tested'] = True
        return next_pipe
    else:
        return None

def reset_branches_tested_values(branches_df):
    branches_df['Tested'] = False  

# def add_pressure_at_end_of_pipe(pipes_table:pd.DataFrame) -> float:
#         #adding Pressure at end of pipe (Again, 1 pump only!!)

#         pump_name = 'Pump 1'  

#         print(pipes_table['total head loss'])
#         input('press any key')

#         system_total_headloss = pipes_table['total head loss'].sum()
#         current_pipe = pipes_table[pipes_table['start with'] == pump_name]['pipe #'].values[0]
#         next_pipe = pipes_table[pipes_table['start with'] == pump_name]['end with'].values[0]
#         minimum_pressure = 0
        
#         pressure = system_total_headloss-float(pipes_table.loc[current_pipe,'total head loss'])
#         pipes_table.loc[current_pipe,'Pressure at end of pipe'] = pressure
#         if pressure < pipes_table.loc[current_pipe,'minimum pressure required']:
#             minimum_pressure = pressure - current_pipe

#         try:
#             for i in range (1,len(pipes_table.index)):
                
#                 pressure = pressure-float(pipes_table.loc[next_pipe,'total head loss'])
#                 pipes_table.loc[next_pipe,'Pressure at end of pipe'] = pressure
#                 if pressure < pipes_table.loc[next_pipe,'minimum pressure required']:
#                     delta = pressure - pipes_table.loc[next_pipe,'minimum pressure required']
#                     minimum_pressure = min(minimum_pressure,delta)

#                 # pipes_table.loc[next_pipe,'Pressure at end of pipe'] = float(pipes_table.loc[current_pipe]['Pressure at end of pipe'])-float(pipes_table.loc[next_pipe,'total head loss'])
#                 current_pipe = next_pipe
#                 next_pipe = pipes_table[pipes_table['pipe #'] == current_pipe]['end with'].values[0]
                
#         except Exception as e:
#             print("The error is: ",e)
#             print(f''' ################################################################
#                 i={i}
#                 prev_pipe = {current_pipe};
#                 next_pipe = {next_pipe};
#                 pipes_table.loc[prev_pipe]['Pressure at end of pipe'] = {pipes_table.loc[current_pipe]['Pressure at end of pipe']};
#                 ''')
#             input("press any key: ")

#         if pipes_table['Pressure at end of pipe'].min() < minimum_pressure:
#             minimum_pressure = pipes_table[pipes_table['Pressure at end of pipe'] < minimum_pressure]['Pressure at end of pipe'].min()
#         pipes_table['Pressure at end of pipe'] = pipes_table['Pressure at end of pipe'] - minimum_pressure
        
#         return minimum_pressure
def add_pressure_at_end_of_pipe(pipes_table:pd.DataFrame,branches_df:pd.DataFrame) -> float:
        #adding Pressure at end of pipe (Again, 1 pump only!!)

        pump_name = 'Pump 1'  

        print(pipes_table['total head loss'])
        input('press any key')

        system_total_headloss = pipes_table['total head loss'].sum()
        current_pipe = pipes_table[pipes_table['start with'] == pump_name]['pipe #'].values[0]
        next_pipe = pipes_table[pipes_table['start with'] == pump_name]['end with'].values[0]
        minimum_pressure = 0
        
        pressure = system_total_headloss-float(pipes_table.loc[current_pipe,'total head loss'])
        pipes_table.loc[current_pipe,'Pressure at end of pipe'] = pressure
        if pressure < pipes_table.loc[current_pipe,'minimum pressure required']:
            minimum_pressure = pressure - current_pipe

        try:
            for i in range (1,len(pipes_table.index)):
                
                pressure = pressure-float(pipes_table.loc[next_pipe,'total head loss'])
                pipes_table.loc[next_pipe,'Pressure at end of pipe'] = pressure
                if pressure < pipes_table.loc[next_pipe,'minimum pressure required']:
                    delta = pressure - pipes_table.loc[next_pipe,'minimum pressure required']
                    minimum_pressure = min(minimum_pressure,delta)

                # pipes_table.loc[next_pipe,'Pressure at end of pipe'] = float(pipes_table.loc[current_pipe]['Pressure at end of pipe'])-float(pipes_table.loc[next_pipe,'total head loss'])
                current_pipe = next_pipe
                if (current_pipe in branches_df.index) or (pipes_table['end with'][current_pipe] == ""):
                    next_pipe = next_branches_not_tested(branches_df)
                else:
                    next_pipe = pipes_table[pipes_table['pipe #'] == current_pipe]['end with'].values[0]
            reset_branches_tested_values(branches_df)
        except Exception as e:
            print("The error is: ",e)
            print(f''' ##########################ADD PRESSURE#############################
                i={i}
                prev_pipe = {current_pipe};
                next_pipe = {next_pipe};
                pipes_table.loc[prev_pipe]['Pressure at end of pipe'] = {pipes_table.loc[current_pipe]['Pressure at end of pipe']};
                ''')
            input("press any key: ")

        if pipes_table['Pressure at end of pipe'].min() < minimum_pressure:
            minimum_pressure = pipes_table[pipes_table['Pressure at end of pipe'] < minimum_pressure]['Pressure at end of pipe'].min()
        pipes_table['Pressure at end of pipe'] = pipes_table['Pressure at end of pipe'] - minimum_pressure
        
        return minimum_pressure

def make_branches_df(pipes_table: pd.DataFrame):
    junctions_list = list(pipes_table[pipes_table['end with'].str.contains(',', na=False)]['pipe #'])
    data = []

    for junction in junctions_list:
        branched_pipes = pipes_table['end with'][junction].split(', ')
        for i, pipe in enumerate(branched_pipes):
            branch_id = f'Branch {i+1}'
            new_pipe = pipe
            branch_pipes = []
            branch_consumption = 0
            while pipes_table['end with'][new_pipe] != '':
                branch_consumption += pipes_table['consumption'][new_pipe]
                branch_pipes.append(str(new_pipe))
                new_pipe = pipes_table['end with'][new_pipe]
            branch_consumption += pipes_table['consumption'][new_pipe]
            branch_pipes.append(str(new_pipe))

            pipes_table['flow'][branch_pipes[0]] = branch_consumption
            data.append((junction, branch_id, branch_pipes, branch_consumption, False))

    branches_df = pd.DataFrame(data, columns=['Pipe', 'Branch', 'Pipes', 'Branch Consumption', 'Tested'])
    branches_df.set_index(branches_df['Pipe'],inplace=True)
    print(branches_df)
    return branches_df
    # junctions_list= list(pipes_table[pipes_table['end with'].str.contains(',', na=False)]['pipe #'])
    # branches_tree = {}
    # for junction in junctions_list:
    #     branched_pipes = pipes_table['end with'][junction].split(', ')
    #     branches_tree[junction] = {}
    #     for i,pipe in enumerate(branched_pipes):
    #         branch_id = f'Branch {i+1}'
    #         new_pipe=pipe
    #         branch_pipes = []
    #         branch_consumption = 0
    #         while pipes_table['end with'][new_pipe] != '':
    #             branch_consumption += pipes_table['consumption'][new_pipe]
    #             branch_pipes.append(str(new_pipe))
    #             new_pipe= pipes_table['end with'][new_pipe]
    #         branch_consumption += pipes_table['consumption'][new_pipe]
    #         branch_pipes.append(str(new_pipe))
        
    #         pipes_table['flow'][[branch_pipes][0][0]]= branch_consumption
    #         branch_dict = {
    #             'pipes' : branch_pipes,
    #             'branch_consumption' : branch_consumption,
    #             'tested': False,
    #         }

    #         branches_tree[junction][branch_id] = branch_dict
    
    # branches_df = pd.DataFrame(branches_tree)
    # branches_df.set_index(branches_df[junction],inplace=True)
    # pprint(branches_df)
    # return pd.DataFrame(branches_tree)

def branched_network(pipes_table: pd.DataFrame,pumps_table: pd.DataFrame):

    branches_df = make_branches_df(pipes_table)
    # junctions_list= list(pipes_table[pipes_table['end with'].str.contains(',', na=False)]['pipe #'])
    # branches_tree = {}
    # for junction in junctions_list:
    #     branched_pipes = pipes_table['end with'][junction].split(', ')
    #     branches_tree[junction] = {}
    #     for i,pipe in enumerate(branched_pipes):
    #         branch_id = f'Branch {i+1}'
    #         new_pipe=pipe
    #         branch_pipes = []
    #         branch_consumption = 0
    #         while pipes_table['end with'][new_pipe] != '':
    #             branch_consumption += pipes_table['consumption'][new_pipe]
    #             branch_pipes.append(str(new_pipe))
    #             new_pipe= pipes_table['end with'][new_pipe]
    #         branch_consumption += pipes_table['consumption'][new_pipe]
    #         branch_pipes.append(str(new_pipe))
        
    #         pipes_table['flow'][[branch_pipes][0][0]]= branch_consumption
    #         branch_dict = {
    #             'pipes' : branch_pipes,
    #             'branch_consumption' : branch_consumption,
    #             'tested': False,
    #         }

    #         branches_tree[junction][branch_id] = branch_dict
    # branches_df = pd.DataFrame(branches_tree)

    #start solve the network: begin with pump data:
    ###  Pump data  ###
    pump_number = pumps_table['pump #'][0]
    pump_flow = pipes_table['consumption'].sum()  
    pumps_table['flow'][pump_number] = pump_flow
    pump1 = entities.Pump(rated_flow=pump_flow)

    previous_pipe_number = 0

    for pipe in range(0,len(pipes_table.index)):

        # branch_index = 1
        if pipe == 0:
            new_pipe_number = pipes_table[pipes_table['start with'] == pump_number]['end with'].index[0]
            flow_rate = pump_flow
        elif (previous_pipe_number in branches_df.index) or (pipes_table['end with'][previous_pipe_number] == ""):
            new_pipe_number = next_branches_not_tested(branches_df)
            print(new_pipe_number)
            flow_rate = pipes_table['flow'][new_pipe_number]

        else:
            new_pipe_number = pipes_table['end with'][previous_pipe_number]
            flow_in = float(pipes_table['flow'][previous_pipe_number])
            consumption = float(pipes_table['consumption'][previous_pipe_number])
            flow_rate = flow_in - consumption
            
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
    reset_branches_tested_values(branches_df)
    minimum_pressure = add_pressure_at_end_of_pipe(pipes_table,branches_df)

   ### Again some pumps data:
    
    
    start_num = 8
    pump_efficiency = pumps_table['efficiency'][pump_number] 
    pump_head = pipes_table['total head loss'].sum() - minimum_pressure
    pump_power = pump1.power(pump_flow,pump_head,pump_efficiency)
    
    pumps_table['head'][pump_number] = pump_head
    pumps_table['power'][pump_number] = pump_power
    pumps_table['wetpit min volume'][pump_number] = pump1.min_wet_pit(pump_flow,start_num)
    pumps_table['start num'][pump_number] = start_num
    
    #adding Pressure at end of pipe (Again, 1 pump only!!)
    # print(pipes_table['Pressure at end of pipe'])
    # print(f'''pump_head = {pump_head}''')
    # input("press any key: ")

    current_pipe = pipes_table[pipes_table['start with'] == 'Pump 1']['pipe #'].values[0]
    next_pipe = pipes_table[pipes_table['start with'] == 'Pump 1']['end with'].values[0]
    pipes_table.loc[current_pipe,'Pressure at end of pipe'] = pumps_table.loc['Pump 1','head']-float(pipes_table.loc[current_pipe,'total head loss'])

    try:
        for i in range (1,len(pipes_table.index)):
            pipes_table.loc[next_pipe,'Pressure at end of pipe'] = float(pipes_table.loc[current_pipe]['Pressure at end of pipe'])-float(pipes_table.loc[next_pipe,'total head loss'])
            
            current_pipe = next_pipe
            if (current_pipe in branches_df.index) or (pipes_table['end with'][current_pipe] == ""):
                next_pipe = next_branches_not_tested(branches_df)
            else:
                next_pipe = pipes_table[pipes_table['pipe #'] == current_pipe]['end with'].values[0]
        reset_branches_tested_values(branches_df)
        print(pipes_table['Pressure at end of pipe'])
        input("press any key: ")

    except Exception as e:
        print("The error is: ",e)
        print(f''' #########################SET PRESSURE#######################################
              i={i}
              prev_pipe = {current_pipe};
              next_pipe = {next_pipe};
              pipes_table.loc[prev_pipe]['Pressure at end of pipe'] = {pipes_table.loc[current_pipe]['Pressure at end of pipe']};
              ''')
        input("press any key: ")
    


def simple_network(pipes_table: pd.DataFrame,pumps_table: pd.DataFrame):
    
    '''
    A single pump is responsible for discharging water through a lengthy pipeline composed of various sections, 
    each with its unique pipe type and diameter.
    At the end of each section, 
    there is a consumer that draws water from it.
    '''

    ###  Pump data  ###
    
    pump_number = pumps_table['pump #'][0]
    pump_flow = pipes_table['consumption'].sum()  
    pumps_table['flow'][pump_number] = pump_flow
    pump1 = entities.Pump(rated_flow=pump_flow)

    ### Pipes data ###

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
    
    minimum_pressure = add_pressure_at_end_of_pipe(pipes_table)
    
    ### Again some pumps data:
    
    
    start_num = 8
    pump_efficiency = pumps_table['efficiency'][pump_number] 
    pump_head = pipes_table['total head loss'].sum() - minimum_pressure
    pump_power = pump1.power(pump_flow,pump_head,pump_efficiency)
    
    pumps_table['head'][pump_number] = pump_head
    pumps_table['power'][pump_number] = pump_power
    pumps_table['wetpit min volume'][pump_number] = pump1.min_wet_pit(pump_flow,start_num)
    pumps_table['start num'][pump_number] = start_num
    
    #adding Pressure at end of pipe (Again, 1 pump only!!)
    # print(pipes_table['Pressure at end of pipe'])
    # print(f'''pump_head = {pump_head}''')
    # input("press any key: ")

    current_pipe = pipes_table[pipes_table['start with'] == 'Pump 1']['pipe #'].values[0]
    next_pipe = pipes_table[pipes_table['start with'] == 'Pump 1']['end with'].values[0]
    pipes_table.loc[current_pipe,'Pressure at end of pipe'] = pumps_table.loc['Pump 1','head']-float(pipes_table.loc[current_pipe,'total head loss'])

    try:
        for i in range (1,len(pipes_table.index)):
            pipes_table.loc[next_pipe,'Pressure at end of pipe'] = float(pipes_table.loc[current_pipe]['Pressure at end of pipe'])-float(pipes_table.loc[next_pipe,'total head loss'])

            current_pipe = next_pipe
            next_pipe = pipes_table[pipes_table['pipe #'] == current_pipe]['end with'].values[0]
        print(pipes_table['Pressure at end of pipe'])
        input("press any key: ")

    except Exception as e:
        print("The error is: ",e)
        print(f''' ################################################################
              i={i}
              prev_pipe = {current_pipe};
              next_pipe = {next_pipe};
              pipes_table.loc[prev_pipe]['Pressure at end of pipe'] = {pipes_table.loc[current_pipe]['Pressure at end of pipe']};
              ''')
        input("press any key: ")
    


def pipes_from_flow_and_velocity (eco_pipes_table: pd.DataFrame, eco_pumps_table: pd.DataFrame, des_velocity=2.5):

    branches_df = make_branches_df(eco_pipes_table)
    for i in range(len(eco_pipes_table)):
        pipetype = eco_pipes_table['pipe type'][i]
        flow = eco_pipes_table['flow'][i]
        print(f'pipe # {i+1} {flow}')
        length = eco_pipes_table['length (m)'][i]
        static_head = eco_pipes_table['static head (endZ-startZ)'][i]

        pipe1 = entities.Pipe(pipetype=pipetype,flow_rate=flow,length=length,static_head=static_head)

        # print(f'\n\n\n\n #######################################\n{pipe1.flow_rate}\n\n\n')

        pipe1.nominal_dia, pipe1.inside_dia, min_wt = pipe1.select_pipe_dia_from_velocity(des_velocity)
        
        velocity = pipe1.velocity()
        head_loss = pipe1.major_head_loss()
        total_headloss = pipe1.total_head_loss()

        pipes_type_table = entities.pipes_type_dict[pipetype]
        costs_per_meter = pipes_type_table[pipes_type_table['ND'] == pipe1.nominal_dia]['prices'].values[0]
        total_costs = costs_per_meter*length

        eco_pipes_table['velocity'][i] = velocity
        eco_pipes_table['head loss'][i] = head_loss
        eco_pipes_table['total head loss'][i] = total_headloss
        eco_pipes_table['nominal dia'][i] = pipe1.nominal_dia
        eco_pipes_table['id (mm)'][i] = pipe1.inside_dia
        eco_pipes_table['costs per meter'][i] = costs_per_meter
        eco_pipes_table['total costs'][i] = total_costs        

    
    minimum_pressure = add_pressure_at_end_of_pipe(eco_pipes_table,branches_df)

    ### Again some pumps data:
    for pump_number in range(len(eco_pumps_table)):
        
        flow = eco_pumps_table['flow'][pump_number]
        pump_efficiency = eco_pumps_table['efficiency'][pump_number] 
        pump_head = eco_pipes_table['total head loss'].sum() - minimum_pressure
        pump = entities.Pump(rated_flow=flow,rated_head=pump_head)
        pump_power = pump.power(pump.rated_flow,pump_head,pump_efficiency)

        eco_pumps_table['head'][pump_number] = pump_head
        eco_pumps_table['power'][pump_number] = pump_power

    # return eco_pump_table, eco_pipe_table
        