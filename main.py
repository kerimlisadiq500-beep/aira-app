from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.core.window import Window

from aira_app import aira_cavab_ver

class AiraChatApp(App):
    def build(self):
        self.title = "Aira AI Assistant"
        
        ana_panel = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.scroll = ScrollView(size_hint=(1, 0.85))
        
        # Qalın mətn tag-lərini ([b]) sildik ki, Kivy Android-də çöküş verməsin
        self.chat_label = Label(
            text="Aira: Salam! Mən hazıram. Mənim qurucum Sadiqdir! 🤖\n",
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(Window.width - 40, None)
        )
        self.chat_label.bind(texture_size=self.chat_label.setter('size'))
        self.scroll.add_widget(self.chat_label)
        ana_panel.add_widget(self.scroll)
        
        giris_paneli = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        self.txt_input = TextInput(
            hint_text="Mesajınızı yazın...",
            multiline=False,
            size_hint=(0.8, 1)
        )
        self.txt_input.bind(on_text_validate=self.mesaj_gonder)
        
        gonder_duyme = Button(
            text="Göndər",
            size_hint=(0.2, 1),
            background_color=(0.1, 0.6, 0.9, 1)
        )
        gonder_duyme.bind(on_press=self.mesaj_gonder)
        
        giris_paneli.add_widget(self.txt_input)
        giris_paneli.add_widget(gonder_duyme)
        
        ana_panel.add_widget(giris_paneli)
        return ana_panel

    def mesaj_gonder(self, instance):
        sual = self.txt_input.text.strip()
        if not sual:
            return
            
        self.chat_label.text += f"\nSən: {sual}\n"
        self.txt_input.text = "" 
        
        cavab = aira_cavab_ver(sual)
        
        self.chat_label.text += f"Aira: {cavab}\n"
        self.scroll.scroll_y = 0

if __name__ == "__main__":
    AiraChatApp().run()
