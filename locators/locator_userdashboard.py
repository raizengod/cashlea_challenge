from playwright.sync_api import Page

class UserDashboardLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector mensaje error/éxito/alerta
    @property
    def flashMessage(self):
        return self.page.locator("#flash")
    
    #Selector cerrar mensaje error/éxito/alerta
    @property
    def btnCerrarFlashMessage(self):
        return self.page.get_by_role("button", name="Close")
    
    #Selector label user dashboard
    @property
    def labelUserDashboard(self):
        return self.page.get_by_role("heading", name="Secure Area page for")
    
    #Selector saludo a usuario
    @property
    def labelWelcome(self):
        return self.page.locator("#username")
    
    #Selector label descripción dashboard
    @property
    def labelDescriptionDashboard(self):
        return self.page.get_by_role("heading", name="Welcome to the Secure Area.")
    
    #Selector botón logout
    @property
    def btnLogout(self):
        return self.page.get_by_role("link", name="Logout")
    
    #Selector link home
    @property
    def linkGoHome(self):
        return self.page.get_by_role("link", name="Home")