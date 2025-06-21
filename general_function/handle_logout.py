"""Handle user logout and reset session attributes."""

from general_function.query import log_out_session


def handle_logout(self):
    """Handle user logout and reset session attributes."""
    from login_page.login_page import setup_login_page

    try:
        # Log out the current session if it exists
        if hasattr(self, "id_operation") and self.id_operation:
            log_out_session(self.id_operation)

        # Reset all session attributes
        session_attrs = ["id_user", "username", "password", "role", "id_operation"]
        for attr in session_attrs:
            setattr(self, attr, None)

        # Return to login page
        setup_login_page(self)

    except Exception as e:
        print(f"Error during logout: {str(e)}")
