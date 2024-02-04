import sys
import os
import pandas as pd
sys.path.insert(1,os.getcwd())
from entities import entities

def simple_network(pipes_table,pumps_table):
    
    '''
    one pump, discharge for 1 long pipe 
    that is made from serise of pipes 
    ech with his own pipe type, dia.
    at the end of ecth pipe there is a consumer that
    take some of the water.
    '''

    ###  Pump data  ###
    
    pump_number = pumps_table['pump #'][0]
    cnt = 0
    pump_flow = pipes_table['consumption'].sum()  
    # print(f'pump_flow = {pump_flow}')
    pumps_table['flow'][pump_number] = pump_flow
    pump1 = entities.Pump(rated_flow=pump_flow)

    ### Pipes data ###

    previous_pipe_number = 0


    for pipe in range(len(pipes_table.index)):

        if pipe == 0:
            new_pipe_number = pipes_table[pipes_table['start with'] == pump_number]['end with'].index[0]
            flow_rate = pump_flow
            
        else:
            new_pipe_number = pipes_table['end with'][previous_pipe_number]
            flow_in = float(pipes_table['flow'][previous_pipe_number])
            consumption = float(pipes_table['consumption'][previous_pipe_number])
            flow_rate = flow_in - consumption
            

        # print(new_pipe_number)
        # previous_pipe_number = new_pipe_number
        new_pipe = pipes_table[pipes_table['pipe #'] == new_pipe_number]

        pipetype = pipes_table['pipe type'][new_pipe_number]
        nominal_dia = pipes_table['nominal dia'][new_pipe_number]
        inside_dia = pipes_table['id (mm)'][new_pipe_number]
        length = pipes_table['length (m)'][new_pipe_number]
        static_head = pipes_table['static head (endZ-startZ)'][new_pipe_number]

        # print (pipetype, ' ', nominal_dia, ' ', inside_dia, ' ', length, ' ', static_head, ' ', flow_rate)
    
        pipe1 = entities.Pipe(pipetype=pipetype,nominal_dia=nominal_dia,inside_dia=inside_dia,length=length,static_head=static_head,flow_rate=flow_rate)

        velocity = pipe1.velocity()
        head_loss = pipe1.major_head_loss()
        total_headloss = pipe1.total_head_loss()
        # print(velocity, '', head loss, '', total_headloss)

        pipes_table['flow'][new_pipe_number] = flow_rate 
        pipes_table['velocity'][new_pipe_number] = velocity
        pipes_table['head loss'][new_pipe_number] = head_loss
        pipes_table['total head loss'][new_pipe_number] = total_headloss

        previous_pipe_number = new_pipe_number
        # print ('\n\n\n')

    ### Again some pumps data:
    pump_efficiency = pumps_table['efficiency'][pump_number] 
    pump_head = pipes_table['total head loss'].sum()
    pump_power = pump1.power(pump_flow,pump_head,pump_efficiency)

    start_num = 8

    pumps_table['head'][pump_number] = pump_head
    pumps_table['power'][pump_number] = pump_power
    pumps_table['wetpit min volume'][pump_number] = pump1.min_wet_pit(pump_flow,start_num)
    pumps_table['start num'][pump_number] = start_num

def pipes_from_flow_and_velocity (eco_pipes_table, eco_pumps_table, des_velocity):

    for i in range(len(eco_pipes_table)):
        pipetype = eco_pipes_table['pipe type'][i]
        flow = eco_pipes_table['flow'][i]
        length = eco_pipes_table['length (m)'][i]
        static_head = eco_pipes_table['static head (endZ-startZ)'][i]

        pipe1 = entities.Pipe(pipetype=pipetype,flow_rate=flow,length=length,static_head=static_head)
        pipe1.nominal_dia, pipe1.inside_dia, min_wt = pipe1.select_pipe_dia_from_velocity(des_velocity)
        
        velocity = pipe1.velocity()
        head_loss = pipe1.major_head_loss()
        total_headloss = pipe1.total_head_loss()

        pipes_type_table = pd.read_excel('data\\info\\pipes.xlsx',sheet_name=pipetype)
        costs_per_meter = pipes_type_table[pipes_type_table['ND'] == pipe1.nominal_dia]['prices'].values[0]
        total_costs = costs_per_meter*length

        eco_pipes_table['velocity'][i] = velocity
        eco_pipes_table['head loss'][i] = head_loss
        eco_pipes_table['total head loss'][i] = total_headloss
        eco_pipes_table['nominal dia'][i] = pipe1.nominal_dia
        eco_pipes_table['id (mm)'][i] = pipe1.inside_dia
        eco_pipes_table['costs per meter'][i] = costs_per_meter
        eco_pipes_table['total costs'][i] = total_costs        

    ### Again some pumps data:
    for pump_number in range(len(eco_pumps_table)):
        
        flow = eco_pumps_table['flow'][pump_number]
        pump_efficiency = eco_pumps_table['efficiency'][pump_number] 
        pump_head = eco_pipes_table['total head loss'].sum()
        pump = entities.Pump(rated_flow=flow,rated_head=pump_head)
        pump_power = pump.power(pump.rated_flow,pump_head,pump_efficiency)

        eco_pumps_table['head'][pump_number] = pump_head
        eco_pumps_table['power'][pump_number] = pump_power

    # return eco_pump_table, eco_pipe_table
        