import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
import os

DB_PATH = "Tkinter_Task-2_database.db"


# ---------------- DATABASE ---------------- #
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            profession TEXT,
            salary REAL,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()


# ---------------- APP ---------------- #
class CRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter CRUD App")
        self.root.geometry("1150x650")
        self.root.config(bg="#f0f0f0")

        # temp selections + caches
        self.selected_image = None
        self.image_cache = {}
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")

        # ---------- LEFT PANEL (Form) ----------
        left = tk.Frame(root, bg="#dbeafe", bd=2, relief="groove")
        left.place(x=10, y=10, width=360, height=630)
        tk.Label(left, text="User Details", font=("Arial", 18, "bold"), bg="#dbeafe").pack(pady=12)

        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.prof_var = tk.StringVar()
        self.sal_var = tk.StringVar()

        self._create_field(left, "Name", self.name_var)
        self._create_field(left, "Age", self.age_var)
        self._create_field(left, "Profession", self.prof_var)
        self._create_field(left, "Salary", self.sal_var)

        tk.Label(left, text="Image:", bg="#dbeafe").pack(anchor="w", padx=12, pady=(6, 0))
        self.image_label = tk.Label(left, text="No image selected", bg="#dbeafe")
        self.image_label.pack(pady=(2, 6))
        tk.Button(left, text="Browse Image", command=self.browse_image, bg="#2563eb", fg="white").pack()

        tk.Button(left, text="Add User", bg="#16a34a", fg="white", width=20, command=self.add_user).pack(pady=12)
        tk.Button(left, text="Clear Fields", bg="#facc15", width=20, command=self.clear_fields).pack()

        # ---------- RIGHT PANEL (Records) ----------
        right = tk.Frame(root, bg="#e0f2fe", bd=2, relief="groove")
        right.place(x=380, y=10, width=760, height=630)
        tk.Label(right, text="User Records", font=("Arial", 18, "bold"), bg="#e0f2fe").pack(pady=10)

        # Search and Filter bar
        search_frame = tk.Frame(right, bg="#e0f2fe")
        search_frame.pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(search_frame, text="Search:", bg="#e0f2fe", font=("Arial", 10, "bold")).pack(side="left")
        tk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side="left", padx=(6, 16))
        tk.Label(search_frame, text="Filter by Profession:", bg="#e0f2fe", font=("Arial", 10, "bold")).pack(side="left")

        self.filter_menu = ttk.Combobox(search_frame, textvariable=self.filter_var, width=20, state="readonly")
        self.filter_menu.pack(side="left", padx=(6, 8))
        self.filter_menu.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        tk.Button(search_frame, text="Search", command=self.load_data, bg="#2563eb", fg="white").pack(side="left", padx=6)
        tk.Button(search_frame, text="Clear", command=self.clear_search, bg="#facc15").pack(side="left")

        # container for canvas+scrollbars (use grid inside)
        right_inner = tk.Frame(right, bg="#e0f2fe")
        right_inner.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Canvas + scrollbars
        self.canvas = tk.Canvas(right_inner, bg="white", highlightthickness=0)
        self.vsb = tk.Scrollbar(right_inner, orient="vertical", command=self.canvas.yview)
        self.hsb = tk.Scrollbar(right_inner, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

        right_inner.grid_rowconfigure(0, weight=1)
        right_inner.grid_columnconfigure(0, weight=1)

        # Frame inside canvas
        self.table_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Scroll mousewheel support
        self.canvas.bind("<Enter>", lambda e: (self.canvas.bind_all("<MouseWheel>", self._on_mousewheel),
                                               self.canvas.bind_all("<Button-4>", self._on_mousewheel),
                                               self.canvas.bind_all("<Button-5>", self._on_mousewheel),
                                               self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)))
        self.canvas.bind("<Leave>", lambda e: (self.canvas.unbind_all("<MouseWheel>"),
                                               self.canvas.unbind_all("<Button-4>"),
                                               self.canvas.unbind_all("<Button-5>"),
                                               self.canvas.unbind_all("<Shift-MouseWheel>")))

        self.load_data()

    # ---------------- helpers ---------------- #
    def _create_field(self, parent, label_text, var):
        tk.Label(parent, text=f"{label_text}:", bg="#dbeafe").pack(anchor="w", padx=12, pady=(6, 2))
        tk.Entry(parent, textvariable=var, width=36).pack(padx=12, pady=(0, 4))

    def browse_image(self):
        path = filedialog.askopenfilename(title="Select Image",
                                          filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if path:
            self.selected_image = path
            self.image_label.config(text=os.path.basename(path))

    def clear_fields(self):
        self.name_var.set("")
        self.age_var.set("")
        self.prof_var.set("")
        self.sal_var.set("")
        self.selected_image = None
        self.image_label.config(text="No image selected")

    def clear_search(self):
        self.search_var.set("")
        self.filter_var.set("All")
        self.load_data()

    def add_user(self):
        name = self.name_var.get().strip()
        age = self.age_var.get().strip()
        prof = self.prof_var.get().strip()
        sal = self.sal_var.get().strip()
        img = self.selected_image

        if not (name and age and prof and sal and img):
            messagebox.showwarning("Input Error", "All fields including image are required.")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (name, age, profession, salary, image_path) VALUES (?, ?, ?, ?, ?)",
                  (name, age, prof, sal, img))
        conn.commit()
        conn.close()
        self.clear_fields()
        self.load_data()
        messagebox.showinfo("Success", "User added successfully!")

    # ---------------- scrolling ---------------- #
    def _on_mousewheel(self, event):
        if hasattr(event, "delta") and event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(3, "units")

    def _on_shift_mousewheel(self, event):
        if hasattr(event, "delta") and event.delta:
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    # ---------------- load & render ---------------- #
    def load_data(self):
        for w in self.table_frame.winfo_children():
            w.destroy()
        self.image_cache.clear()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Apply search & filter
        query = "SELECT * FROM users WHERE 1=1"
        params = []

        search_text = self.search_var.get().strip().lower()
        if search_text:
            query += " AND (LOWER(name) LIKE ? OR LOWER(profession) LIKE ?)"
            params.extend((f"%{search_text}%", f"%{search_text}%"))

        filter_text = self.filter_var.get()
        if filter_text != "All":
            query += " AND profession = ?"
            params.append(filter_text)

        c.execute(query, params)
        rows = c.fetchall()

        # Populate filter dropdown with all professions
        c.execute("SELECT DISTINCT profession FROM users")
        professions = ["All"] + [r[0] for r in c.fetchall()]
        self.filter_menu["values"] = professions

        conn.close()

        headers = ["Image", "Name", "Age", "Profession", "Salary", "Actions"]
        header_bg = "#93c5fd"
        for col, text in enumerate(headers):
            lbl = tk.Label(self.table_frame, text=text, bg=header_bg, font=("Arial", 11, "bold"),
                           bd=1, relief="ridge", padx=6, pady=6)
            lbl.grid(row=0, column=col, sticky="nsew")

        # Column sizes
        self.table_frame.grid_columnconfigure(0, minsize=90)
        self.table_frame.grid_columnconfigure(1, minsize=200)
        self.table_frame.grid_columnconfigure(2, minsize=80)
        self.table_frame.grid_columnconfigure(3, minsize=260)
        self.table_frame.grid_columnconfigure(4, minsize=120)
        self.table_frame.grid_columnconfigure(5, minsize=160)

        # Data rows
        for r, row in enumerate(rows, start=1):
            uid, name, age, profession, salary, image_path = row
            row_bg = "#ffffff" if r % 2 == 0 else "#f3f4f6"

            # Image thumbnail
            if image_path and os.path.exists(image_path):
                try:
                    im = Image.open(image_path)
                    im.thumbnail((72, 72))
                    photo = ImageTk.PhotoImage(im)
                    self.image_cache[uid] = photo
                    lbl_img = tk.Label(self.table_frame, image=photo, bg=row_bg)
                except:
                    lbl_img = tk.Label(self.table_frame, text="No Img", bg=row_bg, width=12, height=4)
            else:
                lbl_img = tk.Label(self.table_frame, text="No Img", bg=row_bg, width=12, height=4)

            lbl_img.grid(row=r, column=0, padx=6, pady=6, sticky="nsew")

            tk.Label(self.table_frame, text=name, bg=row_bg, anchor="w", padx=8).grid(row=r, column=1, sticky="nsew")
            tk.Label(self.table_frame, text=age, bg=row_bg, anchor="center").grid(row=r, column=2, sticky="nsew")
            tk.Label(self.table_frame, text=profession, bg=row_bg, anchor="w", padx=8).grid(row=r, column=3, sticky="nsew")
            tk.Label(self.table_frame, text=str(salary), bg=row_bg, anchor="e", padx=8).grid(row=r, column=4, sticky="nsew")

            # Buttons
            btn_frame = tk.Frame(self.table_frame, bg=row_bg)
            upd_btn = tk.Button(btn_frame, text="Update", bg="#16a34a", fg="white",
                                relief="raised", padx=8, pady=4,
                                command=lambda _id=uid: self.open_update_window(_id))
            del_btn = tk.Button(btn_frame, text="Delete", bg="#dc2626", fg="white",
                                relief="raised", padx=8, pady=4,
                                command=lambda _id=uid: self.delete_user(_id))
            upd_btn.bind("<Enter>", lambda e, b=upd_btn: b.config(bg="#1f7a2e"))
            upd_btn.bind("<Leave>", lambda e, b=upd_btn: b.config(bg="#16a34a"))
            del_btn.bind("<Enter>", lambda e, b=del_btn: b.config(bg="#ff5b5b"))
            del_btn.bind("<Leave>", lambda e, b=del_btn: b.config(bg="#dc2626"))
            upd_btn.pack(side="left", padx=(0, 6))
            del_btn.pack(side="left")
            btn_frame.grid(row=r, column=5, padx=6, pady=6, sticky="nsew")

        self.table_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # ---------------- update flow ---------------- #
    def open_update_window(self, uid):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (uid,))
        data = c.fetchone()
        conn.close()
        if not data:
            messagebox.showerror("Error", "User not found.")
            return

        _, name, age, profession, salary, img_path = data
        win = tk.Toplevel(self.root)
        win.title("Update User")
        win.geometry("420x320")
        win.transient(self.root)

        name_v, age_v, prof_v, sal_v = tk.StringVar(value=name), tk.StringVar(value=str(age)), \
                                       tk.StringVar(value=profession), tk.StringVar(value=str(salary))
        new_image = img_path

        tk.Label(win, text="Name:").pack(anchor="w", padx=12, pady=(12, 0))
        tk.Entry(win, textvariable=name_v, width=48).pack(padx=12)
        tk.Label(win, text="Age:").pack(anchor="w", padx=12, pady=(8, 0))
        tk.Entry(win, textvariable=age_v, width=48).pack(padx=12)
        tk.Label(win, text="Profession:").pack(anchor="w", padx=12, pady=(8, 0))
        tk.Entry(win, textvariable=prof_v, width=48).pack(padx=12)
        tk.Label(win, text="Salary:").pack(anchor="w", padx=12, pady=(8, 0))
        tk.Entry(win, textvariable=sal_v, width=48).pack(padx=12)

        img_lbl = tk.Label(win, text=os.path.basename(img_path) if img_path else "No image", fg="blue")
        img_lbl.pack(pady=(10, 6))

        def change_image():
            nonlocal new_image
            p = filedialog.askopenfilename(title="Select new image",
                                           filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
            if p:
                new_image = p
                img_lbl.config(text=os.path.basename(p))

        tk.Button(win, text="Change Image", command=change_image, bg="#2563eb", fg="white").pack(pady=(0, 6))

        def save_update():
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE users SET name=?, age=?, profession=?, salary=?, image_path=? WHERE id=?",
                      (name_v.get().strip(), age_v.get().strip(), prof_v.get().strip(), sal_v.get().strip(),
                       new_image, uid))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User updated.")
            win.destroy()
            self.load_data()

        tk.Button(win, text="Save Update", command=save_update, bg="#16a34a", fg="white").pack(pady=10)

    # ---------------- delete ---------------- #
    def delete_user(self, uid):
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()
        conn.close()
        self.load_data()


# ---------------- run ---------------- #
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = CRUDApp(root)
    root.mainloop()
    