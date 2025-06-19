def move_page(self, page_select, index) :
    selected_text = page_select.currentText()  
    if selected_text == 'Main' :
        from menu_page.menu_page import menu_page
        menu_page(self)
    elif selected_text == "Detect" :
        from detect_page.upload_menu.upload_menu import upload_menu
        upload_menu(self)
    elif selected_text == "Label" :
        from label_page.anomaly.anomaly import anomaly
        anomaly(self)
    elif selected_text == "Train" :
        from train_page.train import train
        train(self)
    elif selected_text == "Report" :
        return
    elif selected_text == 'Admin' :
        from admin_page.create_user.create_user import create_user
        create_user(self)