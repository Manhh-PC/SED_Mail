import os
import json
import smtplib
from tkinter import filedialog
from email.message import EmailMessage
from datetime import datetime, timedelta
import customtkinter as ctk
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ==========================================
# CẤU HÌNH EMAIL THỰC TẾ TẠI ĐÂY
# ==========================================
SENDER_EMAIL = "cuanhchatli1@gmail.com"  # Điền đúng địa chỉ Gmail của bạn
SENDER_APP_PASSWORD = "amub bgts jtoe svgm"  # Chuỗi 16 ký tự App Password

# Cấu hình giao diện Sáng sủa & Sang trọng (Light Mode)
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ===== MOCK DATABASE =====
USERS = {"admin": "123456"}


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Secure Document Management System")
        self.geometry("1060x680")
        self.resizable(False, False)

        # Cấu hình màu nền tổng thể tinh tế, sáng sủa
        self.configure(fg_color="#F8F9FA")

        # Trạng thái hệ thống (State Management)
        self.current_user = None
        self.selected_file = None
        self.encrypted_file_path = None

        # Khởi chạy màn hình đăng nhập
        self.login_screen()

    def clear_screen(self):
        """Xóa toàn bộ widget trên cửa sổ chính"""
        for widget in self.winfo_children():
            widget.destroy()

    # ==========================================
    # 1. MÀN HÌNH ĐĂNG NHẬP (PREMIUM LOGIN)
    # ==========================================
    def login_screen(self):
        self.clear_screen()
        self.current_user = None

        # Khung chứa trung tâm với hiệu ứng đổ bóng nền trắng sáng sang trọng
        login_frame = ctk.CTkFrame(
            self, width=420, height=520, corner_radius=16, fg_color="#FFFFFF"
        )
        login_frame.pack_configure(expand=True, pady=40)
        login_frame.pack_propagate(False)

        # Tiêu đề và Thẩm mỹ duyên dáng
        ctk.CTkLabel(login_frame, text="🛡️", font=("Arial", 55)).pack(
            pady=(45, 5)
        )
        ctk.CTkLabel(
            login_frame,
            text="SECURE DOCS",
            font=("Segoe UI", 26, "bold"),
            text_color="#0F172A",
        ).pack(pady=(0, 5))
        ctk.CTkLabel(
            login_frame,
            text="Hệ thống quản lý tài liệu bảo mật",
            font=("Segoe UI", 13),
            text_color="#64748B",
        ).pack(pady=(0, 30))

        # Form nhập liệu tinh tế
        self.user_input = ctk.CTkEntry(
            login_frame,
            placeholder_text="Tên đăng nhập",
            width=300,
            height=48,
            corner_radius=10,
            fg_color="#F1F5F9",
            border_color="#E2E8F0",
            text_color="#0F172A",
            placeholder_text_color="#94A3B8",
        )
        self.user_input.pack(pady=10)

        self.pass_input = ctk.CTkEntry(
            login_frame,
            placeholder_text="Mật khẩu",
            show="*",
            width=300,
            height=48,
            corner_radius=10,
            fg_color="#F1F5F9",
            border_color="#E2E8F0",
            text_color="#0F172A",
            placeholder_text_color="#94A3B8",
        )
        self.pass_input.pack(pady=10)

        # Thông báo lỗi ngầm mềm mại
        self.login_error_lbl = ctk.CTkLabel(
            login_frame, text="", text_color="#EF4444", font=("Segoe UI", 13)
        )
        self.login_error_lbl.pack(pady=5)

        # Nút Đăng nhập vững chãi
        btn_login = ctk.CTkButton(
            login_frame,
            text="Đăng Nhập",
            font=("Segoe UI", 15, "bold"),
            width=300,
            height=48,
            corner_radius=10,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.process_login,
        )
        btn_login.pack(pady=(10, 20))

    def process_login(self):
        username = self.user_input.get()
        password = self.pass_input.get()

        if username in USERS and USERS[username] == password:
            self.current_user = username
            self.main_layout()
        else:
            self.login_error_lbl.configure(
                text="Tài khoản hoặc mật khẩu không chính xác!"
            )

    # ==========================================
    # 2. KHUNG LAYOUT CHÍNH (MAIN LAYOUT)
    # ==========================================
    def main_layout(self):
        self.clear_screen()

        # --- SIDEBAR PANEL (Màu tối lịch lãm tương phản cao) ---
        self.sidebar = ctk.CTkFrame(
            self, width=240, corner_radius=0, fg_color="#1E293B"
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo Sidebar tinh xảo
        ctk.CTkLabel(
            self.sidebar,
            text="SECURE DOCS",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC",
        ).pack(pady=(35, 35))

        # Các nút Menu điều hướng có icon rõ nét
        self.btn_dash = self.create_menu_btn(
            "Tổng quan", self.show_dashboard
        )
        self.btn_enc = self.create_menu_btn(
            "Mã hóa tài liệu", self.show_encrypt
        )
        self.btn_send = self.create_menu_btn(
            "Gửi Email bảo mật", self.show_send
        )
        self.btn_dec = self.create_menu_btn(
            "Giải mã & Kiểm tra", self.show_decrypt
        )

        # Nút Đăng xuất ở đáy sidebar tinh tế
        btn_logout = ctk.CTkButton(
            self.sidebar,
            text="🚪 Đăng xuất",
            fg_color="#334155",
            hover_color="#EF4444",
            height=42,
            corner_radius=10,
            font=("Segoe UI", 13, "bold"),
            text_color="#F8FAFC",
            command=self.login_screen,
        )
        btn_logout.pack(side="bottom", fill="x", padx=20, pady=35)

        # --- CONTENT PANEL (Nền sáng sủa cao cấp) ---
        self.content_frame = ctk.CTkFrame(self, fg_color="#F8F9FA", corner_radius=0)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Mặc định hiển thị Dashboard trước
        self.show_dashboard()

    def create_menu_btn(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            anchor="w",
            fg_color="transparent",
            hover_color="#334155",
            height=46,
            corner_radius=10,
            font=("Segoe UI", 14),
            text_color="#CBD5E1",
            text_color_disabled="#94A3B8",
            command=command,
        )
        btn.pack(fill="x", padx=16, pady=5)
        return btn

    def set_active_tab(self, active_button):
        """Hiệu ứng highlight tab đang chọn theo phong cách ứng dụng cao cấp"""
        for btn in [self.btn_dash, self.btn_enc, self.btn_send, self.btn_dec]:
            btn.configure(
                fg_color="transparent",
                text_color="#CBD5E1",
                font=("Segoe UI", 14),
            )
        active_button.configure(
            fg_color="#2563EB", text_color="#FFFFFF", font=("Segoe UI", 14, "bold")
        )

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # 3. MÀN HÌNH DASHBOARD (DASHBOARD)
    # ==========================================
    def show_dashboard(self):
        self.clear_content()
        self.set_active_tab(self.btn_dash)

        # Khung chào mừng chuẩn Thượng lưu (Premium Card)
        welcome_card = ctk.CTkFrame(
            self.content_frame, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E2E8F0"
        )
        welcome_card.pack(fill="x", padx=40, pady=35, ipady=15)

        ctk.CTkLabel(
            welcome_card,
            text=f"Xin chào, {self.current_user}!",
            font=("Segoe UI", 24, "bold"),
            text_color="#0F172A",
            anchor="w",
        ).pack(padx=30, pady=(20, 5), fill="x")
        ctk.CTkLabel(
            welcome_card,
            text="Hệ thống chia sẻ dữ liệu bảo mật có giới hạn thời gian.",
            font=("Segoe UI", 14),
            text_color="#64748B",
            anchor="w",
        ).pack(padx=30, fill="x")

        # Grid thông số nhanh trực quan bên dưới
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=40, pady=(0, 35))
        stats_frame.columnconfigure((0, 1), weight=1, uniform="equal")

        # Thẻ thông số thuật toán
        card_1 = ctk.CTkFrame(
            stats_frame, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E2E8F0"
        )
        card_1.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        ctk.CTkLabel(
            card_1,
            text="THUẬT TOÁN ÁP DỤNG",
            font=("Segoe UI", 12, "bold"),
            text_color="#2563EB",
        ).pack(pady=(25, 0))
        ctk.CTkLabel(
            card_1,
            text="AES-128-GCM (AEAD)",
            font=("Segoe UI", 20, "bold"),
            text_color="#0F172A",
        ).pack(pady=(10, 25))

        # Thẻ chính sách thời gian
        card_2 = ctk.CTkFrame(
            stats_frame, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E2E8F0"
        )
        card_2.grid(row=0, column=1, padx=(15, 0), sticky="nsew")
        ctk.CTkLabel(
            card_2,
            text="CHÍNH SÁCH THỜI GIAN",
            font=("Segoe UI", 12, "bold"),
            text_color="#2563EB",
        ).pack(pady=(25, 0))
        ctk.CTkLabel(
            card_2,
            text="2 Phút (Tự hủy toàn phần)",
            font=("Segoe UI", 20, "bold"),
            text_color="#0F172A",
        ).pack(pady=(10, 25))

    # ==========================================
    # 4. MÀN HÌNH MÃ HÓA (ENCRYPT SCREEN)
    # ==========================================
    def show_encrypt(self):
        self.clear_content()
        self.set_active_tab(self.btn_enc)

        ctk.CTkLabel(
            self.content_frame,
            text="Mã hóa tài liệu",
            font=("Segoe UI", 24, "bold"),
            text_color="#0F172A",
        ).pack(anchor="w", padx=40, pady=(35, 20))

        main_box = ctk.CTkFrame(
            self.content_frame, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E2E8F0"
        )
        main_box.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        def action_choose():
            path = filedialog.askopenfilename()
            if path:
                self.selected_file = path
                lbl_file.configure(
                    text=f"{os.path.basename(path)}", text_color="#2563EB"
                )
                btn_execute.configure(state="normal")

        def action_encrypt():
            if not self.selected_file:
                return

            try:
                key = AESGCM.generate_key(bit_length=128)
                aes = AESGCM(key)
                nonce = os.urandom(12)

                with open(self.selected_file, "rb") as f:
                    data = f.read()

                ciphertext = aes.encrypt(nonce, data, None)
                self.encrypted_file_path = self.selected_file + ".enc"

                with open(self.encrypted_file_path, "wb") as f:
                    f.write(nonce + ciphertext)

                expire_time = (datetime.now() + timedelta(minutes=2)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                meta = {"key": key.hex(), "expire": expire_time}

                with open("meta.json", "w") as f:
                    json.dump(meta, f)

                lbl_status.configure(
                    text=f"Mã hóa mật mã thành công!\nFile lưu tại thư mục gốc.\nHết hạn: {expire_time}",
                    text_color="#16A34A",
                )
            except Exception as e:
                lbl_status.configure(
                    text=f"Lỗi thực thi: {str(e)}", text_color="#DC2626"
                )

        # Thành phần UI mượt mà
        ctk.CTkButton(
            main_box,
            text="Chọn tệp tin gốc",
            font=("Segoe UI", 13, "bold"),
            height=42,
            fg_color="#475569",
            hover_color="#334155",
            command=action_choose,
        ).pack(pady=(50, 10))

        lbl_file = ctk.CTkLabel(
            main_box,
            text="Chưa chọn tệp tin nào từ máy tính",
            font=("Segoe UI", 13),
            text_color="#94A3B8",
        )
        lbl_file.pack(pady=5)

        btn_execute = ctk.CTkButton(
            main_box,
            text="Bắt đầu mã hóa dữ liệu",
            font=("Segoe UI", 14, "bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            height=46,
            width=220,
            state="disabled",
            command=action_encrypt,
        )
        btn_execute.pack(pady=35)

        lbl_status = ctk.CTkLabel(
            main_box, text="", font=("Segoe UI", 14, "bold")
        )
        lbl_status.pack(pady=10)

    # ==========================================
    # 5. MÀN HÌNH GỬI EMAIL (SEND EMAIL SCREEN)
    # ==========================================
    def show_send(self):
        self.clear_content()
        self.set_active_tab(self.btn_send)

        ctk.CTkLabel(
            self.content_frame,
            text="Phân phối tệp tin qua Email",
            font=("Segoe UI", 24, "bold"),
            text_color="#0F172A",
        ).pack(anchor="w", padx=40, pady=(35, 20))

        main_box = ctk.CTkFrame(
            self.content_frame, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E2E8F0"
        )
        main_box.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        active_file_text = (
            f"Tệp sẵn sàng phân phối: {os.path.basename(self.encrypted_file_path)}"
            if self.encrypted_file_path
            else "Lưu ý: Bạn cần thực hiện mã hóa file trước khi gửi đi."
        )
        lbl_info = ctk.CTkLabel(
            main_box,
            text=active_file_text,
            font=("Segoe UI", 13, "bold"),
            text_color="#D97706" if not self.encrypted_file_path else "#16A34A",
        )
        lbl_info.pack(pady=(40, 10))

        email_entry = ctk.CTkEntry(
            main_box,
            placeholder_text="Địa chỉ Email người nhận thực tế",
            width=380,
            height=46,
            corner_radius=10,
            fg_color="#F1F5F9",
            border_color="#E2E8F0",
            text_color="#0F172A",
            placeholder_text_color="#94A3B8",
        )
        email_entry.pack(pady=15)

        def action_send():
            if not self.encrypted_file_path:
                lbl_status.configure(
                    text="Thất bại: Không phát hiện file mã hóa hợp lệ để gửi!",
                    text_color="#DC2626",
                )
                return

            lbl_status.configure(
                text="Đang thiết lập kết nối mã hóa tới SMTP Server...",
                text_color="#2563EB",
            )
            self.update_idletasks()

            try:
                msg = EmailMessage()
                msg["Subject"] = "Gói tài liệu bảo mật tự hủy"
                msg["From"] = SENDER_EMAIL
                msg["To"] = email_entry.get()
                msg.set_content(
                    "Bạn nhận được một tài liệu mã hóa bảo mật. File đính kèm sẽ tự động mất quyền giải mã sau 2 phút từ hệ thống quản lý."
                )

                with open(self.encrypted_file_path, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype="application",
                        subtype="octet-stream",
                        filename="secure_payload.enc",
                    )

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
                    smtp.send_message(msg)

                lbl_status.configure(
                    text="Đã chuyển phát gói tin bảo mật thành công!",
                    text_color="#16A34A",
                )
            except Exception as e:
                lbl_status.configure(
                    text=f"❌ Thất bại kết nối SMTP: {str(e)}",
                    text_color="#DC2626",
                )

        btn_send = ctk.CTkButton(
            main_box,
            text="Gửi tài liệu",
            font=("Segoe UI", 14, "bold"),
            height=46,
            width=160,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=action_send,
        )
        btn_send.pack(pady=20)

        lbl_status = ctk.CTkLabel(main_box, text="", font=("Segoe UI", 13))
        lbl_status.pack(pady=10)

    # ==========================================
    # 6. MÀN HÌNH GIẢI MÃ (DECRYPT SCREEN)
    # ==========================================
    def show_decrypt(self):
        self.clear_content()
        self.set_active_tab(self.btn_dec)

        ctk.CTkLabel(
            self.content_frame,
            text="Kiểm tra và Giải mã",
            font=("Segoe UI", 24, "bold"),
            text_color="#0F172A",
        ).pack(anchor="w", padx=40, pady=(35, 20))

        main_box = ctk.CTkFrame(
            self.content_frame, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E2E8F0"
        )
        main_box.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        def action_decrypt():
            if not os.path.exists("meta.json"):
                lbl_status.configure(
                    text="Lỗi hệ thống: Không tìm thấy file quản lý cơ sở khóa meta.json!",
                    text_color="#DC2626",
                )
                return

            try:
                with open("meta.json", "r") as f:
                    meta = json.load(f)

                expire_time = datetime.strptime(
                    meta["expire"], "%Y-%m-%d %H:%M:%S"
                )
                if datetime.now() > expire_time:
                    lbl_status.configure(
                        text=f"HỆ THỐNG TỪ CHỐI TRUY CẬP: File đã hết hạn vào lúc {meta['expire']}!",
                        text_color="#DC2626",
                    )
                    return

                file_enc = filedialog.askopenfilename(
                    filetypes=[("Encrypted Files", "*.enc")]
                )
                if not file_enc:
                    return

                with open(file_enc, "rb") as f:
                    payload = f.read()

                nonce = payload[:12]
                ciphertext = payload[12:]

                aes = AESGCM(bytes.fromhex(meta["key"]))
                decrypted_bytes = aes.decrypt(nonce, ciphertext, None)

                output_name = "Restored_" + os.path.basename(file_enc).replace(
                    ".enc", ""
                )
                with open(output_name, "wb") as f:
                    f.write(decrypted_bytes)

                lbl_status.configure(
                    text=f"XÁC THỰC THÀNH CÔNG!\nTài liệu gốc đã khôi phục: {output_name}",
                    text_color="#16A34A",
                )

            except Exception as e:
                lbl_status.configure(
                    text="Lỗi Toàn vẹn: Dữ liệu bị chỉnh sửa trái phép hoặc khóa sai lệch!",
                    text_color="#DC2626",
                )

        ctk.CTkButton(
            main_box,
            text="Chọn tập tin giải mã (.enc)",
            font=("Segoe UI", 14, "bold"),
            fg_color="#EA580C",
            hover_color="#C2410C",
            height=46,
            command=action_decrypt,
        ).pack(pady=60)

        lbl_status = ctk.CTkLabel(
            main_box, text="", font=("Segoe UI", 14, "bold")
        )
        lbl_status.pack(pady=10)


# ===== KHỞI CHẠY HỆ THỐNG =====
if __name__ == "__main__":
    app = App()
    app.mainloop()