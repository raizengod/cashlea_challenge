from playwright.sync_api import Page

class WebInputsLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector label Web input
    @property
    def labelTituloWebInput(self):
        return self.page.get_by_role("heading", name="Web inputs page for")
    
    #Selector label Web input
    @property
    def labelDescriptionWebInput(self):
        return self.page.get_by_text("Web inputs refer to the data")
    
    #Selector botón display inputs
    @property
    def btnDisplayInputs(self):
        return self.page.get_by_role("button", name="Display Inputs")
    
    #Selector botón clear inputs
    @property
    def btnClearInputs(self):
        return self.page.get_by_role("button", name="Clear Inputs")
    
    # ================================== TextBox Inputs ==================================
    
    #Selector campo numérico
    @property
    def inputNumerico(self):
        return self.page.get_by_role("spinbutton", name="Input: Number")
    
    #Selector campo alfabético
    @property
    def inputAlfabetico(self):
        return self.page.get_by_role("textbox", name="Input: Text")
    
    #Selector campo password
    @property
    def inputPassword(self):
        return self.page.get_by_role("textbox", name="Input: Password")
    
    #Selector campo fecha
    @property
    def inputFecha(self):
        return self.page.get_by_role("textbox", name="Input: Date")
    
    # ================================== TextBox Output ==================================
    
    #Selector campo numérico
    @property
    def outputNumerico(self):
        return self.page.locator("#output-number")
    
    #Selector campo alfabético
    @property
    def outputAlfabetico(self):
        return self.page.locator("#output-text")
    
    #Selector campo password
    @property
    def outputPassword(self):
        return self.page.locator("#output-password")
    
    #Selector campo fecha
    @property
    def outputFecha(self):
        return self.page.locator("#output-date")
    