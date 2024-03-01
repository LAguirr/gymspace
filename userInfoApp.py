from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests


class UserInfoApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # User ID Entry
        self.user_id_input = TextInput(text='', hint_text='Enter User ID')
        self.layout.add_widget(self.user_id_input)

        # Button to Get User Info
        self.get_info_button = Button(text='Get User Info')
        self.get_info_button.bind(on_press=self.get_user_info)
        self.layout.add_widget(self.get_info_button)

        # Label to Show User Info
        self.info_label = Label(text='')
        self.layout.add_widget(self.info_label)

        return self.layout

    def get_user_info(self, instance):
        user_id = self.user_id_input.text
        url = f"http://localhost:5000/find_user/{user_id}"
        response = requests.get(url)
        if response.status_code == 200:
            user_info = response.json()
            self.info_label.text = str(user_info)
        else:
            self.info_label.text = "User not found or error occurred."


if __name__ == '__main__':
    UserInfoApp().run()
