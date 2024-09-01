# practice to name the main file as main.py
# .py for the logic
# .kv is the better way to create the GUI (not in python language)
# to orgnaise a .json file press Alt + Shift + F
''' 
# kivy hirchy:
    App (MainApp)
        ScreenManager(RootWidget)
            Screen(Logininscreen)
'''
import os, sys
import pandas as pd

from kivy.resources import resource_add_path, resource_find
from fileinput import filename
from random import random
# from zoneinfo import available_timezones
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
# import json , glob, random
from datetime import datetime
from pathlib import Path

from utils.autocad.analyzing.sort_objects import sort_objects
# import eq

sys.path.insert(1,os.getcwd())
from utils import eq
from utils import useful_functions as usf
from entities import entities
from utils.autocad import autocad_functions,pipes_network_sytems,autocad_analyzing
from utils.autocad.autocad_analyzing import acad
from utils.autocad.add_objects.add_text import add_text_to_dwg


Builder.load_file('design.kv')
pipes_table = pd.DataFrame()
pumps_table = pd.DataFrame()
channels_table = pd.DataFrame()
eco_pipes_table = pipes_table.copy()
eco_pumps_table = pumps_table.copy()

class WidgetScreen(Screen):
    pass

class WelcomeScreen(Screen):
    pass

class AddElemntsWidget(Screen):
    
    new_pipe = entities.Pipe()
    nominal_dia_list = ["Please chosse pipe type:"]

    def pipe_spinner_clicked(self, value):


        # if value == 'Steel':
        #     self.ids.units.text = '"\n'
        # else:
        #     self.ids.units.text = 'mm\n'
        self.new_pipe.pipetype = value
        print(value)
        # diameter_table = self.new_pipe.pipe_diameter_table(value)
        diameter_table = usf.pipe_diameter_table(value)
        # print(diameter_table)
        self.ids.nominal_dia_spinner.values = diameter_table

    def pipe_validation(self,pipetype:str, nominal_diameter:str, consumption='0', min_pressure='0')->bool:
        error_message = ""

        if (pipetype not in entities.pipes_type_dict.keys()):
            error_message += "Pipe type is not supported! "
        elif nominal_diameter not in self.ids.nominal_dia_spinner.values:
            error_message += "Nominal diameter is not supported! "
        error_message += usf.is_float_message(string=consumption, name='Consumption')
        error_message += usf.is_float_message(string=min_pressure, name='Min pressure')
        if error_message != "":
            self.ids.pipe_error_message.text = error_message
            return False
        return True
    
    def pump_validation(self,efficiency:str, starts_per_hour:str)->bool:
        error_message = ""

        if efficiency != "":
            error_message += usf.is_float_message(string=efficiency, name='Efficiency')
        if starts_per_hour != "":
            error_message += usf.is_float_message(string=starts_per_hour, name='Starts per hour')

        if error_message != "":
            self.ids.pump_error_message.text = error_message
            return False
        return True

    def create_a_pipe(self,pipetype:str,nominal_diameter:str,consumption='0',min_pressure='0'):

        if not self.pipe_validation(pipetype,nominal_diameter,consumption,min_pressure):
            return
          
        autocad_functions.make_a_pipe_from_app(pipetype,nominal_diameter,consumption,min_pressure)

    def draw_a_pipe(self,pipetype,nominal_diameter, start_elv,end_elv,consumption='0',min_pressure='0'):
        if not self.pipe_validation(pipetype,nominal_diameter,consumption,min_pressure):
            return
        
        autocad_functions.draw_a_pipe_from_app(pipetype,nominal_diameter,consumption,start_elv,end_elv,min_pressure)

    def create_a_pump(self, efficiency:str, starts_per_hour:str):

        if not self.pump_validation(efficiency, starts_per_hour):
            return        
        autocad_functions.make_a_pump_from_app(efficiency, starts_per_hour)

class NetworkWidget(Screen):

    
    def make_a_sec(self, x_steps=500, y_steps=5):
        print(pipes_table)
        min_x,max_x,min_y,max_y = autocad_analyzing.make_a_sec_grid(pipes_table,x_steps,y_steps)
        autocad_analyzing.draw_pipe_sec(pipes_table,min_y,max_y)

    def calculate_the_network(self):
        
        # global pipes_table
        # global pumps_table
        # global channels_table

        # pipes_table, pumps_table, channels_table = autocad_analyzing.dwg_objects_sorting()
        pipes_table, pumps_table, channels_table = sort_objects()
        autocad_analyzing.is_pipe_conected(pipes_table,pumps_table)

        if not pipes_table.empty: 
            pipes_network_sytems.branched_network(pipes_table,pumps_table)
            # pipes_network_sytems.simple_network(pipes_table,pumps_table)
        add_text_to_dwg(pipes_table,pumps_table, channels_table)
        
        # self.make_a_sec()

    def calculate_with_max_velocity(self,velocity):
        
        if velocity == '':
            velocity = '2.5'

        global eco_pipes_table
        global eco_pumps_table

        try:
            eco_pipes_table, eco_pumps_table, channels_table = autocad_analyzing.dwg_objects_sorting()
            autocad_analyzing.is_pipe_conected(eco_pipes_table,eco_pumps_table)
            pipes_network_sytems.branched_network(eco_pipes_table,eco_pumps_table) #Need diffrent func
            pipes_network_sytems.pipes_from_flow_and_velocity (eco_pipes_table, eco_pumps_table, float(velocity))
            add_text_to_dwg(eco_pipes_table,eco_pumps_table,channels_table)
        except Exception as e:
            print (f'error: {e}')


    def save_to_excel(self):
        try:
            with pd.ExcelWriter('data\\outputs\\acad-pipelines.xlsx') as writer:

                pipes_table.to_excel(writer,sheet_name='Pipes',index=False)
                
                pumps_table.to_excel(writer,sheet_name='Pumps',index=False)

                eco_pipes_table.to_excel(writer,sheet_name='eco Pipes',index=False)
                
                eco_pumps_table.to_excel(writer,sheet_name='eco Pumps',index=False)

                channels_table.to_excel(writer,sheet_name='Channels',index=False)
            
            os.startfile('data\\outputs\\acad-pipelines.xlsx')
        except Exception as e:
            print(e)
        # print('file saved')

    # def open_calculator(self):
    #     os.startfile('C:\\Users\\avner\\google drive\\Python\\Apps\\Avner water app1\\app v 0.00\\desktop app\\main.py')
    #     # sys.path.insert(1,os.getcwd())



class RootWidget(ScreenManager): # Have to name it just like the .kv <>
    pass

# class ImageButton(ButtonBehavior, HoverBehavior, Image): # ButtonBehavior Goes first
#     pass

class MainApp(App):
    
    def build(self):
        return RootWidget() # Make sure we use ()

if __name__=='__main__':
    
    #######################################################
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    MainApp().run()
    ########################################################

    # pipes_table = pd.DataFrame()
    # pumps_table = pd.DataFrame()
    # channels_table = pd.DataFrame()
    # eco_pipes_table = pipes_table.copy()
    # eco_pumps_table = pumps_table.copy()

    # def calculate_the_network():
        
    #     global pipes_table
    #     global pumps_table
    #     global channels_table

    #     pipes_table, pumps_table, channels_table = autocad_analyzing.dwg_objects_sorting()
    #     autocad_analyzing.is_pipe_conected(pipes_table,pumps_table)
    #     if not pipes_table.empty: 
    #         pipes_network_sytems.simple_network(pipes_table,pumps_table)
    #     autocad_analyzing.add_text_to_dwg(pipes_table,pumps_table, channels_table)
    
    # calculate_the_network()