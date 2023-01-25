import sys
import autostarter # works only with https://github.com/richibrics/autostarter.git at the moment, waiting for PR to be merged
from IoTuring.MyApp.App import App

# todo check if autostart is enabled or disabled (need autostarter creator to add this feature)
class AutostartConfigurator():
    def run():
        selection = False
        while selection is False:
            print("\nConfiguring autostart...")
            print("1 - Enable autostart [system-wide]")
            print("2 - Disable autostart [system-wide]")
            print("3 - Enable autostart [user-wide]")
            print("4 - Disable autostart [user-wide]")
            selection = input("Select an option: ")
            
            if selection == "1":
                AutostartConfigurator.enable(True)
            elif selection == "2":
                AutostartConfigurator.disable(True)
            elif selection == "3":
                AutostartConfigurator.enable(False)
            elif selection == "4":
                AutostartConfigurator.disable(False)
            else:
                selection = False
        
    def enable(system_wide):
        try: 
            app_name = App.getName()
            script_location = f"-m {app_name}"
            interpreter=sys.executable
            
            autostarter.add(
                script_location,
                identifier=app_name,
                system_wide=system_wide,
                interpreter=interpreter
            )
            print("Autostart enabled successfully")
        except Exception as e:
            print("Autostart could not be enabled")
            print("Error: " + str(e))
        
    def disable(system_wide):
        try:
            app_name = App.getName()
            result = autostarter.remove(app_name, system_wide=system_wide)
            
            if result is True: 
                print("Autostart disabled successfully")
            else:
                print("Autostart could not be disabled")
        except Exception as e:
            print("Autostart could not be disabled")
            print("Error: " + str(e))
