import flet as ft
from db_connection import connect_db
from mysql.connector import Error


def main(page: ft.Page):
    try:
        page.window.frameless = True
        page.window.width = 400
        page.window.height = 350
        if hasattr(page.window, "alignment"):
            page.window.alignment = ft.alignment.center
    except Exception:
        pass

    page.title = "User Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.AMBER_ACCENT
    page.theme_mode = ft.ThemeMode.LIGHT

    login_title = ft.Text(
        "User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER,
    )

    username_field = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True,
        can_reveal_password=True,
        icon=ft.Icons.LOCK,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    def make_dialog(title, message, icon=None, color=None):
        return ft.AlertDialog(
            title=ft.Text(title, text_align=ft.TextAlign.CENTER),
            content=ft.Text(message, text_align=ft.TextAlign.CENTER),
            icon=ft.Icon(name=icon, color=color) if icon else None,
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dialog(dlg))
                for dlg in []
            ],
        )

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def login_click(e):
        username = username_field.value
        password = password_field.value

        success_dialog = ft.AlertDialog(
            title=ft.Text("Login Successful"),
            content=ft.Text(f"Welcome, {username}!"),
            icon=ft.Icon(name=ft.Icons.CHECK_CIRCLE, color="green"),
            actions=[ft.TextButton("OK", on_click=lambda ev: close_dialog(success_dialog))],
        )
        failure_dialog = ft.AlertDialog(
            title=ft.Text("Login Failed"),
            content=ft.Text("Invalid username or password"),
            icon=ft.Icon(name=ft.Icons.ERROR, color="red"),
            actions=[ft.TextButton("OK", on_click=lambda ev: close_dialog(failure_dialog))],
        )
        invalid_input_dialog = ft.AlertDialog(
            title=ft.Text("Input Error"),
            content=ft.Text("Please enter username and password"),
            icon=ft.Icon(name=ft.Icons.INFO, color="blue"),
            actions=[ft.TextButton("OK", on_click=lambda ev: close_dialog(invalid_input_dialog))],
        )
        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error"),
            content=ft.Text("An error occurred while connecting to the database"),
            actions=[ft.TextButton("OK", on_click=lambda ev: close_dialog(database_error_dialog))],
        )

        if not username or not password:
            page.open(invalid_input_dialog)
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password),
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                page.open(success_dialog)
            else:
                page.open(failure_dialog)
            page.update()

        except Error:
            page.open(database_error_dialog)
            page.update()

    login_button = ft.ElevatedButton(
        text="Login", on_click=login_click, width=100, icon=ft.Icons.LOGIN
    )

    field_container = ft.Container(
        content=ft.Column([username_field, password_field], spacing=20)
    )
    button_container = ft.Container(
        content=login_button,
        alignment=ft.alignment.top_right,
        margin=ft.margin.only(0, 20, 40, 0),
    )

    page.add(login_title, field_container, button_container)


ft.app(target=main)