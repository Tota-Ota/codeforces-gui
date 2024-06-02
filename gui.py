import tkinter as tk
from tkinter import ttk
import requests
import threading
import pytz
from datetime import datetime

def get_upcoming_contests_codeforces():
    try:
        url = "https://codeforces.com/api/contest.list"
        response = requests.get(url)
        data = response.json()
        if data["status"] == "OK":
            contests = data["result"]
            upcoming_contests = [
                {
                    "name": contest["name"],
                    "start_time": datetime.utcfromtimestamp(contest["startTimeSeconds"]).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                }
                for contest in contests if contest["phase"] == "BEFORE"
            ]
            return upcoming_contests
        else:
            return []
    except Exception as e:
        print(f"Error fetching Codeforces contests: {e}")
        return []


def convert_to_ist(utc_time_str):
    try:
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S%z')
    utc_zone = pytz.utc
    ist_zone = pytz.timezone('Asia/Kolkata')
    utc_time = utc_zone.localize(utc_time)
    ist_time = utc_time.astimezone(ist_zone)
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

class CodeforcesWidget(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Upcoming Coding Contests")
        self.geometry("500x500")
        self.configure(bg='#1e1e1e')

        # Enable high DPI awareness for better text rendering
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"Failed to set DPI awareness: {e}")

        self.style = ttk.Style()
        self.style.configure('TLabel', background='#1e1e1e', foreground='#ffffff', font=("Helvetica Neue", 14))
        self.style.configure('TButton', background='#1e1e1e', foreground='#ffffff', font=("Helvetica Neue", 12), padding=10)
        self.style.map('TButton', background=[('active', '#555555')])

        self.label = ttk.Label(self, text="Fetching data...", style='TLabel')
        self.label.pack(pady=20)

        self.refresh_button = ttk.Button(self, text="Refresh", command=self.update_contest_info, style='TButton')
        self.refresh_button.pack(pady=10)

        self.canvas = tk.Canvas(self, bg='#1e1e1e', bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollable_frame = ttk.Frame(self.canvas, style='TLabel')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.update_contest_info()

    def update_contest_info(self):
        threading.Thread(target=self.fetch_and_update, daemon=True).start()

    def fetch_and_update(self):
        contests_codeforces = get_upcoming_contests_codeforces()
        contests = contests_codeforces
        contests.sort(key=lambda x: x["start_time"])  # Sort by start time

        self.label.config(text="Upcoming Contests:" if contests else "No upcoming contests found")
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for contest in contests[:10]:  # Limit to top 10 upcoming contests
            try:
                start_time_ist = convert_to_ist(contest["start_time"])
                contest_label = ttk.Label(self.scrollable_frame, text=f"{contest['name']}\nStarts at: {start_time_ist} IST", style='TLabel', anchor='w', justify='left', wraplength=450)
                contest_label.pack(anchor='w', pady=5, padx=10, fill=tk.X)
            except Exception as e:
                print(f"Error displaying contest {contest['name']}: {e}")

if __name__ == "__main__":
    app = CodeforcesWidget()
    app.mainloop()
