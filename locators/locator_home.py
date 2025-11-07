from playwright.sync_api import Page

class HomeLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector app-header
    @property
    def addHeader (self):
        return self.page.locator("app-header").get_by_role("link", name="conduit")
    
    #Selector link home
    @property
    def linkHome(self):
        return self.page.get_by_role("link", name="Home")
    
    #Selector botón sing in
    @property
    def linkSingIn(self):
        return self.page.get_by_role("link", name="Sign in")
    
    #Selector botón sing up
    @property
    def linkSingUp(self):
        return self.page.get_by_role("link", name="Sign up")
    
    #Selector banner home
    @property
    def bannerHome(self):
        return self.page.locator("div").filter(has_text="conduit A place to share your").nth(3)
    
    #Selector encabezado global feed home
    @property
    def globalFeedHome(self):
        return self.page.get_by_text("Your Feed Global Feed")