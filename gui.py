import random
import tkinter as tk
from tkinter import filedialog, ttk
import threading
from queue import Queue
import asyncio
from datetime import datetime, timezone
from playwright.async_api import async_playwright, Error
from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN
from facebook_signup import facebook_signup
from gmail_signup import google_signup
from instagram_signup import instagram_signup
from tiktok_signup import tiktok_signup
from paypal_signup import paypal_signup
from zenler_signup import zenler_signup
from testpage import test_page
from bcgame_signup import bcgame_signup
from megapari_signup import megapari_signup
from jackpot50 import jackpot_signup
from gofundme_signup import gofundme_signup
from wolt import wolt_signup
from yandex import yandex_signup

class FacebookSignupBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DOLS Processing Tool")
        self.root.geometry("700x600")
        self.root.configure(bg="#212121")
        self.all_functions = ["FB-signup", "Google-signup", "Wolt", "Gofundme", "Jackpot", "Tiktok-signup",
                              "Instagram-signup", "Paypal-signup", "Zenler-signup", "BcGame-signup", "Yandex-signup",
                              "Megapari-signup", "Test-page"]
        self.all_functions.sort()
        self.is_running = False
        self.is_paused = False
        self.queue = Queue()
        self.current_line = 0
        self.success_counter = 0
        self.failed_counter = 0
        self.pending_counter = 0
        self.proxy_list = []
        self.vpn_settings = None
        with open("nordvpn/countrylist.txt", "r") as file:
            self.areas_list = file.readlines()
        self.areas_list = [area.strip() for area in self.areas_list]

        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background="#333333", foreground="#ffffff", borderwidth=0,
                        padding=5, font=('Helvetica', 10, 'bold'))
        style.map("TButton", background=[('active', '#454545')], foreground=[('active', '#ffffff')])
        style.configure("Red.TButton", background="#d32f2f", foreground="#ffffff", borderwidth=0,
                        padding=5, font=('Helvetica', 10, 'bold'))
        style.map("Red.TButton", background=[('active', '#b71c1c')], foreground=[('active', '#ffffff')])
        style.configure("TLabel", background="#212121", foreground="#ffffff", font=('Helvetica', 11))
        style.configure("TCombobox", fieldbackground="#333333", background="#333333",
                        foreground="#ffffff", arrowsize=12)
        style.map("TCombobox", fieldbackground=[('readonly', '#333333')],
                  selectbackground=[('readonly', '#333333')], selectforeground=[('readonly', '#ffffff')])
        style.configure("Green.Horizontal.TProgressbar", troughcolor="#333333", background="#4caf50",
                        borderwidth=0, thickness=8)

        # Main frame
        main_frame = tk.Frame(root, bg="#212121", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Input section
        input_frame = tk.LabelFrame(main_frame, text="Configuration", bg="#212121", fg="#ffffff",
                                    font=('Helvetica', 11, 'bold'), padx=10, pady=10)
        input_frame.pack(fill="x", pady=(0, 10))

        self.numbers_label = ttk.Label(input_frame, text="Phone Numbers File:")
        self.numbers_label.grid(row=0, column=0, pady=5, sticky="w")
        self.numbers_btn = ttk.Button(input_frame, text="Browse", command=self.select_numbers_file)
        self.numbers_btn.grid(row=0, column=2, pady=5, padx=5)
        self.numbers_file = tk.StringVar()
        self.numbers_entry = ttk.Entry(input_frame, textvariable=self.numbers_file, width=50)
        self.numbers_entry.grid(row=0, column=1, pady=5, padx=5)

        # Proxy Checkbox
        self.use_proxy = tk.BooleanVar(value=False)
        self.proxy_checkbox = ttk.Checkbutton(input_frame, text="Use Proxy", variable=self.use_proxy,
                                              command=self.update_proxy_file_state)
        self.proxy_checkbox.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        # self.proxy_label = ttk.Label(input_frame, text="Proxy File:")
        # self.proxy_label.grid(row=2, column=0, pady=5, sticky="w")
        self.proxy_btn = ttk.Button(input_frame, text="Browse", command=self.select_proxy_file)
        self.proxy_btn.grid(row=1, column=2, pady=5, padx=5)
        self.proxy_file = tk.StringVar()
        self.proxy_entry = ttk.Entry(input_frame, textvariable=self.proxy_file, width=50)
        self.proxy_entry.grid(row=1, column=1, pady=5, padx=5)
        self.proxy_btn.state(['disabled'])
        self.proxy_entry.state(['disabled'])

        # Nord Process
        self.use_nord = tk.BooleanVar(value=False)
        self.nord_checkbox = ttk.Checkbutton(input_frame, text="Use NordVpn", variable=self.use_nord,
                                                 command=self.update_selected_area_state)
        self.nord_checkbox.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.selected_area = tk.StringVar(value="Select area")
        self.area_combo = ttk.Combobox(
            input_frame,
            textvariable=self.selected_area,
            values=self.areas_list,
            width=50,
            state="readonly"
        )
        self.area_combo.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.area_combo.state(['disabled'])

        self.function_label = ttk.Label(input_frame, text="Process Type:")
        self.function_label.grid(row=4, column=0, pady=5, sticky="w")
        self.function_type = tk.StringVar(value="FB-signup")
        self.function_combo = ttk.Combobox(input_frame, textvariable=self.function_type,
                                           values=self.all_functions,
                                           width=15, state="readonly")
        self.function_combo.grid(row=5, column=0, pady=5, padx=5, sticky="w")

        self.thread_label = ttk.Label(input_frame, text="Processes:")
        self.thread_label.grid(row=4, column=1, pady=5, sticky="w")
        self.thread_count = tk.StringVar(value="1")
        self.thread_combo = ttk.Combobox(input_frame, textvariable=self.thread_count,
                                         values=[str(i) for i in range(1, 11)], width=10, state="readonly")
        self.thread_combo.grid(row=5, column=1, pady=5, padx=5, sticky="w")

        self.country_label = ttk.Label(input_frame, text="Country:")
        self.country_label.grid(row=4, column=2, pady=5, sticky="w")

        self.selected_country = tk.StringVar(value="default")
        self.country_combo = ttk.Combobox(
            input_frame,
            textvariable=self.selected_country,
            values=["default","tajikistan", "nigeria", "east timor", "myanmar", "netherlands", "germany", "tanzania", "uk"],  # Add more as needed
            width=15,
            state="readonly"
        )
        self.country_combo.grid(row=5, column=2, pady=5, padx=5, sticky="w")

        # Results section
        results_frame = tk.LabelFrame(main_frame, text="Results", bg="#212121", fg="#ffffff",
                                      font=('Helvetica', 11, 'bold'), padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, pady=10)

        self.results_text = tk.Text(results_frame, height=8, bg="#333333", fg="#ffffff",
                                    font=('Courier', 10), bd=0, insertbackground="white")
        self.results_text.pack(fill="both", expand=True)
        self.results_text.tag_configure("success", foreground="#4caf50")
        self.results_text.tag_configure("fail", foreground="#d32f2f")
        self.results_text.tag_configure("error", foreground="#ff9800")
        self.results_text.tag_configure("pending", foreground="#29b6f6")

        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate',
                                        style="Green.Horizontal.TProgressbar")
        self.progress.pack(pady=10)

        self.counts_label = ttk.Label(
            main_frame,
            text="✅ Success: 0    ❌ Failed: 0    ⏳ Pending: 0",
            foreground="#ffffff",
            background="#212121",
            font=('Helvetica', 10, 'bold')
        )
        self.counts_label.pack(pady=(0, 10))

        self.btn_frame = tk.Frame(main_frame, bg="#212121")
        self.btn_frame.pack(pady=10)
        self.start_btn = ttk.Button(self.btn_frame, text="START", command=self.start_process)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = ttk.Button(self.btn_frame, text="STOP", command=self.stop_process,
                                   style="Red.TButton")
        self.stop_btn.pack(side="left", padx=5)
        self.resume_btn = ttk.Button(self.btn_frame, text="RESUME", command=self.resume_process)
        self.resume_btn.pack(side="left", padx=5)

        # Start result updates loop
        self.update_results()

    def select_numbers_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file:
            self.numbers_file.set(file)

    def select_proxy_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file:
            self.proxy_file.set(file)

    def update_proxy_file_state(self):
        if self.use_proxy.get():
            self.proxy_btn.state(['!disabled'])
            self.proxy_entry.state(['!disabled'])
        else:
            self.proxy_btn.state(['disabled'])
            self.proxy_entry.state(['disabled'])
    def update_selected_area_state(self):
        if self.use_nord.get():
            self.area_combo.state(['!disabled'])
        else:
            self.area_combo.state(['disabled'])

    def start_process(self):
        self.success_counter = 0
        self.failed_counter = 0
        self.pending_counter = 0
        self.progress['value'] = 0
        self.results_text.delete("1.0", tk.END)
        self.counts_label.config(
            text="✅ Success: 0    ❌ Failed: 0    ⏳ Pending: 0"
        )
        phone_numbers_file = self.numbers_file.get()
        proxies_file = self.proxy_file.get()
        selected_area = self.selected_area.get()
        max_concurrent = int(self.thread_count.get())
        use_proxy = self.use_proxy.get()
        use_nord = self.use_nord.get()

        if not phone_numbers_file:
            self.show_error("Please select a phone numbers file!")
            return

        if use_proxy and not proxies_file:
            self.show_error("Please select a proxy file!")
            return
        if use_nord and selected_area == "Select area":
            self.show_error("Please select an area for nord!")
            return

        script_name = self.function_type.get()
        self.show_success(f"Start {script_name} Script ...")
        self.is_running = True
        self.is_paused = False
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.resume_btn.config(state="normal")
        phone_numbers = self.load_lines_from_file(phone_numbers_file)
        proxies = self.load_lines_from_file(proxies_file) if use_proxy else []
        if use_nord:
            selected_area = [selected_area]
            self.vpn_settings = initialize_VPN(area_input=selected_area)
        threading.Thread(target=self.run_bot, args=(phone_numbers, proxies, max_concurrent, use_proxy)).start()

    def stop_process(self):
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.resume_btn.config(state="normal")
        self.show_error("Process has Stopped")

    def resume_process(self):
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.show_error("Process has Resumed")

    def show_error(self, message):
        self.results_text.insert(tk.END, f"[ERROR] {message}\n", "error")
        self.results_text.yview(tk.END)

    def show_success(self, message):
        self.results_text.insert(tk.END, f"[SUCCESS] {message}\n", "success")
        self.results_text.yview(tk.END)

    def run_bot(self, phone_numbers, proxies, max_concurrent, use_proxy):
        # This will run the async function inside a separate thread
        bot_thread = threading.Thread(target=self.run_async_bot, args=(phone_numbers, proxies, use_proxy, max_concurrent))
        bot_thread.start()

    def run_async_bot(self, phone_numbers, proxies, use_proxy, max_concurrent):
        # This is where the async function will run in a separate thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_main(phone_numbers, proxies, use_proxy, max_concurrent))

    def load_lines_from_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f.readlines()]
        except Exception as e:
            self.show_error(f"Error reading file: {e}")
            return []

    def update_results(self):
        while not self.queue.empty():
            result = self.queue.get()
            timestamp = datetime.now(timezone.utc).strftime("[%H:%M:%S]")
            status = result.get('status', 'info').lower()
            message = result.get('message', '')
            if status == 'success':
                tag = 'success'
                formatted = f"{timestamp}  [SUCCESS]  {message}\n"
                self.success_counter += 1
                self.pending_counter = max(0, self.pending_counter - 1)

            elif status == 'fail':
                tag = 'fail'
                formatted = f"{timestamp}  [FAIL]     {message}\n"
                self.failed_counter += 1
                self.pending_counter = max(0, self.pending_counter - 1)

            elif status == 'pending':
                tag = 'pending'
                formatted = f"{timestamp}  [PENDING]  {message}\n"
                self.pending_counter += 1

            else:
                tag = 'error'
                formatted = f"{timestamp}  [ERROR]    {message}\n"

            self.results_text.insert(tk.END, formatted, tag)
            self.results_text.yview(tk.END)

            total = self.success_counter + self.failed_counter
            max_total = len(self.load_lines_from_file(self.numbers_file.get()))
            if max_total > 0:
                self.progress['value'] = (total / max_total) * 100

            self.counts_label.config(
                text=f"✅ Success: {self.success_counter}    ❌ Failed: {self.failed_counter}    ⏳ Pending: {self.pending_counter}"
            )

            if total == max_total and self.use_nord.get():
                terminate_VPN(self.vpn_settings)

        self.root.after(100, self.update_results)

    def repeat_proxies_to_match(self, proxies, total_needed):
        random.shuffle(proxies)
        extended_proxies = []
        proxy_count = len(proxies)

        for i in range(total_needed):
            extended_proxies.append(proxies[i % proxy_count])

        return extended_proxies

    async def run_main(self, numbers, proxy_list, use_proxy, max_concurrent):
        random.shuffle(numbers)
        semaphore = asyncio.Semaphore(max_concurrent)

        if use_proxy:
            if not proxy_list:
                raise ValueError("Proxy list is empty but 'use_proxy' is True.")
            proxy_list = self.repeat_proxies_to_match(proxy_list, len(numbers))

        async with async_playwright() as playwright:
            async def sem_task(index, number, proxy=False):
                async with semaphore:
                    if not self.is_running:
                        return
                    try:
                        func_type = self.function_type.get()
                        country = self.selected_country.get()
                        signup_functions = {
                            "FB-signup": facebook_signup,
                            "Google-signup": google_signup,
                            "Tiktok-signup": tiktok_signup,
                            "Paypal-signup": paypal_signup,
                            "Instagram-signup": instagram_signup,
                            "Zenler-signup": zenler_signup,
                            "BcGame-signup": bcgame_signup,
                            "Megapari-signup": megapari_signup,
                            "Jackpot": jackpot_signup,
                            "Gofundme": gofundme_signup,
                            "Wolt": wolt_signup,
                            "Test-page": test_page,
                            "Yandex-signup": yandex_signup,
                        }
                        signup_func = signup_functions.get(func_type)
                        if signup_func:
                            await signup_func(playwright, number, country, proxy, index, self.queue)
                            if index % max_concurrent == 0 and self.use_nord.get():
                                rotate_VPN(self.vpn_settings)
                        else:
                            print(f"Unknown function type: {func_type}")
                    except Error as e:
                        self.queue.put(
                            {'status': 'fail', 'message': f'{index} - {number} Playwright timeout error: {e}'})
                    except Exception as e:
                        self.queue.put({'status': 'fail', 'message': f'{index} - {number} Unexpected error: {e}'})

            if use_proxy:
                tasks = [
                    asyncio.create_task(sem_task(i, number, proxy))
                    for i, (number, proxy) in enumerate(zip(numbers, proxy_list))
                ]
            else:
                tasks = [
                    asyncio.create_task(sem_task(i, number))
                    for i, number in enumerate(numbers)
                ]

            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = FacebookSignupBotGUI(root)
    root.mainloop()
