def handle_logout(self) :   
    from login_page.login_page import login_page 
    from general_function.query import log_out_session
    id_operation = self.id_operation
    log_out_session(id_operation)
    self.id_user = None
    self.username = None
    self.password = None
    self.role = None
    self.id_operation = None
    login_page(self)