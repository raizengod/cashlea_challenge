from playwright.sync_api import Page

class RegisterLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector label titulo sing up
    @property
    def labelRegister(self):
        return self.page.get_by_role("heading", name="Test Register page for")
    
    #Selector label decripción de register
    @property
    def labelDescriptionRegister(self):
        return self.page.locator("#core div").filter(has_text="This Test Register page is").nth(3)
    
    #Selector label username register
    @property
    def labelUsernameRegister(self):
        return self.page.get_by_text("Username")
    
    #Selector campo username register
    @property
    def txtUsernameRegister(self):
        return self.page.get_by_role("textbox", name="Username")
    
    #Selector label password register
    @property
    def labelPasswordRegister(self):
        return self.page.get_by_text("Password", exact=True)
    
    #Selector campo password register
    @property
    def txtPasswordRegister(self):
        return self.page.get_by_role("textbox", name="Password", exact=True)
    
    #Selector label confirmar password register
    @property
    def labelConfirmPasswordRegister(self):
        return self.page.get_by_text("Confirm Password")
    
    #Selector campo confirmar password register
    @property
    def txtConnfirPasswordRegister(self):
        return self.page.get_by_role("textbox", name="Confirm Password")
    
    #Selector botón Register
    @property
    def btnRegister(self):
        return self.page.get_by_role("button", name="Register")
    
    #Selector mensaje error/éxito/alerta
    @property
    def flashMessage(self):
        return self.page.locator("#flash")
    
    #Selector cerrar mensaje error/éxito/alerta
    @property
    def btnCerrarFlashMessage(self):
        return self.page.get_by_role("button", name="Close")
    
    
    