from builtins import object
from lib.common import helpers

class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Restart-Computer',

            'Author': ['@harmj0y'],

            'Description': ("Restarts the specified machine."),

            'Software': '',

            'Techniques': [''],

            'Background' : False,

            'OutputExtension' : None,
            
            'NeedsAdmin' : False,

            'OpsecSafe' : False,
            
            'Language' : 'powershell',

            'MinLanguageVersion' : '2',
            
            'Comments': []
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu
        
        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value


    def generate(self, obfuscate=False, obfuscationCommand=""):
        
        script = "'Restarting computer';Restart-Computer -Force"
        if obfuscate:
            script = helpers.obfuscate(self.mainMenu.installPath, psScript=script, obfuscationCommand=obfuscationCommand)

        moduleName = self.info['Name']
        techniques = self.info['Techniques']
        software = self.info['Software']

        return script, moduleName, techniques, software
