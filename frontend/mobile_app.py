# frontend/mobile_app.py (updated with particle animations)
import os
import threading
import requests
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label
from kivymd.uix.card import MDCard
from kivy.animation import Animation
from kivy.uix.widget import Widget
from random import randint, uniform
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout


# ---------------- Particle System ----------------
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, PushMatrix, PopMatrix, Rotate, Ellipse
from random import randint, uniform

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

        # Flicker effect
        self.alpha += self.alpha_change
        if self.alpha > 0.9 or self.alpha < 0.3:
            self.alpha_change *= -1
        self.color.a = self.alpha  # update the Color's alpha



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
        if y < -self.size[1]:  # respawn at top
            y = 1200
            x = randint(0, 800)
            self.speed = uniform(0.5, 1.5)
            self.sway = uniform(-0.5, 0.5)
        self.pos = (x, y)
        self.ellipse.pos = self.pos


class LeafParticle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (randint(20, 40), randint(10, 25))  # leaf-like size
        self.pos = (randint(0, 800), randint(0, 1200))
        self.speed = uniform(1, 3)  # falling speed
        self.sway = uniform(-1, 1)  # horizontal swaying
        self.rotation_angle = uniform(0, 360)
        self.rotation_speed = uniform(-2, 2)

        with self.canvas:
            PushMatrix()
            self.rot = Rotate(angle=self.rotation_angle, origin=self.center)
            Color(uniform(0.0, 0.5), uniform(0.3, 0.8), uniform(0.0, 0.2), 0.8)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            PopMatrix()

    def move(self):
        x, y = self.pos
        x += self.sway
        y -= self.speed  # falling down
        self.rotation_angle += self.rotation_speed
        if y < -self.size[1]:  # respawn at top
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
        layout = BoxLayout(orientation="vertical")

        top_bar = MDTopAppBar(
            title="About AgroDoctor",
            elevation=4,
            left_action_items=[["arrow-left", lambda x: self.go_home()]]
        )

        scroll = MDScrollView()
        about_text = (
            "[b]AgroDoctor[/b]\n\n"
            "This application is a full-stack AI solution for farmers.\n\n"
            "[u]Core Features:[/u]\n"
            "    • AI-powered leaf disease diagnosis.\n"
            "    • Multi-language treatment plans from a Generative AI.\n"
            "    • Mobile-friendly interface.\n"
            "    • Python backend with ML.\n\n"
            "[u]Developed by:[/u]\n"
            "Raghuveer, Tanuja, Prabhu, Pavan\n\n"
            "This app helps farmers quickly identify leaf diseases and get treatment plans."
        )

        content_label = MDLabel(
            text=about_text,
            halign="left",
            markup=True,
            padding="20dp",
            size_hint_y=None
        )
        content_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
        content_label.bind(texture_size=lambda instance, value: setattr(instance, "height", value[1]))

        scroll.add_widget(content_label)
        layout.add_widget(top_bar)
        layout.add_widget(scroll)

        # --- Contact Us Button ---
        contact_btn = MDRaisedButton(text="Contact Us", pos_hint={"center_x": 0.5})
        contact_btn.bind(on_release=self.show_contact_dialog)
        layout.add_widget(contact_btn)

        self.add_widget(layout)

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

        # For now, just print it; later can send to API
        print(f"Name: {name}\nEmail: {email}\nMessage: {message}")

        from kivymd.toast import toast
        toast("Feedback submitted successfully!")
        self.dialog.dismiss()





# ---------------- Splash Screen ----------------
class SplashScreen(Screen):
    def on_enter(self, *args):
        if not hasattr(self, "logo_added"):
            logo = Image(source="placeholder.png", pos_hint={"center_x": 0.5, "center_y": 0.5}, size_hint=(0.5, 0.5))
            self.add_widget(logo)
            self.logo_added = True
        Clock.schedule_once(self.switch_to_main, 2.0)

    def switch_to_main(self, dt):
        if self.manager:
            self.manager.transition = FadeTransition(duration=0.4)
            self.manager.current = "main_screen"


# ---------------- Main App ----------------
class AgroDoctorApp(MDApp):
    def build(self):
        # Fonts & Theme
        font_path = os.path.dirname(__file__)
        try:
            LabelBase.register(name="NotoSans", fn_regular=os.path.join(font_path, "NotoSans-Regular.ttf"))
            LabelBase.register(name="NotoSansTelugu", fn_regular=os.path.join(font_path, "NotoSansTelugu-Regular.ttf"))
            LabelBase.register(name="NotoSansDevanagari", fn_regular=os.path.join(font_path, "NotoSansDevanagari-Regular.ttf"))
            self.theme_cls.font_name = "NotoSans"
        except Exception:
            pass

        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"

        # ScreenManager
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

        with home.canvas.before:
            try:
                self.bg_rect = Rectangle(source="background.jpg", pos=home.pos, size=home.size)
            except Exception:
                self.bg_rect = Rectangle(pos=home.pos, size=home.size)
            self.overlay = Color(0, 0, 0, 0.4)
            self.overlay_rect = Rectangle(pos=home.pos, size=home.size)
        home.bind(size=self.update_bg, pos=self.update_bg)

        # Animate background
        anim_bg = Animation(pos=(self.bg_rect.pos[0], self.bg_rect.pos[1]+10), duration=2) + \
                  Animation(pos=(self.bg_rect.pos[0], self.bg_rect.pos[1]-10), duration=2)
        anim_bg.repeat = True
        anim_bg.start(self.bg_rect)

        # Root layout
        root_layout = BoxLayout(orientation="vertical")

        # Particles
        self.particles = []
        for _ in range(25):  # 25 leaves
            leaf = LeafParticle()
            self.particles.append(leaf)
            home.add_widget(leaf)

        self.dust_particles = []
        for _ in range(50):
            dust = DustParticle()
            self.dust_particles.append(dust)
            home.add_widget(dust)

        self.sparkles = []
        for _ in range(40):  # number of sparkles
            sparkle = SparkleParticle()
            self.sparkles.append(sparkle)
            home.add_widget(sparkle)
        Clock.schedule_interval(self.update_particles, 1/30)


        # Top bar
        self.top_bar = MDTopAppBar(
            title="AgroDoctor",
            elevation=4,
            left_action_items=[["logo.png", lambda x: None]],
            right_action_items=[["information", lambda x: self.switch_to_about()]]
        )
        self.top_bar.ids.label_title.font_size = "32sp"
        root_layout.add_widget(self.top_bar)

        # Content layout
        content_layout = BoxLayout(orientation="vertical", padding="20dp", spacing="20dp")

        # Image Card
        self.image_card = MDCard(
            orientation="vertical",
            padding="10dp",
            elevation=8,
            radius=[25, 25, 25, 25],
            md_bg_color=(1, 1, 1, 0.12)
        )

        self.image_display = Image(source="placeholder.png")
        self.result_label = MDLabel(
            text="Upload a leaf image to begin", halign="center",
            font_style="H6", size_hint_y=None, height="40dp", adaptive_height=True,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)

        )
        self.image_card.add_widget(self.image_display)
        self.image_card.add_widget(self.result_label)

        # Buttons
        button_layout = BoxLayout(
            orientation="horizontal",
            spacing="10dp",
            size_hint_y=None,
            height="50dp"
        )
        select_button = MDFillRoundFlatIconButton(
            text="Select", icon="image-search-outline",
            on_release=self.select_image, size_hint=(1, 1)
        )
        select_button.ripple_color = (0, 1, 0, 0.3)

        self.diagnose_button = MDFillRoundFlatIconButton(
            text="Diagnose", icon="magnify",
            on_release=self.diagnose_disease_thread,
            disabled=True, size_hint=(1, 1)
        )
        self.treatment_button = MDFillRoundFlatIconButton(
            text="Get Plan", icon="pill",
            on_release=self.open_language_dialog,
            disabled=True, size_hint=(1, 1)
        )

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
    def select_image(self, *args):
        self.diagnose_button.disabled = True
        self.treatment_button.disabled = True
        self.predicted_disease = None
        from plyer import filechooser
        filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self, selection):
        if selection:
            self.selected_path = selection[0]
            self.image_display.source = self.selected_path
            self.result_label.text = "Image ready for diagnosis."
            self.diagnose_button.disabled = False

            # Animate image card pop
            orig_size = self.image_display.size
            anim = Animation(size=(orig_size[0]*1.05, orig_size[1]*1.05), duration=0.15) + \
                   Animation(size=orig_size, duration=0.15)
            anim.start(self.image_display)
        else:
            self.result_label.text = "No file selected."

    # ---------------- Diagnosis ----------------
    def diagnose_disease_thread(self, *args):
        threading.Thread(target=self.diagnose_disease, daemon=True).start()

    def diagnose_disease(self):
        if not getattr(self, "selected_path", None):
            return
        Clock.schedule_once(lambda dt: self.show_dialog("Diagnosing...", "Please wait.", is_loading=True))
        api_url = "http://127.0.0.1:8000/predict_disease"
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
        api_url = f"http://127.0.0.1:8000/get_treatment?disease_name={self.predicted_disease}&language={language}"
        try:
            response = requests.get(api_url, timeout=60)
            Clock.schedule_once(lambda dt: self._handle_treatment_response(response, language))
        except requests.exceptions.RequestException:
            Clock.schedule_once(lambda dt: self._dismiss_and_show_message("Network Error"))

    def _handle_treatment_response(self, response, language):
        try: self.dialog.dismiss()
        except Exception: pass
        if response.status_code == 200:
            result = response.json()
            plan = result.get("treatment_plan", "No plan found.")
            Clock.schedule_once(lambda dt: self.show_dialog(f"Plan for {self.predicted_disease}", plan, language=language))
        else:
            Clock.schedule_once(lambda dt: self.show_dialog("Error", "Could not get plan."))

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
        img = PILImage.new("RGB", (200, 200), color="gray")
        img.save("placeholder.png")
    if not os.path.exists("background.jpg"):
        from PIL import Image as PILImage
        img = PILImage.new("RGB", (800, 1200), color=(7, 50, 8))
        img.save("background.jpg")
    AgroDoctorApp().run()
