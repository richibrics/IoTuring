import sys
import autostarter # works only with https://github.com/richibrics/autostarter.git at the moment, waiting for PR to be merged
from IoTuring.MyApp.App import App

# todo check if autostart is enabled or disabled (need autostarter creator to add this feature)
class AutostartConfigurator():
    def run():
        selection = False
        while selection is False:
            print("\nConfiguring autostart...")
            print("1 - Enable autostart")
            print("2 - Disable autostart")
            selection = input("Select an option: ")
            
            if selection == "1":
                AutostartConfigurator.enable()
            elif selection == "2":
                AutostartConfigurator.disable()
            else:
                selection = False
        
    def enable():
        try: 
            app_name = App.getName()
            script_location = f"-m {app_name}"
            interpreter=sys.executable
            
            autostarter.add(
                script_location,
                identifier=app_name,
                interpreter=interpreter
            )
            print("Autostart enabled successfully")
        except Exception as e:
            print("Autostart could not be enabled")
            print("Error: " + str(e))
        
    def disable():
        try:
            app_name = App.getName()
            result = autostarter.remove(app_name)
            
            if result is True: 
                print("Autostart disabled successfully")
            else:
                print("Autostart could not be disabled")
        except Exception as e:
            print("Autostart could not be disabled")
            print("Error: " + str(e))
