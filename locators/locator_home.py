from playwright.sync_api import Page

class HomeLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector contendor tipo de prueba
    @property
    def contenedorTipoPrueba(self):
        return self.page.get_by_text("Automation Testing Practice WebSite for QA and Developers Free Test Automation")
        
    #Selector link Wen input
    @property
    def linkWebInput(self):
        return self.page.get_by_role("link", name="Web inputs")
    
    #Selector link Login
    @property
    def linkTestLogin(self):
        return self.page.get_by_role("link", name="Test Login Page")
    
    #Selector link Register
    @property
    def linkTestRegister(self):
        return self.page.get_by_role("link", name="Test Register Page")
    
    #Selector link Dynamic table
    @property
    def linkDynamicTable(self):
        return self.page.get_by_role("link", name="Dynamic Table")
    
    #Selector menú superior hamburguesa
    @property
    def menuSuperiorHamburguesa(self):
        return self.page.get_by_role("button", name="Toggle navigation")