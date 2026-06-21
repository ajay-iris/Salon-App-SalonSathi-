import flet as ft
import random
import string

def main(page: ft.Page):
    app_state = {
        "current_page": "login",
        "generated_otp": "",
        "user_phone": "+977",
        "user_name": "",
        "database": {} 
    }

    def generate_secure_otp():
        pool = string.ascii_uppercase + string.digits
        return "".join(random.choice(pool) for _ in range(6))

    def trigger_mock_sms(phone, otp):
        print("\n" + "="*40)
        print(f" SMS GATEWAY SIMULATION -> To: {phone} | Code: [{otp}]")
        print("="*40 + "\n")

    def route_to(screen_name):
        app_state["current_page"] = screen_name
        page.clean()
        if screen_name == "login":
            page.add(build_login_screen())
        elif screen_name == "register":
            page.add(build_register_screen())
        page.update()

    # --- View 1: Login ---
    def build_login_screen():
        phone_input = ft.TextField(
            value=app_state["user_phone"],
            label="Phone Number",
            label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
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
            phone = phone_input.value.strip()
            if phone not in app_state["database"]:
                error_msg.value = "Access Denied: Sign up first."
                page.update()
                return

            error_msg.value = ""
            app_state["generated_otp"] = generate_secure_otp()
            app_state["user_phone"] = phone
            trigger_mock_sms(phone, app_state["generated_otp"])
            
            sms_status.value = f"Verification SMS sent!"
            otp_input.visible = True
            login_action_btn.visible = True
            request_sms_btn.visible = False
            page.update()

        def on_verify_and_login(e):
            if otp_input.value.strip().upper() == app_state["generated_otp"]:
                error_msg.value = ""
                sms_status.value = f"Welcome back, {app_state['database'][app_state['user_phone']]}!"
            else:
                error_msg.value = "Security Violation: Invalid validation code."
            page.update()

        request_sms_btn.on_click = on_request_sms
        login_action_btn.on_click = on_verify_and_login

        return ft.Container(
            content=ft.Column([
                ft.Text(" Salon Sign-In", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
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
            value="+977",
            label="Mobile Phone Number",
            label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            border_color=ft.Colors.BLACK, border_width=2, border_radius=12, height=56, fill_color=ft.Colors.WHITE, filled=True
        )

        name_input = ft.TextField(
            label="Full Account Holder Name",
            label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=ft.Colors.BLACK),
            border_color=ft.Colors.BLACK, border_width=2, border_radius=12, height=56, fill_color=ft.Colors.WHITE, filled=True
        )

        # Create 6 boxes list
        otp_boxes = []
        
        # Auto-focus jumper logic loop
        def make_focus_jumper(index):
            def jumper(e):
                val = e.control.value
                if len(val) >= 1:
                    # Strip to max 1 char, capitalize it
                    e.control.value = val[-1].upper()
                    # Jump focus forward to next box index if available
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
                on_change=make_focus_jumper(i) # Connect jumping callback trigger
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
            phone = phone_input.value.strip()
            name = name_input.value.strip()
            
            if len(phone) < 7 or not name:
                error_msg.value = "Fields cannot be empty."
                page.update()
                return

            error_msg.value = ""
            app_state["generated_otp"] = generate_secure_otp()
            app_state["user_phone"] = phone
            app_state["user_name"] = name
            
            trigger_mock_sms(phone, app_state["generated_otp"])
            
            sms_status.value = "SMS Sent!"
            otp_section_label.visible = True
            otp_row_container.visible = True
            submit_registration_btn.visible = True
            send_code_btn.visible = False
            page.update()
            
            # Focus on the very first box automatically
            otp_boxes[0].focus()
            page.update()

        def on_register_submit(e):
            collected_otp = "".join(box.value.strip().upper() for box in otp_boxes)
            if collected_otp == app_state["generated_otp"]:
                app_state["database"][app_state["user_phone"]] = app_state["user_name"]
                sms_status.value = "Registration verified! Redirecting..."
                page.update()
                import time
                time.sleep(1)
                route_to("login")
            else:
                error_msg.value = "Validation Error: Code mismatch."
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

    page.title = "Salon Core Application"
    page.window_width = 400
    page.window_height = 740
    page.window_resizable = False
    page.add(build_login_screen())

if __name__ == "__main__":
    ft.app(target=main)