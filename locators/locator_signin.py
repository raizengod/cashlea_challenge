from playwright.sync_api import Page

class SignInLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector label titulo sing in
    @property
    def labelSingIn(self):
        return self.page.get_by_role("heading", name="Sign in")
    
    #Selector link Need an account
    @property
    def linkNeedAnAccount(self):
        return self.page.get_by_role("link", name="Need an account?")
    
    #Selector campo email
    @property
    def txtBoxEmail(self):
        return self.page.get_by_role("textbox", name="Email")
    
    #Selector campo password
    @property
    def txtBoxPassword(self):
        return self.page.get_by_role("textbox", name="Password")
    
    #Selector botón Sign In
    @property
    def btnSignIn(self):
        return self.page.get_by_role("button", name="Sign in")
    
    #Selector mensaje de error
    @property
    def msgerror(self):
        return self.page.locator("body > div.ng-scope > div > div > div > div > div > list-errors > ul")