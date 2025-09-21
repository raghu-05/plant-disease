import os
import threading
import requests
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel,MDIcon
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.graphics import Rectangle, Color, PushMatrix, PopMatrix, Rotate, Ellipse
from kivy.uix.label import Label
from kivymd.uix.card import MDCard
from kivy.animation import Animation
from kivy.uix.widget import Widget
from random import randint, uniform
from kivy.uix.textinput import TextInput
from kivymd.uix.boxlayout import MDBoxLayout
import shutil
#from kivymd.uix.icon import MDIcon
from kivy.utils import get_color_from_hex

# Imports for Permissions, Camera, and File Handling
from kivy.utils import platform
from plyer import filechooser, camera

# Imports only needed for Android
if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import app_storage_path
    from jnius import autoclass, cast


class SparkleParticle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (randint(2, 5), randint(2, 5))
        self.pos = (randint(0, 800), randint(0, 1200))
        self.speed = uniform(0.2, 0.8)
        self.sway = uniform(-0.3, 0.3)
        self.alpha = uniform(0.3, 0.9)
        self.alpha_change = uniform(0.01, 0.03)  # flicker speed
        with self.canvas:
            self.color = Color(1, 1, 1, self.alpha)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

    def move(self):
        x, y = self.pos
        x += self.sway
        y -= self.speed
        if y < -self.size[1]:
            y = 1200
            x = randint(0, 800)
            self.speed = uniform(0.2, 0.8)
            self.sway = uniform(-0.3, 0.3)
        self.pos = (x, y)
        self.ellipse.pos = self.pos
        self.alpha += self.alpha_change
        if self.alpha > 0.9 or self.alpha < 0.3:
            self.alpha_change *= -1
        self.color.a = self.alpha

class DustParticle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (randint(2, 6), randint(2, 6))
        self.pos = (randint(0, 800), randint(0, 1200))
        self.speed = uniform(0.5, 1.5)
        self.sway = uniform(-0.5, 0.5)
        with self.canvas:
            Color(1, 1, 0.8, uniform(0.3, 0.7))
            self.ellipse = Ellipse(pos=self.pos, size=self.size)

    def move(self):
        x, y = self.pos
        x += self.sway
        y -= self.speed
        if y < -self.size[1]:
            y = 1200
            x = randint(0, 800)
            self.speed = uniform(0.5, 1.5)
            self.sway = uniform(-0.5, 0.5)
        self.pos = (x, y)
        self.ellipse.pos = self.pos

class LeafParticle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (randint(20, 40), randint(10, 25))
        self.pos = (randint(0, 800), randint(0, 1200))
        self.speed = uniform(1, 3)
        self.sway = uniform(-1, 1)
        self.rotation_angle = uniform(0, 360)
        self.rotation_speed = uniform(-2, 2)
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=self.rotation_angle, origin=self.center)
            Color(uniform(0.0, 0.5), uniform(0.3, 0.8), uniform(0.0, 0.2), 0.8)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            PopMatrix()

    def move(self):
        x, y = self.pos
        x += self.sway
        y -= self.speed
        self.rotation_angle += self.rotation_speed
        if y < -self.size[1]:
            y = 1200
            x = randint(0, 800)
            self.speed = uniform(1, 3)
            self.sway = uniform(-1, 1)
            self.size = (randint(20, 40), randint(10, 25))
        self.pos = (x, y)
        self.rect.pos = self.pos
        self.rot.angle = self.rotation_angle
        self.rot.origin = self.center


# ---------------- About Screen ----------------
class AboutScreen(Screen):
    def __init__(self, content_sm, **kwargs):
        super().__init__(name="about", **kwargs)
        self.content_sm = content_sm
        self.md_bg_color = get_color_from_hex("#E8F5E9") 

        root_layout = MDBoxLayout(orientation="vertical")
        
        top_bar = MDTopAppBar(
            title="About AgroDoctor",
            elevation=4,
            left_action_items=[["arrow-left", lambda x: self.go_home()]]
        )
        
        scroll = MDScrollView()
        
        content_layout = MDBoxLayout(
            orientation='vertical',
            padding="20dp",
            spacing="20dp",
            adaptive_height=True
        )

        # --- Intro Card ---
        intro_card = MDCard(padding="15dp", md_bg_color=(1,1,1,1), elevation=2, adaptive_height=True)
        intro_text = (
            "[b] AgroDoctor[/b]\n\n"
            "An innovative AI-powered platform designed to empower farmers with modern technology. "
            "It acts as a digital farming companion, helping identify plant diseases quickly and providing "
            "instant treatment solutions in multiple languages and the medication cost."
        )
        intro_card.add_widget(MDLabel(text=intro_text, markup=True, halign="center", adaptive_height=True))
        content_layout.add_widget(intro_card)

        # --- "Why AgroDoctor?" Card ---
        why_card = MDCard(padding="15dp", md_bg_color=(1,1,1,1), elevation=2, adaptive_height=True)
        why_text = (
            "[b][u] Why AgroDoctor?[/u][/b]\n\n"
            "Farming communities often face challenges like late disease detection, lack of expert guidance, "
            "and language barriers. AgroDoctor bridges this gap by combining Artificial Intelligence and "
            "Generative AI to deliver accurate, reliable, and farmer-friendly support right in their hands."
        )
        why_card.add_widget(MDLabel(text=why_text, markup=True, adaptive_height=True))
        content_layout.add_widget(why_card)

        # --- Core Features Section ---
        content_layout.add_widget(MDLabel(text="Core Features", font_style="H5", halign="center", adaptive_height=True, padding=("0dp", "15dp")))

        content_layout.add_widget(self.create_feature_card(
            "robot-love-outline", "AI Diagnosis", "Detects leaf diseases using advanced Machine Learning models."
        ))
        content_layout.add_widget(self.create_feature_card(
            "head-sync-outline", "Generative AI Guidance", "Provides clear treatment plans in English, Hindi, and Telugu."
        ))
        content_layout.add_widget(self.create_feature_card(
            "cellphone-check", "Farmer-Centric Design", "Simple, mobile-ready interface for easy use in the field."
        ))
        content_layout.add_widget(self.create_feature_card(
            "database-cog-outline", "Full-Stack Solution", "Powered by Python, ML, and an intuitive frontend."
        ))

        # --- "Developed by" Card ---
        dev_card = MDCard(padding="15dp", md_bg_color=(1,1,1,1), elevation=2, adaptive_height=True)
        dev_text = (
            "[b] Developed by:[/b]\n"
            "    • Arja Raghuveer\n"
            "    • Tanuja\n"
            "    • Prabhu\n"
            "    • Pavan"
        )
        dev_card.add_widget(MDLabel(text=dev_text, markup=True, adaptive_height=True))
        content_layout.add_widget(dev_card)
        
        # --- Contact Us Button (Restored) ---
        contact_btn = MDRaisedButton(text="Contact Us", pos_hint={"center_x": 0.5}, size_hint_x=None, width="200dp")
        contact_btn.bind(on_release=self.show_contact_dialog)
        content_layout.add_widget(contact_btn)

        scroll.add_widget(content_layout)
        root_layout.add_widget(top_bar)
        root_layout.add_widget(scroll)
        self.add_widget(root_layout)
        
    def create_feature_card(self, icon_name, title_text, body_text):
        """A helper function to create a consistent card for each feature."""
        card = MDCard(
            orientation='vertical',
            padding="15dp",
            spacing="5dp",
            size_hint_y=None,
            adaptive_height=True, # <-- FIX: Make card height adaptive
            md_bg_color=(1,1,1,1),
            elevation=2
        )
        
        header_layout = MDBoxLayout(adaptive_height=True, spacing="15dp")
        header_layout.add_widget(MDIcon(icon=icon_name, size_hint=(None, None), size=("40dp", "40dp")))
        header_layout.add_widget(MDLabel(text=title_text, font_style="H6", adaptive_height=True))
        
        card.add_widget(header_layout)
        card.add_widget(MDLabel(text=body_text, theme_text_color="Secondary", adaptive_height=True)) # <-- FIX: Make label height adaptive
        
        return card

    def go_home(self):
        if self.content_sm:
            self.content_sm.transition.direction = "right"
            self.content_sm.current = "home"
            

    def show_contact_dialog(self, *args):
        # Scrollable layout for mobile
        scroll_layout = MDScrollView(size_hint=(1, None), height="350dp")
        
        layout = MDBoxLayout(
            orientation="vertical",
            spacing="15dp",
            padding=("15dp", "15dp", "15dp", "15dp"),
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter('height'))

        # Name
        layout.add_widget(Label(
            text="Your Name:",
            size_hint_y=None, height="20dp",
            color=(0,0,0,1)
        ))
        self.name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height="40dp",
            padding=(10,10),
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1),
            cursor_color=(0,0,0,1)
        )
        layout.add_widget(self.name_input)

        # Email
        layout.add_widget(Label(
            text="Your Email:",
            size_hint_y=None, height="20dp",
            color=(0,0,0,1)
        ))
        self.email_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height="40dp",
            padding=(10,10),
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1),
            cursor_color=(0,0,0,1)
        )
        layout.add_widget(self.email_input)

        # Message
        layout.add_widget(Label(
            text="Your Message:",
            size_hint_y=None, height="20dp",
            color=(0,0,0,1)
        ))
        self.message_input = TextInput(
            multiline=True,
            size_hint_y=None,
            height="120dp",
            padding=(10,10),
            background_color=(1,1,1,1),
            foreground_color=(0,0,0,1),
            cursor_color=(0,0,0,1)
        )
        layout.add_widget(self.message_input)

        scroll_layout.add_widget(layout)

        # Dialog
        self.dialog = MDDialog(
            title="Contact Us",
            type="custom",
            content_cls=scroll_layout,
            buttons=[
                MDRaisedButton(
                    text="Submit",
                    md_bg_color=(0, 0.6, 0, 1),
                    text_color=(1,1,1,1),
                    on_release=self.submit_feedback
                ),
                MDRaisedButton(
                    text="Close",
                    md_bg_color=(0.8,0.8,0.8,1),
                    text_color=(0,0,0,1),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()


    def submit_feedback(self, *args):
        name = self.name_input.text.strip()
        email = self.email_input.text.strip()
        message = self.message_input.text.strip()

        if not name or not email or not message:
            from kivymd.toast import toast
            toast("Please fill all fields!")
            return
        feedback_data = {
            "name": name,
            "email": email,
            "message": message
        }
    

        threading.Thread(target=self.send_data_to_backend, args=(feedback_data,)).start()
        self.dialog.dismiss()

    def send_data_to_backend(self, data):
    # Your unique Getform URL goes here
        api_url = "https://getform.io/f/awnyrxqb"  # <-- THIS IS THE ONLY CHANGE
        
        try:
            response = requests.post(api_url, json=data, timeout=30)
            if response.status_code == 200:
                Clock.schedule_once(lambda dt: self.show_submission_toast("Feedback submitted successfully!"))
            else:
                Clock.schedule_once(lambda dt: self.show_submission_toast(f"Error: {response.text}"))
        except requests.exceptions.RequestException as e:
            Clock.schedule_once(lambda dt: self.show_submission_toast("Network Error. Please try again."))
            print(f"Feedback submission error: {e}")

    def show_submission_toast(self, message):
        from kivymd.toast import toast
        toast(message)

# ---------------- Splash Screen ----------------
class SplashScreen(Screen):
    # This class is unchanged
    def on_enter(self, *args):
        if not hasattr(self, "logo_added"):
            logo = Image(source="logo.png", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.5, 0.5))
            self.add_widget(logo)
            self.logo_added = True
        Clock.schedule_once(self.switch_to_main, 2.0)

    def switch_to_main(self, dt):
        if self.manager:
            self.manager.transition = FadeTransition(duration=0.4)
            self.manager.current = "main_screen"


# ---------------- Main App ----------------
class AgroDoctorApp(MDApp):
    dialog = None
    # <-- NEW FUNCTION to request permissions when the app starts.
    def on_start(self):
        if platform == "android":
            permissions = [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA
            ]
            request_permissions(permissions)

    def build(self):
        # This part is unchanged
        font_path = os.path.dirname(__file__)
        try:
            LabelBase.register(name="NotoSans", fn_regular=os.path.join(font_path, "NotoSans-Regular.ttf"))
            LabelBase.register(name="NotoSansTelugu", fn_regular=os.path.join(font_path, "Mandali-Regular.ttf"))
            LabelBase.register(name="NotoSansDevanagari", fn_regular=os.path.join(font_path, "NotoSansDevanagari-Regular.ttf"))
            self.theme_cls.font_name = "NotoSans"
        except Exception:
            pass
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.sm = ScreenManager()
        self.sm.add_widget(SplashScreen(name="splash"))
        self.sm.add_widget(self.build_main_screen())
        return self.sm

    # ---------------- Main screen ----------------
    def build_main_screen(self):
        main_screen = Screen(name="main_screen")
        self.content_sm = ScreenManager()
        self.content_sm.add_widget(self.build_home_screen())
        self.content_sm.add_widget(AboutScreen(content_sm=self.content_sm))
        main_screen.add_widget(self.content_sm)
        return main_screen

    # ---------------- Home Screen ----------------
    def build_home_screen(self):
        home = Screen(name="home")
        # Canvas and particle setup is unchanged
        with home.canvas.before:
            try:
                self.bg_rect = Rectangle(source="background.jpg", pos=home.pos, size=home.size)
            except Exception:
                self.bg_rect = Rectangle(pos=home.pos, size=home.size)
            self.overlay = Color(0, 0, 0, 0.4)
            self.overlay_rect = Rectangle(pos=home.pos, size=home.size)
        home.bind(size=self.update_bg, pos=self.update_bg)
        anim_bg = Animation(pos=(self.bg_rect.pos[0], self.bg_rect.pos[1]+10), duration=2) + Animation(pos=(self.bg_rect.pos[0], self.bg_rect.pos[1]-10), duration=2)
        anim_bg.repeat = True
        anim_bg.start(self.bg_rect)
        root_layout = BoxLayout(orientation="vertical")
        self.particles = [LeafParticle() for _ in range(25)]
        self.dust_particles = [DustParticle() for _ in range(50)]
        self.sparkles = [SparkleParticle() for _ in range(40)]
        for p in self.particles + self.dust_particles + self.sparkles:
            home.add_widget(p)
        Clock.schedule_interval(self.update_particles, 1/30)
        
        # Top bar and card setup is unchanged
        self.top_bar = MDTopAppBar(title="AgroDoctor", elevation=4, left_action_items=[["logo.png", lambda x: None]], right_action_items=[["information", lambda x: self.switch_to_about()]])
        self.top_bar.ids.label_title.font_size = "32sp"
        root_layout.add_widget(self.top_bar)
        content_layout = BoxLayout(orientation="vertical", padding="20dp", spacing="20dp")
        self.image_card = MDCard(orientation="vertical", padding="10dp", elevation=8, radius=[25, 25, 25, 25], md_bg_color=(1, 1, 1, 0.12))
        self.image_display = Image(source="placeholder.png")
        self.result_label = MDLabel(text="Upload a leaf image to begin", halign="center", font_style="H6", size_hint_y=None, height="40dp", adaptive_height=True, theme_text_color="Custom", text_color=(1, 1, 1, 1))
        self.image_card.add_widget(self.image_display)
        self.image_card.add_widget(self.result_label)
        
        # Button setup is MODIFIED
        button_layout = BoxLayout(orientation="horizontal", spacing="10dp", size_hint_y=None, height="50dp")
        
        # <-- MODIFIED 'on_release' to call the new dialog function
        select_button = MDFillRoundFlatIconButton(
            text="Select", icon="image-search-outline",
            on_release=self.open_selection_dialog, # This now calls the dialog
            size_hint=(1, 1)
        )
        select_button.ripple_color = (0, 1, 0, 0.3)

        self.diagnose_button = MDFillRoundFlatIconButton(text="Diagnose", icon="magnify", on_release=self.diagnose_disease_thread, disabled=True, size_hint=(1, 1))
        self.treatment_button = MDFillRoundFlatIconButton(text="Get Plan", icon="pill", on_release=self.open_language_dialog, disabled=True, size_hint=(1, 1))

        button_layout.add_widget(select_button)
        button_layout.add_widget(self.diagnose_button)
        button_layout.add_widget(self.treatment_button)
        content_layout.add_widget(self.image_card)
        content_layout.add_widget(button_layout)
        root_layout.add_widget(content_layout)
        home.add_widget(root_layout)
        return home

    # ---------------- Particle updater ----------------
    def update_particles(self, dt):
        for p in getattr(self, "particles", []):
            p.move()
        for d in getattr(self, "dust_particles", []):
            d.move()
        for s in getattr(self, "sparkles", []):
            s.move()


    # ---------------- About Button ----------------
    def switch_to_about(self):
        if hasattr(self, "content_sm"):
            self.content_sm.transition.direction = "left"
            self.content_sm.current = "about"

    # ---------------- Background updater ----------------
    def update_bg(self, *args):
        try:
            if hasattr(self, "bg_rect"):
                self.bg_rect.pos = args[0].pos if args else self.bg_rect.pos
                self.bg_rect.size = args[0].size if args else self.bg_rect.size
            if hasattr(self, "overlay_rect"):
                self.overlay_rect.pos = args[0].pos if args else self.overlay_rect.pos
                self.overlay_rect.size = args[0].size if args else self.overlay_rect.size
        except Exception:
            pass

    # ---------------- File Selection ----------------
    def open_selection_dialog(self, *args):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Choose Image Source",
                type="simple",
                buttons=[
                    MDRaisedButton(
                        text="Take Picture",
                        on_release=self.take_picture,
                    ),
                    MDRaisedButton(
                        text="Select from Gallery",
                        on_release=self.select_image,
                    ),
                ],
            )
        self.dialog.open()

    # <-- NEW FUNCTION to handle taking a picture ---
    def take_picture(self, bottom_sheet):
        if self.dialog:
            self.dialog.dismiss()
        
        if platform == "android":
            image_path = os.path.join(app_storage_path(), 'camera_capture.jpg')
            try:
                camera.take_picture(filename=image_path, on_complete=self.handle_camera_capture)
            except Exception as e:
                self.result_label.text = "Could not open camera."
                print(f"Camera error: {e}")


    # <-- NEW FUNCTION to handle the camera result ---
    def handle_camera_capture(self, filepath):
        if filepath and os.path.exists(filepath):
            self.handle_selection([filepath])

    # <-- MODIFIED 'select_image' to handle the bottom sheet ---
    def select_image(self, bottom_sheet):
        if self.dialog:
            self.dialog.dismiss()

        self.diagnose_button.disabled = True
        self.treatment_button.disabled = True
        self.predicted_disease = None
        filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self, selection):
        if not selection:
            self.result_label.text = "No file selected."
            return

        source_path = selection[0]

        if platform == "android":
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                cr = PythonActivity.mActivity.getContentResolver()
                input_stream = cr.openInputStream(autoclass('android.net.Uri').parse(source_path))
                temp_file_path = os.path.join(app_storage_path(), 'temp_image.jpg')
                
                with open(temp_file_path, 'wb') as f:
                    shutil.copyfileobj(input_stream, f)
                
                input_stream.close()
                self.selected_path = temp_file_path
            except Exception as e:
                self.result_label.text = "Error: Could not load image."
                print(f"File handling error: {e}")
                return
        else: # For PC testing
            self.selected_path = source_path
        
        self.image_display.source = self.selected_path
        self.image_display.reload()
        self.result_label.text = "Image ready for diagnosis."
        self.diagnose_button.disabled = False

        anim = Animation(size=(self.image_display.width * 1.05, self.image_display.height * 1.05), duration=0.15) + \
               Animation(size=(self.image_display.width, self.image_display.height), duration=0.15)
        anim.start(self.image_display)

    # ---------------- Diagnosis ----------------
    def diagnose_disease_thread(self, *args):
        threading.Thread(target=self.diagnose_disease, daemon=True).start()

    def diagnose_disease(self):
        if not getattr(self, "selected_path", None):
            return
        Clock.schedule_once(lambda dt: self.show_dialog("Diagnosing...", "Please wait.", is_loading=True))
        api_url = "https://agrodoctor-api-raghu.onrender.com/predict_disease"
        try:
            with open(self.selected_path, "rb") as f:
                files = {"file": (os.path.basename(self.selected_path), f, "image/jpeg")}
                response = requests.post(api_url, files=files, timeout=30)
            Clock.schedule_once(lambda dt: self._handle_prediction_response(response))
        except requests.exceptions.RequestException:
            Clock.schedule_once(lambda dt: self._dismiss_and_set_text("Network Error"))

    def _handle_prediction_response(self, response):
        try: self.dialog.dismiss()
        except Exception: pass
        if response.status_code == 200:
            result = response.json()
            self.predicted_disease = result.get("predicted_disease", "N/A")
            confidence = result.get("confidence", 0) * 100
            self.result_label.text = f"Disease: {self.predicted_disease}\nConfidence: {confidence:.2f}%"
            self.treatment_button.disabled = False
        else:
            self.result_label.text = f"Error: Received status code {response.status_code}"

    def _dismiss_and_set_text(self, text):
        try: self.dialog.dismiss()
        except Exception: pass
        self.result_label.text = text

    # ---------------- Treatment Dialogs ----------------
    def open_language_dialog(self, *args):
        if not getattr(self, "predicted_disease", None):
            return
        layout = BoxLayout(orientation="horizontal", spacing="10dp", size_hint_y=None, height="50dp")
        for lang in ["Telugu", "English", "Hindi"]:
            btn = MDRaisedButton(text=lang)
            btn.bind(on_release=lambda x, l=lang: self.fetch_plan_in_language(l))
            layout.add_widget(btn)
        self.dialog = MDDialog(title="Choose Language", type="custom", content_cls=layout,
                               buttons=[MDRaisedButton(text="Cancel", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def fetch_plan_in_language(self, language):
        try: self.dialog.dismiss()
        except Exception: pass
        threading.Thread(target=self.execute_get_treatment, args=(language,), daemon=True).start()

    def execute_get_treatment(self, language):
        Clock.schedule_once(lambda dt: self.show_dialog(f"Fetching in {language}...", "Please wait.", is_loading=True))
        api_url = f"https://agrodoctor-api-raghu.onrender.com/get_treatment?disease_name={self.predicted_disease}&language={language}"
        try:
            response = requests.get(api_url, timeout=60)
            Clock.schedule_once(lambda dt: self._handle_treatment_response(response, language))
        except requests.exceptions.RequestException:
            Clock.schedule_once(lambda dt: self._dismiss_and_show_message("Network Error"))

    # Replace your existing function with this one
    def _handle_treatment_response(self, response, language):
        try:
            self.dialog.dismiss()
        except Exception:
            pass

        if response.status_code == 200:
            result = response.json()
            plan = result.get("treatment_plan", "No plan found.")
            
            # <-- NEW: Store the plan text so we can access it later
            self.current_plan_text = plan

            # --- This is the part that creates the dialog ---
            font_to_use = {"Telugu": "NotoSansTelugu", "Hindi": "NotoSansDevanagari"}.get(language, "NotoSans")
            content_label = Label(text=plan, size_hint_y=None, font_name=font_to_use, color=(0, 0, 0, 1), font_size="16sp")
            content_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
            content_label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
            
            scroll = MDScrollView(size_hint_y=None, height="400dp")
            scroll.add_widget(content_label)

            # <-- NEW: Add a "Download" button to this list
            self.dialog = MDDialog(
                title=f"Plan for {self.predicted_disease}",
                type="custom",
                content_cls=scroll,
                buttons=[
                    MDRaisedButton(
                        text="Download",
                        on_release=self.download_plan
                    ),
                    MDRaisedButton(
                        text="Close",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()
        else:
            Clock.schedule_once(lambda dt: self.show_dialog("Error", "Could not get plan."))

    # Add this new function inside your AgroDoctorApp class
    def download_plan(self, *args):
        """Saves the current treatment plan to the Downloads folder."""
        from kivymd.toast import toast
        plan_text = getattr(self, "current_plan_text", "No plan available to save.")
        disease_name = getattr(self, "predicted_disease", "plant").replace("___", "_")
        filename = f"AgroDoctor_Plan_{disease_name}.txt"

        if platform == "android":
            try:
                # Use Android's MediaStore API for modern, safe file saving
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Context = autoclass('android.content.Context')
                Environment = autoclass('android.os.Environment')
                MediaStore = autoclass('android.provider.MediaStore')
                ContentValues = autoclass('android.content.ContentValues')
                
                content_resolver = PythonActivity.mActivity.getContentResolver()
                
                values = ContentValues()
                values.put(MediaStore.MediaColumns.DISPLAY_NAME, filename)
                values.put(MediaStore.MediaColumns.MIME_TYPE, "text/plain")
                values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
                
                uri = content_resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                
                output_stream = content_resolver.openOutputStream(uri)
                output_stream.write(plan_text.encode('utf-8'))
                output_stream.close()
                
                toast(f"Plan saved to Downloads folder as {filename}")

            except Exception as e:
                toast("Error: Could not save file.")
                print(f"Android file save error: {e}")
                
        else: # For testing on PC
            try:
                downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
                if not os.path.exists(downloads_path):
                    os.makedirs(downloads_path) # Create Downloads folder if it doesn't exist
                
                file_path = os.path.join(downloads_path, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(plan_text)
                
                toast(f"Plan saved to {file_path}")
            except Exception as e:
                toast("Error: Could not save file on PC.")
                print(f"PC file save error: {e}")

    def _dismiss_and_show_message(self, text):
        try: self.dialog.dismiss()
        except Exception: pass
        self.show_dialog("Error", text)

    # ---------------- General Dialog ----------------
    def show_dialog(self, title, text, is_loading=False, language="English"):
        try: self.dialog.dismiss()
        except Exception: pass

        if is_loading:
            from kivymd.uix.spinner import MDSpinner
            spinner = MDSpinner(size_hint=(None, None), size=("48dp", "48dp"))
            spinner.color = (0, 1, 0, 1)
            self.dialog = MDDialog(title=title, type="custom", content_cls=spinner)
        else:
            font_to_use = {"Telugu": "NotoSansTelugu", "Hindi": "NotoSansDevanagari"}.get(language, "NotoSans")
            content_label = Label(text=text, size_hint_y=None, font_name=font_to_use,
                                  color=(1, 1, 1, 1) if self.theme_cls.theme_style == "Dark" else (0, 0, 0, 1),
                                  font_size="16sp")
            content_label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
            content_label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
            scroll = MDScrollView(size_hint_y=None, height="400dp")
            scroll.add_widget(content_label)
            self.dialog = MDDialog(title=title, type="custom", content_cls=scroll,
                                   buttons=[MDRaisedButton(text="Close", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()


# ---------------- Run App ----------------
if __name__ == "__main__":
    if not os.path.exists("placeholder.png"):
        from PIL import Image as PILImage
        img = PILImage.new("RGB", (200, 200), color="white")
        img.save("placeholder.png")
    if not os.path.exists("background.jpg"):
        from PIL import Image as PILImage
        img = PILImage.new("RGB", (800, 1200), color = (27, 94, 32))
        img.save("background.jpg")
    AgroDoctorApp().run()
