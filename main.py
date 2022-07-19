# it's a good practice to name the main file as main.py
# .py for the logic
# .kv is the better way to create the GUI (not in python language)
# to orgnaise a .json file press Alt + Shift + F
''' 
# kivy hirchy:
    App (MainApp)
        ScreenManager(RootWidget)
            Screen(Logininscreen)
'''

from fileinput import filename
from random import random
# from zoneinfo import available_timezones
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import json , glob, random
from datetime import datetime
from pathlib import Path

from numpy import void
# from hoverable import HoverBehavior
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from entities import entities



pipes_list = []
Builder.load_file('design.kv')



class WidgetScreen(Screen):
    pass

################################# Pumps #############################

class PumpPowerWidget(Screen):
    
    def pumpower(self,flow_rate, pump_head, pump_eff):
        
        new_pump = entities.Pump()

        if (flow_rate == "" or flow_rate == 0) and (pump_head == "" or pump_head  == 0):
            self.ids.pump_power.color = 1,0,0,1
            self.ids.pump_power.text = "Please enter flow rate and pump head"
            return            
        if flow_rate == "" or flow_rate == 0:
            self.ids.pump_power.color = 1,0,0,1
            self.ids.pump_power.text = "Please enter flow rate"
            return
        if pump_head == "" or pump_head == 0:
            self.ids.pump_power.color = 1,0,0,1
            self.ids.pump_power.text = "Please enter pump head"
            return 
        if pump_eff == "":
            pump_eff = '1'

        if float(pump_eff) > 1:
            pump_eff = float(pump_eff)/100

        pump_power = str(round(new_pump.power(float(flow_rate),float(pump_head),float(pump_eff)),2))
        
        self.ids.pump_power.color = 1,1,1,1
        self.ids.pump_power.text = f'This pump use approximately {pump_power} Kw'

    def pipes(self):
        self.manager.current = 'pipes_screen'

    def pumps(self):
        self.manager.current = 'pumps_screen'      

class WetPitWidget(Screen):
    
    def wetpit_volume(self,flow_rate, starts_num):
        
        new_pump = entities.Pump()

        if (flow_rate == "" or flow_rate == 0) and (starts_num == "" or starts_num  == 0):
            self.ids.volume.color = 1,0,0,1
            self.ids.volume.text = "Please enter flow rate and operations"
            return            
        if flow_rate == "" or flow_rate == 0:
            self.ids.volume.color = 1,0,0,1
            self.ids.volume.text = "Please enter flow rate"
            return
        if starts_num == "" or flow_rate == 0:
            self.ids.volume.color = 1,0,0,1
            self.ids.volume.text = "Please enter operations"
            return 

        volume = str(round(new_pump.power(float(flow_rate),float(starts_num)),2))
        
        self.ids.volume.color = 1,1,1,1
        self.ids.volume.text = f'The minimum wetpit volume {volume} m\u00B3'

    def pipes(self):
        self.manager.current = 'pipes_screen'

    def pumps(self):
        self.manager.current = 'pumps_screen'     

################################# Pipes #############################

class DiameterFromPipe(Screen):
    
    new_pipe = entities.Pipe()
    nominal_dia_list = ["Please chosse pipe type:"]

    def pipe_spinner_clicked(self, value):
        if value == 'Steel':
            self.ids.units.text = '"\n'
        else:
            self.ids.units.text = 'mm\n'
        self.new_pipe.pipetype = value
        self.ids.nominal_dia_spinner.values = self.new_pipe.pipe_diameter_table()
        # self.new_pipe.pipetype = value
        self.ids.inside_diameter.text = ""
        self.ids.inside_diameter.color = 1,1,1
        self.ids.idunits.text = ""
        print(self.nominal_dia_list)

    async def find_diameter(self,nominal_diameter,pipe_type):
        
        def init_inside_testicles():
            self.ids.inside_diameter.text = ""
            self.ids.inside_diameter.color = 1,1,1
            self.ids.idunits.text = ""

        def get_butthole_condition():
            if nominal_diameter == '' or nominal_diameter == 0:
                self.ids.inside_diameter.text = "Please enter Nominal diameter"
                self.ids.inside_diameter.color = 1,0,0
                return
            elif pipe_type == "Pipe type:":
                self.ids.inside_diameter.text = "Please enter Pipe type"
                self.ids.inside_diameter.color = 1,0,0
                return

        await init_inside_testicles()
        get_butthole_condition()

        # print(pipe_type)
        self.new_pipe.pipetype = pipe_type
        self.new_pipe.inside_dia = self.new_pipe.inside_dia_from_nominal(float(nominal_diameter))
        self.ids.inside_diameter.text = str(self.new_pipe.inside_dia)
        self.ids.idunits.text = "mm"
        return

    def pipes(self):
        self.manager.current = 'pipes_screen'

    def pumps(self):
        self.manager.current = 'pumps_screen'  

    
class PipeFromVelocity(Screen):
    
    
    def find_diameter(self,flow_rate, max_velocity, pipe_type):
        
        self.ids.nominal_diameter.text = ""
        self.ids.inside_diameter.text = ""
        self.ids.real_velocity.text = ""
        self.ids.error_massage.text = ""
        self.ids.wall_tickness_txt.text = ""
        self.ids.wall_tickness_value.text = ''
        self.ids.head_loss.text = ""
        self.ids.cw.text = ""

        if (flow_rate == "" or flow_rate == 0) and (max_velocity == "" or flow_rate == 0):
            self.ids.error_massage.text = "Please enter flow rate and velocity"
            return            
        if flow_rate == "" or flow_rate == 0:
            self.ids.error_massage.text = "Please enter flow rate"
            return
        if max_velocity == "" or flow_rate == 0:
            self.ids.error_massage.text = "Please enter velocity"
            return
        if pipe_type == "Pipe type:" or pipe_type == "":
            self.ids.error_massage.text = "Please enter pipe type"
            return
        
        new_pipe = entities.Pipe(pipetype=pipe_type,flow_rate=float(flow_rate),length=1000)
        nd, id ,wt = new_pipe.select_pipe_dia_from_velocity(float(max_velocity))
        if pipe_type == "Steel":
            ndunits = ' "'
        else:
            ndunits = ' mm'

        self.ids.nominal_diameter.text = str(nd) + ndunits
        self.ids.inside_diameter.text = str(round(id,1)) + ' mm'
        new_pipe.inside_dia = id/1000
        self.ids.real_velocity.text = str(new_pipe.velocity()) + ' m/s'
        if pipe_type == 'Steel':
            self.ids.wall_tickness_txt.text = "Wall Thickness:"
            self.ids.wall_tickness_value.text = str(wt) + ' mm'
            

            if nd < 12 :
                new_pipe.cw = 110
            elif nd == 12:
                new_pipe.cw = 120
            elif nd < 18:
                new_pipe.cw = 125
            elif nd < 30:
                new_pipe.cw = 130
            elif nd < 44:
                new_pipe.cw = 135
            elif nd < 60:
                new_pipe.cw = 140
            elif nd < 90:
                new_pipe.cw = 145
            else:
                new_pipe.cw = 150

            new_pipe1 = new_pipe


        else:
            # self.ids.units.text = 'mm'
            if nd < 225 :
                new_pipe.cw = 110
            elif nd == 225:
                new_pipe.cw = 120
            elif nd < 355:
                new_pipe.cw = 125
            elif nd < 560:
                new_pipe.cw = 130
            elif nd < 900:
                new_pipe.cw = 135
            elif nd < 1200:
                new_pipe.cw = 140
            # elif nd < 90:
            #     new_pipe.cw = 145
            # else:
            #     new_pipe.cw = 150

        self.ids.head_loss.text = str(round(new_pipe.major_head_loss(),2)) + ' m/km'
        self.ids.cw.text = str(new_pipe.cw)

    def pipes(self):
        self.manager.current = 'pipes_screen'

    def pumps(self):
        self.manager.current = 'pumps_screen'  

        

class PipeHeadLossScreen(Screen):
    
    new_pipe = entities.Pipe()
    
    def pipeheadloss(self,flow_rate_n,dia_n,length_n,cw_n,minor,elevation):

        print(1)
        self.ids.error_massage.text = ""

        if flow_rate_n == "" or flow_rate_n == 0:
            self.ids.error_massage.text = "Please enter flow rate"
            print(2)
            return
        if dia_n == "" or dia_n == 0:
            self.ids.error_massage.text = "Please enter diamter"
            return
        if length_n == "":
            self.ids.error_massage.text = "Please enter pipe length"
            return
        if cw_n == "":
            self.ids.error_massage.text = "Please enter pipe Cw"
            return

        if minor == "":
            minor = float(0)

        if elevation == "":
            elevation = float(0)
        
        new_pipe = entities.Pipe(inside_dia=float(dia_n)/1000,length=float(length_n),flow_rate=float(flow_rate_n),cw=float(cw_n),minor_headloss=minor,static_head=elevation)
        
        self.ids.total_head_loss.text = str(new_pipe.total_head_loss()) + ' m'
        self.ids.velocity.text = str(new_pipe.velocity()) + " m/sec"
        self.ids.major_head_loss.text = str(round(new_pipe.major_head_loss(),2)) + ' m'
        self.ids.area.text = str(round(new_pipe.area(),2)) + ' m^2'
        
        new_pipe = entities.Pipe()

    # def pipe_spinner_clicked(self, value):
    #     if value == 'Steel':
    #         self.ids.units.text = '"\n'
    #     else:
    #         self.ids.units.text = 'mm\n'
    #     # self.new_pipe.pipetype = value
    #     self.ids.inside_diameter.text = ""
    #     self.ids.inside_diameter.color = 1,1,1
    #     self.ids.idunits.text = ""

    # def find_diameter(self,nominal_diameter,pipe_type):
        
    #     self.ids.inside_diameter.text = ""
    #     self.ids.inside_diameter.color = 1,1,1
    #     self.ids.idunits.text = ""
    
    #     if nominal_diameter == '' or nominal_diameter == 0:
    #         self.ids.inside_diameter.text = "Please enter Nominal diameter"
    #         self.ids.inside_diameter.color = 1,0,0
    #         return
    #     elif pipe_type == "Pipe type:":
    #         self.ids.inside_diameter.text = "Please enter Pipe type"
    #         self.ids.inside_diameter.color = 1,0,0
    #         return
    #     # print(pipe_type)
    #     self.new_pipe.pipetype = pipe_type
    #     self.new_pipe.inside_dia = self.new_pipe.inside_dia_from_nominal(float(nominal_diameter))
    #     self.ids.inside_diameter.text = str(self.new_pipe.inside_dia)
    #     self.ids.idunits.text = "mm"
    #     return

    # def idfromvelocity(self,flow_rate_n,dia_n,length_n,cw_n,minor,elevation):

    #     if minor == "":
    #         minor = float(0)

    #     if elevation == "":
    #         elevation = float(0)
        
    #     new_pipe = entities.Pipe(dia=float(dia_n),length=float(length_n),flow_rate=float(flow_rate_n),cw=float(cw_n),minor_headloss=minor,static_head=elevation)
        
    #     self.ids.total_head_loss.text = str(new_pipe.total_head_loss())
    #     self.ids.velocity.text = str(new_pipe.velocity())
    #     self.ids.major_head_loss.text = str(round(new_pipe.major_head_loss(),2))
    #     self.ids.area.text = str(new_pipe.area())

    # def pipe_selection(self):
    #     self.manager.current = 'diameter_from_pipe'  

    def pipes(self):
        self.manager.current = 'pipes_screen'

    def pumps(self):
        self.manager.current = 'pumps_screen'      


########################### Main app windows ################################


class WelcomeScreen(Screen): # Have to name it just like the .kv <>
    
    def pipes(self):
        self.manager.current = 'pipes_screen'

    def pumps(self):
        self.manager.current = 'pumps_screen'

    # def forget_pass(self, uname):
    #     with open("users.json") as file:
    #         users = json.load(file)
    #     if uname in users: 
    #         self.ids.login_worng.text = f"your's password is:\n{users[uname]['password']}"
    #     else:    
    #         self.ids.login_worng.text = f"There is no user that called: {uname},\nPlease try again"

class PipesScreen(Screen):
    
    def idfromvel(self):
        self.manager.current = 'pipe_from_velocity'

    def idfrompipe(self):
        self.manager.current = 'diameter_from_pipe'

    def headloss(self):
        self.manager.current = 'pipe_head_loss_screen'

class PumpsScreen(Screen):
    
    def pumppower(self):
        self.manager.current = 'pump_power_widget'

    def wetpit(self):
        self.manager.current = 'wetpitwidget'

class PumpPowerScreen(Screen):
    pass

class SignUpScreen(Screen): # Have to name it just like the .kv <>
    
    def add_user(self, uname, pword):
        with open("users.json") as file:
            users = json.load(file)
        users[uname] = {'username': uname, 'password': pword,
         'created':datetime.now().strftime('%Y-%m-%d %H-%M-%S')}
        
        with open("users.json", 'w') as file:
            json.dump(users, file)
        self.manager.current = 'sign_up_screen_success'

class SignUpScreenSuccess(Screen): # Have to name it just like the .kv <>
    
    def return_login(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login_screen'


class LoginScreenSuccess(Screen): # Have to name it just like the .kv <>
    
    def logout(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login_screen'

    def get_quote(self,feel):
        feel = feel.lower()
        available_feelings = glob.glob('quotes/*txt')
        available_feelings = [Path(filename).stem for filename in
                                available_feelings]
        if feel in available_feelings:
            with open(f'quotes/{feel}.txt', 'r', encoding='UTF8') as file:
                quotes = file.readlines()
                self.ids.qoute.text = random.choice(quotes)
        else:
            self.ids.qoute.text = f'try a diffrent feeling from {available_feelings}'


class RootWidget(ScreenManager): # Have to name it just like the .kv <>
    pass

class ImageButton(ButtonBehavior, HoverBehavior, Image): # ButtonBehavior Goes first
    pass

class MainApp(App):
    
    def build(self):
        return RootWidget() # Make sure we use ()

if __name__=='__main__':
    MainApp().run()

