import flet as ft
import requests
import threading

def build_dashboard_screen(page: ft.Page, route_to_callback=None, app_state=None):
    if app_state is None:
        app_state = {}
    
    # --- Status Messages ---
    loading_indicator = ft.ProgressRing(visible=True, width=30, height=30)
    error_display = ft.Text("", color=ft.Colors.RED_800, size=13, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    salon_cards_list = ft.Column(spacing=15)
    
    # Location state variables
    location_permission_granted = False
    current_location = "Location not specified"
    location_display = ft.Text(
        "Location not specified",
        size=13,
        color=ft.Colors.GREY_600,
        weight=ft.FontWeight.BOLD
    )
    
    dashboard_content = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        visible=True
    )

    # Get user's actual location via IP API safely
    def get_user_location():
        nonlocal current_location
        try:
            response = requests.get("https://ipapi.co/json/", timeout=3)
            if response.status_code == 200:
                data = response.json()
                city = data.get("city", "Unknown")
                country = data.get("country_name", "Unknown")
                current_location = f"{city}, {country}"
                print(f"✅ Location detected: {current_location}")
            else:
                current_location = "Location not specified"
        except Exception as e:
            print(f"⚠️ Could not get location: {str(e)}")
            current_location = "Location not specified"

    # Location Permission Dialog Flow
    def show_location_permission_dialog():
        nonlocal location_permission_granted
        
        def allow_location(e):
            nonlocal location_permission_granted
            location_permission_granted = True
            location_dialog.open = False
            location_display.value = "📍 Getting location..."
            page.update()
            
            # Use Flet's managed thread handler instead of raw threading.Thread
            def fetch_location():
                get_user_location()
                location_display.value = f"📍 {current_location}"
                page.update()
            
            page.run_thread(fetch_location)
        
        def deny_location(e):
            nonlocal location_permission_granted
            location_permission_granted = False
            location_dialog.open = False
            location_display.value = "📍 Location not specified"
            page.update()
        
        location_dialog = ft.AlertDialog(
            title=ft.Text("Compass Access Your Location?", weight=ft.FontWeight.BOLD, size=16),
            content=ft.Text(
                "We need your location to show nearby salons and hair stylists. "
                "Your location will only be used to improve your experience.",
                size=13,
                color=ft.Colors.GREY_700
            ),
            actions=[
                ft.TextButton(
                    "Don't Allow",
                    on_click=deny_location,
                    style=ft.ButtonStyle(color=ft.Colors.GREY_600)
                ),
                ft.ElevatedButton(
                    "Allow Location Access",
                    on_click=allow_location,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = location_dialog
        location_dialog.open = True
        page.update()

    # Live Data Engine Fetcher
    def load_live_salons():
        try:
            print("🔄 Fetching salons from backend...")
            loading_indicator.visible = True
            error_display.value = ""
            page.update()
            
            response = requests.get(
                "http://127.0.0.1:8000/api/salons/nearby",
                timeout=5
            )
            
            print(f"✅ API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                salons_data = response.json()
                print(f"✅ Received {len(salons_data)} salons")
                salon_cards_list.controls.clear()
                
                if not salons_data:
                    salon_cards_list.controls.append(
                        ft.Text("❌ No salons found in database.", color=ft.Colors.GREY_600, size=14)
                    )
                else:
                    for salon in salons_data:
                        card = ft.Container(
                            content=ft.Column([
                                ft.Stack([
                                    ft.Image(
                                        src=salon.get("image") if salon.get("image") else "https://picsum.photos/300/200", 
                                        width=float("inf"), 
                                        height=140, 
                                        fit=ft.ImageFit.COVER
                                    ),
                                    ft.Container(
                                        content=ft.Text(salon.get("tag", "Salon"), size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                        bgcolor=ft.Colors.GREEN_700, padding=6, border_radius=6, top=10, left=10
                                    ),
                                    ft.Container(
                                        content=ft.Text(salon.get("eta", "-- mins"), size=11, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
                                        bgcolor=ft.Colors.WHITE, padding=6, border_radius=6, bottom=10, right=10
                                    )
                                ]),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Column([
                                                ft.Text(salon.get("name", "Unknown Salon"), size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                                ft.Text(f"{salon.get('distance', '0 km')} away", size=12, color=ft.Colors.GREY_600)
                                            ], expand=True),
                                            ft.Column([
                                                ft.Row([
                                                    ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=18),
                                                    ft.Text(salon.get("rating", "5.0"), size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
                                                ], spacing=2),
                                                ft.Text(f"({salon.get('reviews', '0')} reviews)", size=11, color=ft.Colors.GREY_600)
                                            ])
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                        ft.Container(height=5),
                                        ft.Text(salon.get("price_tier", "Rs. --"), size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
                                    ]),
                                    padding=12
                                )
                            ]),
                            bgcolor=ft.Colors.WHITE,
                            border_radius=14,
                            border=ft.Border(ft.BorderSide(1, ft.Colors.GREY_300)),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                        )
                        salon_cards_list.controls.append(card)
                print(f"✅ Added {len(salon_cards_list.controls)} salon cards to UI")
            else:
                error_display.value = f"❌ Server Error {response.status_code}"
                
        except Exception as ex:
            print(f"Exception details: {str(ex)}")
            error_display.value = "❌ Backend Connection Failed. Check server.py"
        
        finally:
            loading_indicator.visible = False
            try:
                page.update()
            except:
                pass

    # Header Control Generator
    def create_header():
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NOT_LISTED_LOCATION, color=ft.Colors.RED, size=18),
                        location_display  
                    ], spacing=4),
                    ft.Text("Current Location", size=12, color=ft.Colors.GREY_700, weight=ft.FontWeight.W_600)
                ], spacing=2),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT_ROUNDED, 
                    icon_color=ft.Colors.RED_800,
                    tooltip="Logout",
                    on_click=lambda _: route_to_callback("login") if route_to_callback else None
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding(left=0, top=0, right=0, bottom=15)
        )

    # Categories Row Slider
    service_categories = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CONTENT_CUT, color=ft.Colors.WHITE, size=28),
                ft.Text("Haircut", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=75, height=75, bgcolor=ft.Colors.BLUE_900, border_radius=12, ink=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.FACE, color=ft.Colors.BLACK, size=28),
                ft.Text("Facial", color=ft.Colors.BLACK, size=11, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=75, height=75, bgcolor=ft.Colors.GREY_200, border_radius=12, ink=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SPA, color=ft.Colors.BLACK, size=28),
                ft.Text("Massage", color=ft.Colors.BLACK, size=11, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=75, height=75, bgcolor=ft.Colors.GREY_200, border_radius=12, ink=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.BRUSH, color=ft.Colors.BLACK, size=28),
                ft.Text("Makeup", color=ft.Colors.BLACK, size=11, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=75, height=75, bgcolor=ft.Colors.GREY_200, border_radius=12, ink=True
        )
    ], scroll=ft.ScrollMode.HIDDEN, spacing=10)

    display_username = app_state.get("user_name") or app_state.get("name") or "Customer"

    dashboard_content.controls = [
        create_header(),  
        ft.Text(f"Welcome, {display_username} 👋", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
        ft.Container(height=10),
        ft.Text("Explore Services", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
        ft.Container(height=5),
        service_categories,
        ft.Container(height=20),
        ft.Row([loading_indicator, error_display], alignment=ft.MainAxisAlignment.CENTER),
        ft.Text("Nearest Active Salons Around You", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
        ft.Container(height=8),
        salon_cards_list
    ]
    
    # Thread-Safe Post-Render Initializer Flow
    def init_dashboard():
        show_location_permission_dialog()
        load_live_salons()
    
    # ✅ FIX: Uses Flet's safe internal thread messenger to map view sequences
    page.run_thread(init_dashboard)

    return ft.Container(
        content=dashboard_content,
        padding=16,
        expand=True,
        bgcolor=ft.Colors.GREY_50
    )

if __name__ == "__main__":
    def sandbox_main(page: ft.Page):
        page.title = "Dashboard Sandbox Live View"
        page.window_width = 400
        page.window_height = 740
        page.window_resizable = False
        
        mock_state = {"user_name": "Test Account"}
        page.add(build_dashboard_screen(page, route_to_callback=None, app_state=mock_state))
        page.update()

    # ✅ FIX: Changed ft.run() to modern thread-safe ft.app() configuration
    ft.app(target=sandbox_main)