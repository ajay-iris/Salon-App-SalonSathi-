import flet as ft
import requests
from dashboard import build_dashboard_screen

# Base URL pointing directly to our local FastAPI server engine
BACKEND_API_BASE = "http://127.0.0.1:8000/api/auth"

def main(page: ft.Page):
    # --- Local Workspace Client App Tracking Flags ---
    app_state = {
        "user_phone": "", # Tracks just the 10 raw digits typed by the user
        "user_name": "Valued Customer"
    }

    def route_to(screen_name):
        page.clean()
        if screen_name == "login":
            page.add(build_login_screen())
        elif screen_name == "register":
            page.add(build_register_screen())
        elif screen_name == "dashboard":
            # Pass page context, navigation engine callback, and state mapping dictionaries cleanly
            page.add(build_dashboard_screen(page, route_to, app_state))
        page.update()

    # --- View 1: Login ---
    def build_login_screen():
        phone_input = ft.TextField(
            label="Phone Number",
            prefix=ft.Text("+977 ", style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD, size=16)),
            hint_text="98XXXXXXXX",
            label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            keyboard_type=ft.KeyboardType.PHONE,
            border_color=ft.Colors.BLACK, border_width=2, border_radius=12, height=60, fill_color=ft.Colors.WHITE, filled=True,
        )

        otp_input = ft.TextField(
            label="Enter 6-Digit Alphanumeric Code",
            label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            hint_text="A1B2C3",
            max_length=6,
            border_color=ft.Colors.BLACK, border_width=2, border_radius=12, height=60, fill_color=ft.Colors.WHITE, filled=True,
            visible=False 
        )

        sms_status = ft.Text("", color=ft.Colors.GREEN_800, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        error_msg = ft.Text("", color=ft.Colors.RED_800, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
        
        request_sms_btn = ft.ElevatedButton(
            content=ft.Text("Request Sign-in Code", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            height=50, width=float("inf"),
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_900, shape=ft.RoundedRectangleBorder(radius=12)),
        )

        login_action_btn = ft.ElevatedButton(
            content=ft.Text("Verify & Login", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            height=54, width=float("inf"),
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_800, shape=ft.RoundedRectangleBorder(radius=12)),
            visible=False
        )

        def on_request_sms(e):
            full_phone_number = f"+977{phone_input.value.strip()}"
            try:
                response = requests.post(
                    f"{BACKEND_API_BASE}/request-otp",
                    json={"phone": full_phone_number, "purpose": "login"}
                )
                data = response.json()
                
                if response.status_code == 200:
                    error_msg.value = ""
                    app_state["user_phone"] = full_phone_number
                    sms_status.value = data.get("message", "SMS Sent!")
                    otp_input.visible = True
                    login_action_btn.visible = True
                    request_sms_btn.visible = False
                else:
                    error_msg.value = data.get("detail", "Failed to process request.")
            except Exception:
                error_msg.value = "Network Error: Could not connect to server."
            page.update()

        def on_verify_and_login(e):
            full_phone_number = f"+977{phone_input.value.strip()}"
            otp = otp_input.value.strip().upper()
            try:
                response = requests.post(
                    f"{BACKEND_API_BASE}/verify-login",
                    json={"phone": full_phone_number, "otp_code": otp}
                )
                data = response.json()
                
                if response.status_code == 200:
                    error_msg.value = ""
                    app_state["user_name"] = data["user_profile"]["name"]
                    app_state["user_phone"] = data["user_profile"]["phone"]
                    route_to("dashboard")
                else:
                    error_msg.value = data.get("detail", "Security mismatch validation.")
            except Exception:
                error_msg.value = "Network communications error."
            page.update()

        request_sms_btn.on_click = on_request_sms
        login_action_btn.on_click = on_verify_and_login

        return ft.Container(
            content=ft.Column([
                ft.Text("💇 Salon Sign-In", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Container(height=30),
                phone_input,
                ft.Container(height=12),
                otp_input,
                ft.Container(height=10),
                sms_status,
                error_msg,
                ft.Container(height=20),
                request_sms_btn,
                login_action_btn,
                ft.Container(height=15),
                ft.TextButton(
                    content=ft.Text("New here? Create New Account", size=14, color=ft.Colors.BLUE_900, weight=ft.FontWeight.BOLD),
                    on_click=lambda _: route_to("register")
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            padding=24, expand=True, bgcolor=ft.Colors.GREY_100
        )

    # --- View 2: Registration ---
    def build_register_screen():
        phone_input = ft.TextField(
            label="Mobile Phone Number",
            prefix=ft.Text("+977 ", style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD, size=16)),
            hint_text="98XXXXXXXX",
            label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            keyboard_type=ft.KeyboardType.PHONE,
            border_color=ft.Colors.BLACK, border_width=2, border_radius=12, height=56, fill_color=ft.Colors.WHITE, filled=True
        )

        name_input = ft.TextField(
            label="Full Account Holder Name",
            label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=ft.Colors.BLACK),
            border_color=ft.Colors.BLACK, border_width=2, border_radius=12, height=56, fill_color=ft.Colors.WHITE, filled=True
        )

        otp_boxes = []
        
        def make_focus_jumper(index):
            def jumper(e):
                val = e.control.value
                if len(val) >= 1:
                    e.control.value = val[-1].upper()
                    if index < 5:
                        otp_boxes[index + 1].focus()
                page.update()
            return jumper

        for i in range(6):
            box = ft.TextField(
                width=45, height=50, border_color=ft.Colors.BLACK, border_width=2,
                border_radius=8, text_align=ft.TextAlign.CENTER, filled=True, fill_color=ft.Colors.WHITE,
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, size=18),
                max_length=2, counter=None, dense=True,
                on_change=make_focus_jumper(i)
            )
            otp_boxes.append(box)

        otp_row_container = ft.Row(otp_boxes, alignment=ft.MainAxisAlignment.CENTER, spacing=6, visible=False)
        otp_section_label = ft.Text("Enter 6-Character Alphanumeric Code Below:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, visible=False)

        sms_status = ft.Text("", color=ft.Colors.GREEN_800, weight=ft.FontWeight.BOLD)
        error_msg = ft.Text("", color=ft.Colors.RED_800, weight=ft.FontWeight.BOLD)

        send_code_btn = ft.ElevatedButton(
            content=ft.Text("Send SMS Verification Code", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            height=50, width=float("inf"),
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_900, shape=ft.RoundedRectangleBorder(radius=12))
        )

        submit_registration_btn = ft.ElevatedButton(
            content=ft.Text("Complete Account Creation", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            height=54, width=float("inf"),
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_800, shape=ft.RoundedRectangleBorder(radius=12)),
            visible=False
        )

        def on_send_verification(e):
            full_phone_number = f"+977{phone_input.value.strip()}"
            name = name_input.value.strip()
            
            if not phone_input.value.strip() or not name:
                error_msg.value = "Fields cannot be empty."
                page.update()
                return

            try:
                response = requests.post(
                    f"{BACKEND_API_BASE}/request-otp",
                    json={"phone": full_phone_number, "purpose": "registration"}
                )
                data = response.json()
                
                if response.status_code == 200:
                    error_msg.value = ""
                    sms_status.value = data.get("message", "SMS Dispatched!")
                    otp_section_label.visible = True
                    otp_row_container.visible = True
                    submit_registration_btn.visible = True
                    send_code_btn.visible = False
                    page.update()
                    otp_boxes[0].focus()
                else:
                    error_msg.value = data.get("detail", "Error processing request.")
            except Exception:
                error_msg.value = "Network connection failure."
            page.update()

        def on_register_submit(e):
            full_phone_number = f"+977{phone_input.value.strip()}"
            name = name_input.value.strip()
            collected_otp = "".join(box.value.strip().upper() for box in otp_boxes)
            
            try:
                response = requests.post(
                    f"{BACKEND_API_BASE}/register-user",
                    json={"phone": full_phone_number, "name": name, "otp_code": collected_otp}
                )
                if response.status_code == 200:
                    error_msg.value = ""
                    sms_status.value = "Account verified! Redirecting to login..."
                    page.update()
                    import time
                    time.sleep(1.2)
                    route_to("login")
                else:
                    error_msg.value = response.json().get("detail", "Verification failed.")
            except Exception:
                error_msg.value = "Network communication error."
            page.update()

        send_code_btn.on_click = on_send_verification
        submit_registration_btn.on_click = on_register_submit

        return ft.Container(
            content=ft.Column([
                ft.Text("📝 Create Account", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Container(height=25),
                name_input,
                ft.Container(height=12),
                phone_input,
                ft.Container(height=15),
                otp_section_label,
                otp_row_container,
                ft.Container(height=10),
                sms_status,
                error_msg,
                ft.Container(height=20),
                send_code_btn,
                submit_registration_btn,
                ft.Container(height=15),
                ft.TextButton(
                    content=ft.Text("Already registered? Sign In", size=14, color=ft.Colors.BLUE_900, weight=ft.FontWeight.BOLD),
                    on_click=lambda _: route_to("login")
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            padding=24, expand=True, bgcolor=ft.Colors.GREY_100
        )

    # --- System Init Boot Configurations ---
    page.title = "Salon Core Application"
    page.window.width = 400
    page.window_height = 740
    page.window_resizable = False
    page.add(build_login_screen())

if __name__ == "__main__":
    ft.run(main)