import flet as ft
import requests
import threading  # ✅ FIXED: Imported threading module

def build_dashboard_screen(page: ft.Page, route_to_callback=None, app_state=None):
    if app_state is None:
        app_state = {}
    
    # --- Status Messages ---
    loading_indicator = ft.ProgressRing(visible=True, width=30, height=30)
    error_display = ft.Text("", color=ft.Colors.RED_800, size=13, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    salon_cards_list = ft.Column(spacing=15)
    
    dashboard_content = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        visible=True
    )

    # --- Live Data Engine Fetcher ---
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
                                        content=ft.Text(
                                            salon.get("tag", "Salon"),
                                            size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
                                        ),
                                        bgcolor=ft.Colors.GREEN_700, padding=6, border_radius=6, top=10, left=10
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            salon.get("eta", "-- mins"),
                                            size=11, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD
                                        ),
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
                error_msg = f"❌ Server Error {response.status_code}"
                error_display.value = error_msg
                
        except Exception as ex:
            error_msg = "❌ Backend Connection Failed. Check server.py"
            print(f"Exception details: {str(ex)}")
            error_display.value = error_msg
        
        finally:
            loading_indicator.visible = False
            try:
                page.update()
            except Exception:
                pass

    # --- Header Navigation Bar ---
    header_section = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.NOT_LISTED_LOCATION, color=ft.Colors.RED, size=18),
                    ft.Text("Current Location 📍", size=11, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD),
                ], spacing=4),
                ft.Text("Kathmandu, Nepal", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
            ]),
            ft.IconButton(
                icon=ft.Icons.LOGOUT_ROUNDED, 
                icon_color=ft.Colors.RED_800,
                tooltip="Logout",
                on_click=lambda _: route_to_callback("login") if route_to_callback else None
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding(left=0, top=0, right=0, bottom=15)
    )

    # --- Horizontal Quick Filters Slider ---
    service_categories = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CONTENT_CUT, color=ft.Colors.WHITE, size=28),
                ft.Text("Haircut", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=75, height=75, bgcolor=ft.Colors.BLUE_900, border_radius=12, ink=True,
            on_click=lambda _: print("Haircut filter selected")
        ),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.FACE, color=ft.Colors.BLACK, size=28),
                ft.Text("Facial", color=ft.Colors.BLACK, size=11, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=75, height=75, bgcolor=ft.Colors.GREY_200, border_radius=12, ink=True,
            on_click=lambda _: print("Facial filter selected")
        ),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SPA, color=ft.Colors.BLACK, size=28),
                ft.Text("Massage", color=ft.Colors.BLACK, size=11, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=75, height=75, bgcolor=ft.Colors.GREY_200, border_radius=12, ink=True,
            on_click=lambda _: print("Massage filter selected")
        ),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.BRUSH, color=ft.Colors.BLACK, size=28),
                ft.Text("Makeup", color=ft.Colors.BLACK, size=11, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=75, height=75, bgcolor=ft.Colors.GREY_200, border_radius=12, ink=True,
            on_click=lambda _: print("Makeup filter selected")
        )
    ], scroll=ft.ScrollMode.HIDDEN, spacing=10)

    display_username = app_state.get("user_name") or app_state.get("name") or "Customer"

    dashboard_content.controls = [
        header_section,
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
    
    # ✅ FIXED HERE: Using standard threading instead of page.run_task for synchronous function
    threading.Thread(target=load_live_salons, daemon=True).start()

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

    ft.run(sandbox_main)