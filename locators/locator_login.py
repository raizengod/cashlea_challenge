from playwright.sync_api import Page

class LoginLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector label titulo Login
    @property
    def labelLogin(self):
        return self.page.get_by_role("heading", name="Test Login page for")
    
    #Selector label decripción de login
    @property
    def labelDescriptionLogin(self):
        return self.page.locator("#core div").filter(has_text="This Test Login page is").nth(3)
    
    #Selector label username login
    @property
    def labelUsernameLogin(self):
        return self.page.locator("#login").get_by_text("Username")
    
    #Selector campo username login
    @property
    def txtUsernameLogin(self):
        return self.page.get_by_role("textbox", name="Username")
    
    #Selector label password login
    @property
    def labelPasswordLogin(self):
        return self.page.locator("#login").get_by_text("Password")
    
    #Selector campo password login
    @property
    def txtPasswordLogin(self):
        return self.page.get_by_role("textbox", name="Password")
    
    #Selector botón login
    @property
    def btnLogin(self):
        return self.page.get_by_role("button", name="Login")
    
    #Selector mensaje error/éxito/alerta
    @property
    def flashMessage(self):
        return self.page.locator("#flash")
    
    #Selector cerrar mensaje error/éxito/alerta
    @property
    def btnCerrarFlashMessage(self):
        return self.page.get_by_role("button", name="Close")