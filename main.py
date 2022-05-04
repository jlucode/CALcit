from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivymd.app import MDApp

from tinydb import TinyDB, Query
from tinydb import where

from typing import Union
from datetime import date
from os.path import join, dirname

# On iOS, data cannot be stored in the root directory. Must create the correct directory path#
directory_path = dirname(App().user_data_dir)
db = TinyDB(join(directory_path, 'stored_user_data.json'))
query = Query()


class CalorieCounterApp(MDApp):
    def __init__(self, **kwargs):
        super(CalorieCounterApp, self).__init__(**kwargs)
        
    def build(self):

        self.theme_cls.primary_palette = "Yellow"
        
        # Removes data that are not from the currrent date. Database should have current information only #
        current_date = str(date.today())
        db.remove(where('current_date') != current_date)
        db.remove(where('mealnumber') == '')

        self.root_widget = Builder.load_file(kv)
        return self.root_widget


# Define the different screens #
class HomeWindow(Screen):
    pass
        

class LogWindow(Screen):
    mealnumber = ObjectProperty(None)
    itemdescription = ObjectProperty(None)
    calories = ObjectProperty(None)
    current_date = str(date.today())
    totaldailycalories = ObjectProperty(None)

    # Removes all empty user submissions #
    db.remove(where('calories') == '')
    
    # Creates a total calories variable. To be viewed on the history screen #
    all_calories = [r['calories'] for r in db]
    sum_calories = []

    for i in all_calories:
        sum_calories.append(int(i))

    sum_calories = sum(sum_calories)
    sum_calories = StringProperty(sum_calories)
    
    def __init__(self, *args, **kwargs):
        super(LogWindow, self).__init__(*args,**kwargs)
        
    # Adds new user submissions, to existing ones, for total calories. To be viewed on the history screen #
    def updatelabel_addition(self):
        db.remove(where('calories') == '')
        ### Sum of Total Calories ###
        allcalories = [r['calories'] for r in db]
        sum_calories = []

        for i in allcalories:
            sum_calories.append(int(i))

        sum_calories = sum(sum_calories)
        sum_calories = StringProperty(sum_calories)
        
    # Saves user submissions on log screen #
    def save(self):
        db.insert({'mealnumber':self.mealnumber.text, 'itemdescription':self.itemdescription.text, 'calories':self.calories.text, 'current_date':self.current_date})

    def press(self, *args):
        db.remove(where('mealnumber') == '')
        db.remove(where('itemdescription') == '')
        db.remove(where('calories') == '')

        mealnumber = self.mealnumber.text
        itemdescription = self.itemdescription.text
        calories = self.calories.text
        current_date = self.current_date

        db.insert({'mealnumber':mealnumber, 'itemdescription':itemdescription, 'calories':calories, 'current_date':current_date})
        allqueries = [db.search(where('mealnumber') != '')]
        allqueries = sorted(allqueries)

        # Clears the input boxes #
        self.mealnumber.text = ""
        self.itemdescription.text = ""
        self.calories.text = ""
        
        db.remove(where('calories') == '')
        
        # Updates the total calories variable. To be viewed on the history screen #
        all_calories = [r['calories'] for r in db]
        sum_calories = []

        for i in all_calories:
            sum_calories.append(int(i))

        self.sum_calories = str(sum(sum_calories))


class HistoryWindow(Screen):
    def __init__(self, **kwargs):
        super(HistoryWindow, self).__init__(**kwargs)
        
    # Creates datatable on history screen #
    def add_datatable(self):
        db.remove(where('calories') == '')

        # Converts user input data from JSON file type to usable text for history screen #
        user_input_data = db.search(query.mealnumber.exists())
        self.a1 = []

        for element in user_input_data:
            for values in element.values():
                self.a1+=[values]
        
        self.a2 = []
        for i in self.a1:
            try:
                self.a2.append(int(i) if float(i).is_integer() else float(i))
            except ValueError:
                self.a2.append(i)
        
        self.a3 = [x for i, x in enumerate(self.a2) if i%4 !=3]
        self.user_data = [self.a3[x:x+3] for x in range(0, len(self.a3), 3)]

        for element in self.user_data:
            element[0] = int(element[0])

        category_titles = [
            ("Meal#", dp(22)), 
            ("Description", dp(22)),
            ("Calories", dp(22))
        ]

        ## Creates the data-table ##
        self.data_tables = MDDataTable(
            rows_num=200,
            size_hint = (0.9, 0.6),
            column_data=category_titles,
            check = True,
            row_data= sorted(self.user_data),
            elevation = 2,
                       
        )
        self.ids.data_layout.add_widget(self.data_tables)
      
    def remove_row(self, data: Union[list, tuple]):
        return self.data_tables.row_data.remove(data) 

    def get_row_checks(self) -> list:
        return self.data_tables.get_row_checks()

    # Function to delete selected user data #
    def remove_selected_rows(self, *args):
        self.selected_rows = self.data_tables.get_row_checks()
        
        # Converts mealnumber and calories from strings to integers. #
        for element in self.selected_rows:
            element[0], element [2] = int(element[0]), int(element[2])
        
        # Removes selected user input data from the database #
        for self.i in self.selected_rows:
            self.remove_row(self.i)
            print (self.i)
            db.remove((query.mealnumber == str(self.i[0])) & (query.itemdescription == str(self.i[1])) & (query.calories == str(self.i[2])))
        
    # Function to subtract from total calories, upon user deletion on history screen #
    def updatelabelsubtract(self, *args):
        
        db.remove(where('calories') == '')
        ### Sum of Total Calories ###
        all_calories = [r['calories'] for r in db]
        sum_calories = []

        for i in all_calories:
            sum_calories.append(int(i))

        sum_calories = sum(sum_calories)

        # Pushes to .kv file #
        self.ids.sum_calories_label.text = str(sum_calories)
        
    
class WindowManager(ScreenManager):
    pass


kv = 'main.kv'
if __name__ == '__main__':
    CalorieCounterApp().run()