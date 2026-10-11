import os
import subprocess
import threading
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ClamAVWin11GUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ClamAV Scanner")
        self.geometry("700x530")
        self.resizable(False, False)

        
        self.clam_dir = r"D:\Programs\clamav"

        self.title_label = ctk.CTkLabel(
            self,
            text="ClamAV Local Scanner",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.title_label.pack(pady=(20, 2))

        self.sub_label = ctk.CTkLabel(
            self,
            text="Быстрая проверка файлов по свежим антивирусным базам",
            font=ctk.CTkFont(size=12),
            text_color="#8A8A8A",
        )
        self.sub_label.pack(pady=(0, 15))

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=5)

        self.btn_file = ctk.CTkButton(
            self.btn_frame,
            text="📄 Выбрать файл",
            command=self.select_file,
            width=170,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.btn_file.pack(side="left", padx=10)

        self.btn_folder = ctk.CTkButton(
            self.btn_frame,
            text="📁 Выбрать папку",
            command=self.select_folder,
            width=170,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.btn_folder.pack(side="left", padx=10)

        self.log_area = ctk.CTkTextbox(
            self,
            width=660,
            height=340,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#181818",
            border_width=1,
            border_color="#2B2B2B",
        )
        self.log_area.pack(pady=15, padx=20)

        
        self.log_area._textbox.tag_config("red", foreground="#FF4D4D")
        self.log_area._textbox.tag_config("green", foreground="#00FF66")
        self.log_area._textbox.tag_config("yellow", foreground="#FFCC00")
        self.log_area._textbox.tag_config("white", foreground="#E0E0E0")

    def log(self, text):
        
        color_tag = "white"
        if "FOUND" in text or (
            "Infected files:" in text and not "Infected files: 0" in text
        ):
            color_tag = "red"
        elif "OK" in text or "Infected files: 0" in text:
            color_tag = "green"
        elif "[1/2]" in text or "[2/2]" in text or "--->" in text:
            color_tag = "yellow"

        self.log_area._textbox.insert("end", text + "\n", color_tag)
        self.log_area.see("end")

    def set_buttons_state(self, state):
        self.btn_file.configure(state=state)
        self.btn_folder.configure(state=state)

    def select_file(self):
        target = ctk.filedialog.askopenfilename(
            title="Выберите файл для проверки"
        )
        if target:
            threading.Thread(
                target=self.run_scan, args=(target,), daemon=True
            ).start()

    def select_folder(self):
        target = ctk.filedialog.askdirectory(
            title="Выберите папку для проверки"
        )
        if target:
            threading.Thread(
                target=self.run_scan, args=(target,), daemon=True
            ).start()

    def run_scan(self, target):
        self.set_buttons_state("disabled")
        self.log_area.delete("1.0", "end")

        freshclam_exe = os.path.join(self.clam_dir, "freshclam.exe")
        clamscan_exe = os.path.join(self.clam_dir, "clamscan.exe")

        
        no_window = (
            subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )

        self.log("[1/2] Обновление антивирусных баз...")
        try:
            p_upd = subprocess.Popen(
                [freshclam_exe],
                cwd=self.clam_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=no_window,
            )
            for line in p_upd.stdout:
                self.log(line.strip())
            p_upd.wait()
        except Exception as e:
            self.log(f"Ошибка при обновлении баз: {e}")

        self.log("\n" + "─" * 60 + "\n")

        self.log(f'[2/2] Сканирование: "{target}"\n')
        try:
            p_scan = subprocess.Popen(
                [clamscan_exe, "--bell", "-r", target],
                cwd=self.clam_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=no_window,
            )
            for line in p_scan.stdout:
                self.log(line.strip())
            p_scan.wait()
        except Exception as e:
            self.log(f"Ошибка при сканировании: {e}")

        self.log("\n---> Проверка завершена!")
        self.set_buttons_state("normal")


if __name__ == "__main__":
    app = ClamAVWin11GUI()
    app.mainloop()