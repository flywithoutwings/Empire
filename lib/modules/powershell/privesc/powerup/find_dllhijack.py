from __future__ import print_function
from builtins import str
from builtins import object
from lib.common import helpers

class Module(object):

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Find-ProcessDLLHijack',

            'Author': ['@harmj0y'],

            'Description': ('Finds generic .DLL hijacking opportunities.'),

            'Software': 'S0194',

            'Techniques': ['T1087', 'T1038', 'T1031', 'T1034', 'T1057', 'T1012'],

            'Background' : True,

            'OutputExtension' : None,
            
            'NeedsAdmin' : False,

            'OpsecSafe' : True,
            
            'Language' : 'powershell',

            'MinLanguageVersion' : '2',
            
            'Comments': [
                'https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerUp'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'ExcludeWindows' : {
                'Description'   :   "Switch. Exclude paths from C:\Windows\* instead of just C:\Windows\System32\*",
                'Required'      :   False,
                'Value'         :   ''
            },
            'ExcludeProgramFiles' : {
                'Description'   :   "Switch. Exclude paths from C:\Program Files\* and C:\Program Files (x86)\*",
                'Required'      :   False,
                'Value'         :   ''
            },
            'ExcludeOwned' : {
                'Description'   :   "Switch. Exclude processes the current user owns.",
                'Required'      :   False,
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

        moduleName = self.info["Name"]
        
        # read in the common powerup.ps1 module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/privesc/PowerUp.ps1"
        if obfuscate:
            helpers.obfuscate_module(self.mainMenu , moduleSource=moduleSource, obfuscationCommand=obfuscationCommand)
            moduleSource = moduleSource.replace("module_source", "obfuscated_module_source")
        try:
            f = open(moduleSource, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(moduleSource)))
            return ""

        moduleCode = f.read()
        f.close()

        # # get just the code needed for the specified function
        # script = helpers.generate_dynamic_powershell_script(moduleCode, moduleName)
        script = moduleCode

        scriptEnd = ';' + moduleName + " "

        for option,values in self.options.items():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        scriptEnd += " -" + str(option)
                    else:
                        scriptEnd += " -" + str(option) + " " + str(values['Value']) 

        scriptEnd += ' | ft -wrap | Out-String | %{$_ + \"`n\"};"`n'+str(moduleName)+' completed!"'
        scriptEnd = helpers.keyword_obfuscation(scriptEnd, self.mainMenu)
        if obfuscate:
            scriptEnd = helpers.obfuscate(self.mainMenu.installPath, psScript=scriptEnd, obfuscationCommand=obfuscationCommand)
        script += scriptEnd
        return script