# source ~/kivy_venv/bin/activate
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle
from kivy.config import Config
from kivy.core.clipboard import Clipboard
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.scrollview import ScrollView
import requests

# from kivy.lang import Builder
# Builder.load_file("exer.kv")

# https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis=8123+4493+6011&sources=ONCHigh

Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '500')

#Repositories
drug_list1=[] 
drug_rxcui_list=[]
address_string=""


class MyTextInput(TextInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """ Add support for tab as an 'autocomplete' using the suggestion text.
        """
    
        if self.suggestion_text and keycode[1] == 'tab':
            self.insert_text(self.suggestion_text + ' ')
            return True
        return super(MyTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

class MainGrid(Widget):
    full_drug_list=[]

    drug1 = ObjectProperty(None)
    drug_list = ObjectProperty(None)
    desc = ObjectProperty(None)
    
    def pressed_add(self):
        if not self.drug1.text:
            pass

        else:
            global drug_list1 
            drug_list1 += [self.drug1.text]
            self.drug_list.text += self.drug1.text +'\n'
            self.drug1.text=""

      
        
    def pressed_re(self):
        drug_list1.clear() 
        drug_rxcui_list.clear()
        address_string=""
        self.drug_list.text=""
        self.desc.text=""

        

    def pressed(self):
        def check_interaction(drug_list1):
            if not drug_list1:
               return "You should put at least one drug."
            
            # if "" in drug_list1:
            #     return "You should put at least one drug."
            #     pressed_re()

            for i in drug_list1:
                
                url2=f"https://rxnav.nlm.nih.gov/REST/approximateTerm?term={i}"
                rxcui2=requests.get(url2, headers={"Accept":"application/json"})

                drug_data=rxcui2.json()

                if 'candidate' not in drug_data["approximateGroup"]:
                    return "The drug(s) cannot be found."
                else:
                    drug_rxcui=drug_data["approximateGroup"]['candidate'][0]['rxcui']
                    global drug_rxcui_list
                    drug_rxcui_list.append(drug_rxcui)
            
            global address_string 
            address_string += drug_rxcui_list[0]
            for i in drug_rxcui_list[1:]:
                address_string += f"+ {i}"

            url3=f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={address_string}"
            response=requests.get(url3, headers={"Accept":"application/json"})
            interaction=response.json()
          
            if 'fullInteractionTypeGroup' not in interaction:
                return 'No interaction'
            
            else:                    
                num_desc=len(interaction['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'])
                
                sev=[]
                inter=[]
                final_list=[]

                for i in range(0,num_desc):
                    final_severity=interaction['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][i]['severity']
                    final_interaction=interaction['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][i]['description']
                    sev.append(final_severity)
                    inter.append(final_interaction)
                    

                for i in range(num_desc):
                    printing=f"Severity: {sev[i]}, Drug interaction: {inter[i]}"
                    final_list.append(printing)

                return str(final_list)
                   
    
            # else:
            #     final_severity=interaction['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['severity']
            #     final_interaction=interaction['fullInteractionTypeGroup'][0]['fullInteractionType'][0]['interactionPair'][0]['description']
                
          


         
        strin=check_interaction(drug_list1)
        self.desc.text=strin
        # drug_list.text=""

        # print(self.desc.text)
        # print(type(self.desc))
        # desc = ObjectProperty(check_interaction(self.drug1.text,self.drug2.text))
        # print(self.drug1.text)
        # check_interaction(self.drug1.text,self.drug2.text)
        # self.count += 1
        # print(self.drug1.text, self.count)
    



    def copyText(self):
        show_popup()
        Clipboard.copy(self.desc.text)


class CopiedPopUp(FloatLayout):
    pass

def show_popup():
    show = CopiedPopUp()
    window = Popup(title="Copied", content=show, size_hint=(None,None), size=(300,100), auto_dismiss= True) 
    window.open()
    def dismiss_popup(dt):
        print(dt)
        window.dismiss()
    Clock.schedule_once(dismiss_popup, 1)

class ExerApp(App):
    def build(self):
        return MainGrid()

if __name__ == "__main__":
    ExerApp().run()