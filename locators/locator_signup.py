from playwright.sync_api import Page

class SignUpLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector label titulo sing up
    @property
    def labelSingUp(self):
        return self.page.get_by_role("heading", name="Sign up")
    
    #Selector link Have an account
    @property
    def linkHaveAnAccount(self):
        return self.page.get_by_role("link", name="Have an account?")
    
    #Selector campo username
    @property
    def txtBoxUserName(self):
        return self.page.get_by_role("textbox", name="Username")
    
    #Selector campo email
    @property
    def txtBoxEmail(self):
        return self.page.get_by_role("textbox", name="Email")
    
    #Selector campo password
    @property
    def txtBoxPassword(self):
        return self.page.get_by_role("textbox", name="Password")
    
    #Selector botón sign up
    @property
    def btnSignUp(self):
        return self.page.get_by_role("button", name="Sign up")
    
    #Selector mensaje de error
    @property
    def msgerror(self):
        return self.page.locator("body > div.ng-scope > div > div > div > div > div > list-errors > ul")