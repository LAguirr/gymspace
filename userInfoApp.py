import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime, timedelta


def fetch_user_data():
    user_id = user_id_entry.get()
    url = f"https://ctsgf6-5000.csb.app/find_user/{user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        user_info = response.json()
        name = user_info.get('name', 'No name available')

        # Parse and format the end_date
        end_date_str = user_info.get('end_date', '')

        # if end_date_str:
        # end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        # else:
        # end_date = 'No end date available'

        display_text = f"Name: {name} \n Fecha Vencimiento: {end_date_str}"
        info_label.config(text=display_text)
    else:
        info_label.config(text="User not found or error occurred.")


# Tkinter setup
app = tk.Tk()
app.title("User Information")
app.configure(bg='black')

# User ID Entry
tk.Label(app, text="Enter User ID:", bg='black', fg='white').pack()
user_id_entry = tk.Entry(app)
user_id_entry.pack()

# Button to Get User Info
get_info_button = ttk.Button(app,
                             text="Get User Info",
                             command=fetch_user_data)
get_info_button.pack()

# Label to Show User Info
info_label = tk.Label(app, text="", bg='black', fg='white', justify=tk.CENTER)
info_label.pack()

app.mainloop()
