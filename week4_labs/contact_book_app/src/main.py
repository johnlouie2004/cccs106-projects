import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT

    db_conn = init_db()

    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)
    search_field = ft.TextField(
        label="Search",
        width=350,
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, search_field.value)
    )
    inputs = (name_input, phone_input, email_input)

    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn, search_field)
    )

    def apply_textfield_style():
        if page.theme_mode == ft.ThemeMode.DARK:
            for field in [name_input, phone_input, email_input, search_field]:
                field.border_color = ft.Colors.WHITE
                field.color = ft.Colors.WHITE
        else:
            for field in [name_input, phone_input, email_input, search_field]:
                field.border_color = ft.Colors.BLACK
                field.color = ft.Colors.BLACK

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_button.icon = ft.Icons.WB_SUNNY
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_button.icon = ft.Icons.NIGHTLIGHT_ROUND
        apply_textfield_style()
        page.update()

    theme_button = ft.IconButton(
        icon=ft.Icons.NIGHTLIGHT_ROUND,
        tooltip="Toggle Theme",
        on_click=toggle_theme
    )

    page.add(
        ft.Column(
            [
                ft.Row([theme_button], alignment=ft.MainAxisAlignment.END),
                ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                ft.Text("Contacts:", size=20, weight=ft.FontWeight.BOLD),
                search_field,
                contacts_list_view,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    apply_textfield_style()
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)