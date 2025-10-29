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



















# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# from PIL import Image, ImageTk
# import sqlite3
# import os

# # ---------------- DATABASE ---------------- #
# def init_db():
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             age INTEGER,
#             profession TEXT,
#             salary REAL,
#             image_path TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()

# # ---------------- MAIN CLASS ---------------- #
# class CRUDApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tkinter CRUD App")
#         self.root.geometry("1000x600")
#         self.root.config(bg="#f0f0f0")

#         self.selected_image = None

#         # ---------- LEFT FRAME: FORM ---------- #
#         left_frame = tk.Frame(self.root, bg="#dbeafe", bd=2, relief="groove")
#         left_frame.place(x=10, y=10, width=350, height=580)

#         tk.Label(left_frame, text="User Details", font=("Arial", 18, "bold"), bg="#dbeafe").pack(pady=10)

#         # Name
#         tk.Label(left_frame, text="Name:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         self.name_var = tk.StringVar()
#         tk.Entry(left_frame, textvariable=self.name_var, width=35).pack(padx=10, pady=2)

#         # Age
#         tk.Label(left_frame, text="Age:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         self.age_var = tk.StringVar()
#         tk.Entry(left_frame, textvariable=self.age_var, width=35).pack(padx=10, pady=2)

#         # Profession
#         tk.Label(left_frame, text="Profession:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         self.prof_var = tk.StringVar()
#         tk.Entry(left_frame, textvariable=self.prof_var, width=35).pack(padx=10, pady=2)

#         # Salary
#         tk.Label(left_frame, text="Salary:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         self.sal_var = tk.StringVar()
#         tk.Entry(left_frame, textvariable=self.sal_var, width=35).pack(padx=10, pady=2)

#         # Image upload
#         tk.Label(left_frame, text="Image:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         self.image_label = tk.Label(left_frame, text="No image selected", bg="#dbeafe")
#         self.image_label.pack(pady=2)
#         tk.Button(left_frame, text="Browse Image", command=self.browse_image, bg="#2563eb", fg="white").pack(pady=5)

#         # Buttons
#         tk.Button(left_frame, text="Add User", bg="#16a34a", fg="white", command=self.add_user).pack(pady=10)
#         tk.Button(left_frame, text="Clear Fields", bg="#facc15", command=self.clear_fields).pack()

#         # ---------- RIGHT FRAME: TABLE ---------- #
#         right_frame = tk.Frame(self.root, bg="#e0f2fe", bd=2, relief="groove")
#         right_frame.place(x=370, y=10, width=620, height=580)

#         tk.Label(right_frame, text="User Records", font=("Arial", 18, "bold"), bg="#e0f2fe").pack(pady=10)

#         # Table setup
#         columns = ("img", "name", "age", "profession", "salary", "update", "delete")
#         self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)

#         self.tree.heading("img", text="Image")
#         self.tree.heading("name", text="Name")
#         self.tree.heading("age", text="Age")
#         self.tree.heading("profession", text="Profession")
#         self.tree.heading("salary", text="Salary")
#         self.tree.heading("update", text="Update")
#         self.tree.heading("delete", text="Delete")

#         self.tree.column("img", width=80)
#         self.tree.column("name", width=120)
#         self.tree.column("age", width=60)
#         self.tree.column("profession", width=120)
#         self.tree.column("salary", width=100)
#         self.tree.column("update", width=60)
#         self.tree.column("delete", width=60)

#         self.tree.pack(fill="both", expand=True, padx=10, pady=10)

#         self.tree.bind("<ButtonRelease-1>", self.handle_action)

#         self.load_data()

#     # ---------- FUNCTIONS ---------- #
#     def browse_image(self):
#         file_path = filedialog.askopenfilename(title="Select Image",
#                                                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
#         if file_path:
#             self.selected_image = file_path
#             self.image_label.config(text=os.path.basename(file_path))

#     def add_user(self):
#         name = self.name_var.get()
#         age = self.age_var.get()
#         profession = self.prof_var.get()
#         salary = self.sal_var.get()
#         img = self.selected_image

#         if not (name and age and profession and salary and img):
#             messagebox.showwarning("Input Error", "All fields including image are required.")
#             return

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("INSERT INTO users (name, age, profession, salary, image_path) VALUES (?, ?, ?, ?, ?)",
#                   (name, age, profession, salary, img))
#         conn.commit()
#         conn.close()

#         messagebox.showinfo("Success", "User added successfully!")
#         self.clear_fields()
#         self.load_data()

#     def clear_fields(self):
#         self.name_var.set("")
#         self.age_var.set("")
#         self.prof_var.set("")
#         self.sal_var.set("")
#         self.selected_image = None
#         self.image_label.config(text="No image selected")

#     def load_data(self):
#         for item in self.tree.get_children():
#             self.tree.delete(item)

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM users")
#         rows = c.fetchall()
#         conn.close()

#         for row in rows:
#             self.tree.insert("", "end", values=(
#                 "📷", row[1], row[2], row[3], row[4], "✏️", "🗑️"
#             ), tags=(row[0],))

#     def handle_action(self, event):
#         item = self.tree.identify_row(event.y)
#         col = self.tree.identify_column(event.x)
#         if not item:
#             return
#         user_id = self.tree.item(item, "tags")[0]

#         if col == "#6":  # Update column
#             self.update_user(user_id)
#         elif col == "#7":  # Delete column
#             self.delete_user(user_id)

#     def update_user(self, user_id):
#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE id=?", (user_id,))
#         data = c.fetchone()
#         conn.close()

#         if not data:
#             messagebox.showerror("Error", "User not found.")
#             return

#         self.name_var.set(data[1])
#         self.age_var.set(data[2])
#         self.prof_var.set(data[3])
#         self.sal_var.set(data[4])
#         self.selected_image = data[5]
#         self.image_label.config(text=os.path.basename(data[5]))

#         def save_update():
#             conn = sqlite3.connect("database.db")
#             c = conn.cursor()
#             c.execute("""
#                 UPDATE users SET name=?, age=?, profession=?, salary=?, image_path=? WHERE id=?
#             """, (self.name_var.get(), self.age_var.get(), self.prof_var.get(),
#                   self.sal_var.get(), self.selected_image, user_id))
#             conn.commit()
#             conn.close()
#             messagebox.showinfo("Success", "User updated successfully!")
#             update_win.destroy()
#             self.clear_fields()
#             self.load_data()

#         update_win = tk.Toplevel(self.root)
#         update_win.title("Update User")
#         update_win.geometry("300x150")
#         tk.Label(update_win, text="Click Save to update details").pack(pady=10)
#         tk.Button(update_win, text="Save Update", bg="#16a34a", fg="white", command=save_update).pack(pady=10)

#     def delete_user(self, user_id):
#         res = messagebox.askyesno("Confirm Delete", "Are you sure to delete this user?")
#         if res:
#             conn = sqlite3.connect("database.db")
#             c = conn.cursor()
#             c.execute("DELETE FROM users WHERE id=?", (user_id,))
#             conn.commit()
#             conn.close()
#             self.load_data()
#             messagebox.showinfo("Deleted", "User deleted successfully!")


# # ---------------- RUN APP ---------------- #
# if __name__ == "__main__":
#     init_db()
#     root = tk.Tk()
#     app = CRUDApp(root)
#     root.mainloop()




# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# from PIL import Image, ImageTk
# import sqlite3
# import os

# # ========== DATABASE SETUP ==========
# def init_db():
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             age INTEGER,
#             profession TEXT,
#             salary REAL,
#             image_path TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()


# # ========== MAIN APPLICATION ==========
# class CRUDApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tkinter CRUD App")
#         self.root.geometry("1100x600")
#         self.root.config(bg="#f0f0f0")

#         self.selected_image = None
#         self.images_cache = {}  # To prevent garbage collection of images

#         # ---------- LEFT FRAME ----------
#         left_frame = tk.Frame(self.root, bg="#dbeafe", bd=2, relief="groove")
#         left_frame.place(x=10, y=10, width=350, height=580)

#         tk.Label(left_frame, text="User Details", font=("Arial", 18, "bold"), bg="#dbeafe").pack(pady=10)

#         self.name_var = tk.StringVar()
#         self.age_var = tk.StringVar()
#         self.prof_var = tk.StringVar()
#         self.sal_var = tk.StringVar()

#         self.create_field(left_frame, "Name", self.name_var)
#         self.create_field(left_frame, "Age", self.age_var)
#         self.create_field(left_frame, "Profession", self.prof_var)
#         self.create_field(left_frame, "Salary", self.sal_var)

#         # Image browse
#         tk.Label(left_frame, text="Image:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         self.image_label = tk.Label(left_frame, text="No image selected", bg="#dbeafe")
#         self.image_label.pack(pady=2)
#         tk.Button(left_frame, text="Browse Image", command=self.browse_image, bg="#2563eb", fg="white").pack(pady=5)

#         # Buttons
#         tk.Button(left_frame, text="Add User", bg="#16a34a", fg="white", command=self.add_user, width=20).pack(pady=10)
#         tk.Button(left_frame, text="Clear Fields", bg="#facc15", command=self.clear_fields, width=20).pack()

#         # ---------- RIGHT FRAME ----------
#         right_frame = tk.Frame(self.root, bg="#e0f2fe", bd=2, relief="groove")
#         right_frame.place(x=370, y=10, width=720, height=580)

#         tk.Label(right_frame, text="User Records", font=("Arial", 18, "bold"), bg="#e0f2fe").pack(pady=10)

#         # Treeview
#         columns = ("name", "age", "profession", "salary")
#         self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=20)
#         self.tree.heading("name", text="Name")
#         self.tree.heading("age", text="Age")
#         self.tree.heading("profession", text="Profession")
#         self.tree.heading("salary", text="Salary")

#         self.tree.column("name", width=150)
#         self.tree.column("age", width=60)
#         self.tree.column("profession", width=150)
#         self.tree.column("salary", width=100)

#         # Add Treeview + Scrollbar
#         vsb = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=vsb.set)
#         vsb.pack(side="right", fill="y")
#         self.tree.pack(fill="both", expand=True, padx=10, pady=10)

#         # Canvas for dynamic widgets
#         self.table_frame = tk.Frame(self.tree)
#         self.table_frame.place(relx=1.0, rely=0, anchor="ne")

#         self.load_data()

#     # ========== FIELD CREATOR ==========
#     def create_field(self, parent, label_text, var):
#         tk.Label(parent, text=f"{label_text}:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         tk.Entry(parent, textvariable=var, width=35).pack(padx=10, pady=2)

#     # ========== BROWSE IMAGE ==========
#     def browse_image(self):
#         file_path = filedialog.askopenfilename(
#             title="Select Image",
#             filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
#         )
#         if file_path:
#             self.selected_image = file_path
#             self.image_label.config(text=os.path.basename(file_path))

#     # ========== ADD USER ==========
#     def add_user(self):
#         name = self.name_var.get()
#         age = self.age_var.get()
#         profession = self.prof_var.get()
#         salary = self.sal_var.get()
#         img = self.selected_image

#         if not (name and age and profession and salary and img):
#             messagebox.showwarning("Input Error", "All fields including image are required.")
#             return

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("INSERT INTO users (name, age, profession, salary, image_path) VALUES (?, ?, ?, ?, ?)",
#                   (name, age, profession, salary, img))
#         conn.commit()
#         conn.close()

#         messagebox.showinfo("Success", "User added successfully!")
#         self.clear_fields()
#         self.load_data()

#     # ========== CLEAR FIELDS ==========
#     def clear_fields(self):
#         self.name_var.set("")
#         self.age_var.set("")
#         self.prof_var.set("")
#         self.sal_var.set("")
#         self.selected_image = None
#         self.image_label.config(text="No image selected")

#     # ========== LOAD DATA ==========
#     def load_data(self):
#         for item in self.tree.get_children():
#             self.tree.delete(item)
#         self.images_cache.clear()

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM users")
#         rows = c.fetchall()
#         conn.close()

#         for row in rows:
#             user_id, name, age, profession, salary, image_path = row

#             # Create small thumbnail
#             try:
#                 img = Image.open(image_path)
#                 img.thumbnail((40, 40))
#                 photo = ImageTk.PhotoImage(img)
#                 self.images_cache[user_id] = photo
#             except:
#                 photo = None

#             # Insert data into table
#             self.tree.insert("", "end", iid=user_id, values=(name, age, profession, salary))

#             # Place image and buttons manually
#             self.tree.update_idletasks()
#             bbox = self.tree.bbox(user_id)
#             if bbox:
#                 y = bbox[1] + bbox[3] // 2
#                 # Place image thumbnail
#                 if photo:
#                     lbl = tk.Label(self.tree, image=photo)
#                     lbl.image = photo
#                     lbl.place(x=10, y=y - 20)

#                 # Update button
#                 tk.Button(self.tree, text="Update", bg="#16a34a", fg="white",
#                           command=lambda uid=user_id: self.update_user(uid)).place(x=600, y=y - 15)
#                 # Delete button
#                 tk.Button(self.tree, text="Delete", bg="#dc2626", fg="white",
#                           command=lambda uid=user_id: self.delete_user(uid)).place(x=670, y=y - 15)

#     # ========== UPDATE USER ==========
#     def update_user(self, user_id):
#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE id=?", (user_id,))
#         data = c.fetchone()
#         conn.close()

#         if not data:
#             messagebox.showerror("Error", "User not found.")
#             return

#         self.name_var.set(data[1])
#         self.age_var.set(data[2])
#         self.prof_var.set(data[3])
#         self.sal_var.set(data[4])
#         self.selected_image = data[5]
#         self.image_label.config(text=os.path.basename(data[5]))

#         def save_update():
#             conn = sqlite3.connect("database.db")
#             c = conn.cursor()
#             c.execute("""
#                 UPDATE users SET name=?, age=?, profession=?, salary=?, image_path=? WHERE id=?
#             """, (self.name_var.get(), self.age_var.get(), self.prof_var.get(),
#                   self.sal_var.get(), self.selected_image, user_id))
#             conn.commit()
#             conn.close()
#             messagebox.showinfo("Success", "User updated successfully!")
#             update_win.destroy()
#             self.clear_fields()
#             self.load_data()

#         update_win = tk.Toplevel(self.root)
#         update_win.title("Update User")
#         update_win.geometry("300x150")
#         tk.Label(update_win, text="Click Save to update details").pack(pady=10)
#         tk.Button(update_win, text="Save Update", bg="#16a34a", fg="white", command=save_update).pack(pady=10)

#     # ========== DELETE USER ==========
#     def delete_user(self, user_id):
#         res = messagebox.askyesno("Confirm Delete", "Are you sure to delete this user?")
#         if res:
#             conn = sqlite3.connect("database.db")
#             c = conn.cursor()
#             c.execute("DELETE FROM users WHERE id=?", (user_id,))
#             conn.commit()
#             conn.close()
#             self.load_data()
#             messagebox.showinfo("Deleted", "User deleted successfully!")


# # ========== RUN APP ==========
# if __name__ == "__main__":
#     init_db()
#     root = tk.Tk()
#     app = CRUDApp(root)
#     root.mainloop()



# import tkinter as tk
# from tkinter import filedialog, messagebox
# from PIL import Image, ImageTk
# import sqlite3, os

# # ---------------- DATABASE ---------------- #
# def init_db():
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT,
#         age INTEGER,
#         profession TEXT,
#         salary REAL,
#         image_path TEXT
#     )''')
#     conn.commit()
#     conn.close()

# # ---------------- MAIN APP ---------------- #
# class CRUDApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tkinter CRUD App")
#         self.root.geometry("1100x600")
#         self.root.config(bg="#f0f0f0")

#         self.selected_image = None
#         self.image_cache = {}

#         # ---------- LEFT PANEL ----------
#         left = tk.Frame(root, bg="#dbeafe", bd=2, relief="groove")
#         left.place(x=10, y=10, width=350, height=580)

#         tk.Label(left, text="User Details", font=("Arial", 18, "bold"), bg="#dbeafe").pack(pady=10)

#         self.name_var = tk.StringVar()
#         self.age_var = tk.StringVar()
#         self.prof_var = tk.StringVar()
#         self.sal_var = tk.StringVar()

#         self.create_field(left, "Name", self.name_var)
#         self.create_field(left, "Age", self.age_var)
#         self.create_field(left, "Profession", self.prof_var)
#         self.create_field(left, "Salary", self.sal_var)

#         tk.Label(left, text="Image:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         self.image_label = tk.Label(left, text="No image selected", bg="#dbeafe")
#         self.image_label.pack(pady=2)
#         tk.Button(left, text="Browse Image", command=self.browse_image, bg="#2563eb", fg="white").pack(pady=5)

#         tk.Button(left, text="Add User", bg="#16a34a", fg="white", width=20, command=self.add_user).pack(pady=10)
#         tk.Button(left, text="Clear Fields", bg="#facc15", width=20, command=self.clear_fields).pack()

#         # ---------- RIGHT PANEL ----------
#         right = tk.Frame(root, bg="#e0f2fe", bd=2, relief="groove")
#         right.place(x=370, y=10, width=720, height=580)
#         tk.Label(right, text="User Records", font=("Arial", 18, "bold"), bg="#e0f2fe").pack(pady=10)

#         # Canvas with scrollbar
#         self.canvas = tk.Canvas(right, bg="white", highlightthickness=0)
#         self.scrollbar = tk.Scrollbar(right, orient="vertical", command=self.canvas.yview)
#         self.scrollbar.pack(side="right", fill="y")
#         self.canvas.pack(fill="both", expand=True)
#         self.canvas.configure(yscrollcommand=self.scrollbar.set)

#         self.table_frame = tk.Frame(self.canvas, bg="white")
#         self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

#         self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

#         self.load_data()

#     def create_field(self, parent, label, var):
#         tk.Label(parent, text=f"{label}:", bg="#dbeafe").pack(anchor="w", padx=10, pady=2)
#         tk.Entry(parent, textvariable=var, width=35).pack(padx=10, pady=2)

#     def browse_image(self):
#         path = filedialog.askopenfilename(title="Select Image",
#                                           filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
#         if path:
#             self.selected_image = path
#             self.image_label.config(text=os.path.basename(path))

#     def add_user(self):
#         name, age, prof, sal, img = self.name_var.get(), self.age_var.get(), self.prof_var.get(), self.sal_var.get(), self.selected_image
#         if not (name and age and prof and sal and img):
#             messagebox.showwarning("Error", "All fields including image are required.")
#             return
#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("INSERT INTO users (name, age, profession, salary, image_path) VALUES (?, ?, ?, ?, ?)",
#                   (name, age, prof, sal, img))
#         conn.commit()
#         conn.close()
#         messagebox.showinfo("Success", "User added successfully!")
#         self.clear_fields()
#         self.load_data()

#     def clear_fields(self):
#         self.name_var.set("")
#         self.age_var.set("")
#         self.prof_var.set("")
#         self.sal_var.set("")
#         self.selected_image = None
#         self.image_label.config(text="No image selected")

#     def load_data(self):
#         for widget in self.table_frame.winfo_children():
#             widget.destroy()

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM users")
#         rows = c.fetchall()
#         conn.close()

#         # Header
#         headers = ["Image", "Name", "Age", "Profession", "Salary", "Actions"]
#         for i, h in enumerate(headers):
#             tk.Label(self.table_frame, text=h, bg="#93c5fd", font=("Arial", 12, "bold"), width=15, relief="ridge").grid(row=0, column=i, padx=1, pady=1, sticky="nsew")

#         # Rows
#         for r, row in enumerate(rows, start=1):
#             uid, name, age, prof, sal, img = row

#             # Image Thumbnail
#             try:
#                 im = Image.open(img)
#                 im.thumbnail((50, 50))
#                 photo = ImageTk.PhotoImage(im)
#                 self.image_cache[uid] = photo
#                 tk.Label(self.table_frame, image=photo, bg="white").grid(row=r, column=0, padx=5, pady=5)
#             except:
#                 tk.Label(self.table_frame, text="No Img", bg="white").grid(row=r, column=0, padx=5, pady=5)

#             tk.Label(self.table_frame, text=name, bg="white", width=15).grid(row=r, column=1)
#             tk.Label(self.table_frame, text=age, bg="white", width=10).grid(row=r, column=2)
#             tk.Label(self.table_frame, text=prof, bg="white", width=20).grid(row=r, column=3)
#             tk.Label(self.table_frame, text=f"₹{sal}", bg="white", width=12).grid(row=r, column=4)

#             # Update & Delete Buttons
#             btn_frame = tk.Frame(self.table_frame, bg="white")
#             tk.Button(btn_frame, text="Update", bg="#16a34a", fg="white", command=lambda id=uid: self.update_user(id)).pack(side="left", padx=5)
#             tk.Button(btn_frame, text="Delete", bg="#dc2626", fg="white", command=lambda id=uid: self.delete_user(id)).pack(side="left")
#             btn_frame.grid(row=r, column=5, padx=5, pady=5)

#     def update_user(self, uid):
#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE id=?", (uid,))
#         data = c.fetchone()
#         conn.close()
#         if not data: return

#         self.name_var.set(data[1])
#         self.age_var.set(data[2])
#         self.prof_var.set(data[3])
#         self.sal_var.set(data[4])
#         self.selected_image = data[5]
#         self.image_label.config(text=os.path.basename(data[5]))

#         def save_update():
#             conn = sqlite3.connect("database.db")
#             c = conn.cursor()
#             c.execute("""UPDATE users SET name=?, age=?, profession=?, salary=?, image_path=? WHERE id=?""",
#                       (self.name_var.get(), self.age_var.get(), self.prof_var.get(),
#                        self.sal_var.get(), self.selected_image, uid))
#             conn.commit()
#             conn.close()
#             messagebox.showinfo("Success", "User updated successfully!")
#             win.destroy()
#             self.clear_fields()
#             self.load_data()

#         win = tk.Toplevel(self.root)
#         win.title("Update User")
#         win.geometry("300x150")
#         tk.Label(win, text="Click Save to update user").pack(pady=10)
#         tk.Button(win, text="Save Update", bg="#16a34a", fg="white", command=save_update).pack(pady=10)

#     def delete_user(self, uid):
#         if messagebox.askyesno("Confirm", "Delete this user?"):
#             conn = sqlite3.connect("database.db")
#             c = conn.cursor()
#             c.execute("DELETE FROM users WHERE id=?", (uid,))
#             conn.commit()
#             conn.close()
#             self.load_data()

# # ---------------- RUN APP ---------------- #
# if __name__ == "__main__":
#     init_db()
#     root = tk.Tk()
#     app = CRUDApp(root)
#     root.mainloop()






# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# from PIL import Image, ImageTk
# import sqlite3
# import os

# DB_PATH = "Tkinter_Task-2_database.db"


# # ---------------- DATABASE ---------------- #
# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             age INTEGER,
#             profession TEXT,
#             salary REAL,
#             image_path TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()


# # ---------------- APP ---------------- #
# class CRUDApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tkinter CRUD App")
#         self.root.geometry("1150x650")
#         self.root.config(bg="#f0f0f0")

#         self.selected_image = None
#         self.image_cache = {}
#         self.search_var = tk.StringVar()
#         self.filter_by = tk.StringVar(value="All")

#         # ---------- LEFT PANEL ----------
#         left = tk.Frame(root, bg="#dbeafe", bd=2, relief="groove")
#         left.place(x=10, y=10, width=360, height=630)
#         tk.Label(left, text="User Details", font=("Arial", 18, "bold"), bg="#dbeafe").pack(pady=12)

#         self.name_var = tk.StringVar()
#         self.age_var = tk.StringVar()
#         self.prof_var = tk.StringVar()
#         self.sal_var = tk.StringVar()

#         self._create_field(left, "Name", self.name_var)
#         self._create_field(left, "Age", self.age_var)
#         self._create_field(left, "Profession", self.prof_var)
#         self._create_field(left, "Salary", self.sal_var)

#         tk.Label(left, text="Image:", bg="#dbeafe").pack(anchor="w", padx=12, pady=(6, 0))
#         self.image_label = tk.Label(left, text="No image selected", bg="#dbeafe")
#         self.image_label.pack(pady=(2, 6))
#         tk.Button(left, text="Browse Image", command=self.browse_image, bg="#2563eb", fg="white").pack()

#         tk.Button(left, text="Add User", bg="#16a34a", fg="white", width=20, command=self.add_user).pack(pady=12)
#         tk.Button(left, text="Clear Fields", bg="#facc15", width=20, command=self.clear_fields).pack()

#         # ---------- RIGHT PANEL ----------
#         right = tk.Frame(root, bg="#e0f2fe", bd=2, relief="groove")
#         right.place(x=380, y=10, width=760, height=630)

#         # Title
#         tk.Label(right, text="User Records", font=("Arial", 18, "bold"), bg="#e0f2fe").pack(pady=6)

#         # Search and Filter
#         search_frame = tk.Frame(right, bg="#e0f2fe")
#         search_frame.pack(fill="x", padx=10, pady=5)

#         tk.Label(search_frame, text="Search:", bg="#e0f2fe", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
#         search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
#         search_entry.pack(side="left", padx=(0, 10))
#         search_entry.bind("<KeyRelease>", lambda e: self.load_data())

#         tk.Label(search_frame, text="Filter by:", bg="#e0f2fe", font=("Arial", 10, "bold")).pack(side="left")
#         filter_box = ttk.Combobox(search_frame, textvariable=self.filter_by, values=["All", "Name", "Profession"], width=15, state="readonly")
#         filter_box.pack(side="left", padx=(5, 0))
#         filter_box.bind("<<ComboboxSelected>>", lambda e: self.load_data())

#         # Table area
#         right_inner = tk.Frame(right, bg="#e0f2fe")
#         right_inner.pack(fill="both", expand=True, padx=10, pady=(0, 10))

#         self.canvas = tk.Canvas(right_inner, bg="white", highlightthickness=0)
#         self.vsb = tk.Scrollbar(right_inner, orient="vertical", command=self.canvas.yview)
#         self.hsb = tk.Scrollbar(right_inner, orient="horizontal", command=self.canvas.xview)
#         self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

#         self.canvas.grid(row=0, column=0, sticky="nsew")
#         self.vsb.grid(row=0, column=1, sticky="ns")
#         self.hsb.grid(row=1, column=0, sticky="ew")

#         right_inner.grid_rowconfigure(0, weight=1)
#         right_inner.grid_columnconfigure(0, weight=1)

#         self.table_frame = tk.Frame(self.canvas, bg="white")
#         self.canvas_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
#         self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

#         self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
#         self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

#         self.load_data()

#     # ---------------- FIELDS ---------------- #
#     def _create_field(self, parent, label_text, var):
#         tk.Label(parent, text=f"{label_text}:", bg="#dbeafe").pack(anchor="w", padx=12, pady=(6, 2))
#         tk.Entry(parent, textvariable=var, width=36).pack(padx=12, pady=(0, 4))

#     def browse_image(self):
#         path = filedialog.askopenfilename(title="Select Image",
#                                           filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
#         if path:
#             self.selected_image = path
#             self.image_label.config(text=os.path.basename(path))

#     def clear_fields(self):
#         self.name_var.set("")
#         self.age_var.set("")
#         self.prof_var.set("")
#         self.sal_var.set("")
#         self.selected_image = None
#         self.image_label.config(text="No image selected")

#     # ---------------- CRUD FUNCTIONS ---------------- #
#     def add_user(self):
#         name = self.name_var.get().strip()
#         age = self.age_var.get().strip()
#         prof = self.prof_var.get().strip()
#         sal = self.sal_var.get().strip()
#         img = self.selected_image

#         if not (name and age and prof and sal and img):
#             messagebox.showwarning("Input Error", "All fields including image are required.")
#             return

#         conn = sqlite3.connect(DB_PATH)
#         c = conn.cursor()
#         c.execute("INSERT INTO users (name, age, profession, salary, image_path) VALUES (?, ?, ?, ?, ?)",
#                   (name, age, prof, sal, img))
#         conn.commit()
#         conn.close()
#         messagebox.showinfo("Success", "User added successfully!")
#         self.clear_fields()
#         self.load_data()

#     def delete_user(self, uid):
#         if not messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
#             return
#         conn = sqlite3.connect(DB_PATH)
#         c = conn.cursor()
#         c.execute("DELETE FROM users WHERE id=?", (uid,))
#         conn.commit()
#         conn.close()
#         self.load_data()

#     def open_update_window(self, uid):
#         conn = sqlite3.connect(DB_PATH)
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE id=?", (uid,))
#         data = c.fetchone()
#         conn.close()

#         if not data:
#             messagebox.showerror("Error", "User not found.")
#             return

#         _, name, age, profession, salary, img_path = data
#         win = tk.Toplevel(self.root)
#         win.title("Update User")
#         win.geometry("420x320")

#         name_v, age_v, prof_v, sal_v = tk.StringVar(value=name), tk.StringVar(value=age), tk.StringVar(value=profession), tk.StringVar(value=salary)
#         new_image = img_path

#         def change_image():
#             nonlocal new_image
#             path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
#             if path:
#                 new_image = path
#                 img_lbl.config(text=os.path.basename(path))

#         for label, var in [("Name", name_v), ("Age", age_v), ("Profession", prof_v), ("Salary", sal_v)]:
#             tk.Label(win, text=label + ":").pack(anchor="w", padx=12, pady=(8, 0))
#             tk.Entry(win, textvariable=var, width=45).pack(padx=12)

#         img_lbl = tk.Label(win, text=os.path.basename(img_path) if img_path else "No image", fg="blue")
#         img_lbl.pack(pady=(10, 6))
#         tk.Button(win, text="Change Image", command=change_image, bg="#2563eb", fg="white").pack(pady=(0, 6))

#         def save_update():
#             conn = sqlite3.connect(DB_PATH)
#             c = conn.cursor()
#             c.execute("UPDATE users SET name=?, age=?, profession=?, salary=?, image_path=? WHERE id=?",
#                       (name_v.get(), age_v.get(), prof_v.get(), sal_v.get(), new_image, uid))
#             conn.commit()
#             conn.close()
#             messagebox.showinfo("Success", "User updated successfully!")
#             win.destroy()
#             self.load_data()

#         tk.Button(win, text="Save Update", bg="#16a34a", fg="white", command=save_update).pack(pady=8)

#     # ---------------- LOAD DATA ---------------- #
#     def load_data(self):
#         for w in self.table_frame.winfo_children():
#             w.destroy()
#         self.image_cache.clear()

#         conn = sqlite3.connect(DB_PATH)
#         c = conn.cursor()
#         c.execute("SELECT * FROM users")
#         rows = c.fetchall()
#         conn.close()

#         # Apply Search Filter
#         query = self.search_var.get().strip().lower()
#         filter_type = self.filter_by.get()

#         if query:
#             if filter_type == "Name":
#                 rows = [r for r in rows if query in r[1].lower()]
#             elif filter_type == "Profession":
#                 rows = [r for r in rows if query in r[3].lower()]
#             else:
#                 rows = [r for r in rows if query in r[1].lower() or query in r[3].lower()]

#         # Table Header
#         headers = ["Image", "Name", "Age", "Profession", "Salary", "Actions"]
#         for col, text in enumerate(headers):
#             tk.Label(self.table_frame, text=text, bg="#93c5fd", font=("Arial", 11, "bold"), bd=1, relief="ridge", padx=6, pady=6)\
#                 .grid(row=0, column=col, sticky="nsew")

#         for r, row in enumerate(rows, start=1):
#             uid, name, age, prof, sal, img_path = row
#             row_bg = "#ffffff" if r % 2 == 0 else "#f3f4f6"

#             # Image
#             if img_path and os.path.exists(img_path):
#                 img = Image.open(img_path)
#                 img.thumbnail((70, 70))
#                 photo = ImageTk.PhotoImage(img)
#                 self.image_cache[uid] = photo
#                 tk.Label(self.table_frame, image=photo, bg=row_bg).grid(row=r, column=0, padx=4, pady=4)
#             else:
#                 tk.Label(self.table_frame, text="No Img", bg=row_bg, width=12, height=4).grid(row=r, column=0, padx=4, pady=4)

#             tk.Label(self.table_frame, text=name, bg=row_bg, anchor="w", padx=8).grid(row=r, column=1, sticky="nsew")
#             tk.Label(self.table_frame, text=age, bg=row_bg).grid(row=r, column=2, sticky="nsew")
#             tk.Label(self.table_frame, text=prof, bg=row_bg, anchor="w", padx=8).grid(row=r, column=3, sticky="nsew")
#             tk.Label(self.table_frame, text=sal, bg=row_bg, anchor="e", padx=8).grid(row=r, column=4, sticky="nsew")

#             # Action Buttons
#             btn_frame = tk.Frame(self.table_frame, bg=row_bg)
#             upd = tk.Button(btn_frame, text="Update", bg="#16a34a", fg="white", command=lambda id=uid: self.open_update_window(id))
#             dlt = tk.Button(btn_frame, text="Delete", bg="#dc2626", fg="white", command=lambda id=uid: self.delete_user(id))

#             upd.bind("<Enter>", lambda e, b=upd: b.config(bg="#1f7a2e"))
#             upd.bind("<Leave>", lambda e, b=upd: b.config(bg="#16a34a"))
#             dlt.bind("<Enter>", lambda e, b=dlt: b.config(bg="#ff5b5b"))
#             dlt.bind("<Leave>", lambda e, b=dlt: b.config(bg="#dc2626"))

#             upd.pack(side="left", padx=5)
#             dlt.pack(side="left", padx=5)
#             btn_frame.grid(row=r, column=5, padx=4, pady=4, sticky="nsew")

#         self.table_frame.update_idletasks()
#         self.canvas.configure(scrollregion=self.canvas.bbox("all"))

#     # ---------------- SCROLL ---------------- #
#     def _on_mousewheel(self, event):
#         self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# # ---------------- RUN ---------------- #
# if __name__ == "__main__":
#     init_db()
#     root = tk.Tk()
#     CRUDApp(root)
#     root.mainloop()






# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# from PIL import Image, ImageTk
# import os

# root = tk.Tk()
# root.title("Tkinter CRUD App")
# root.geometry("1150x600")
# root.config(bg="white")

# # =====================================================
# # Variables
# # =====================================================
# name_var = tk.StringVar()
# age_var = tk.StringVar()
# profession_var = tk.StringVar()
# salary_var = tk.StringVar()
# img_path = None

# users = []  # list to hold user data

# # =====================================================
# # Left Frame (User Input)
# # =====================================================
# left_frame = tk.Frame(root, bg="#dce6f2", width=300, relief="groove", bd=2)
# left_frame.pack(side="left", fill="y", padx=5, pady=5)

# tk.Label(left_frame, text="User Details", font=("Arial", 16, "bold"), bg="#dce6f2").pack(pady=10)

# tk.Label(left_frame, text="Name:", bg="#dce6f2").pack(anchor="w", padx=10)
# tk.Entry(left_frame, textvariable=name_var).pack(fill="x", padx=10)

# tk.Label(left_frame, text="Age:", bg="#dce6f2").pack(anchor="w", padx=10)
# tk.Entry(left_frame, textvariable=age_var).pack(fill="x", padx=10)

# tk.Label(left_frame, text="Profession:", bg="#dce6f2").pack(anchor="w", padx=10)
# tk.Entry(left_frame, textvariable=profession_var).pack(fill="x", padx=10)

# tk.Label(left_frame, text="Salary:", bg="#dce6f2").pack(anchor="w", padx=10)
# tk.Entry(left_frame, textvariable=salary_var).pack(fill="x", padx=10)

# img_label = tk.Label(left_frame, text="No image selected", bg="#dce6f2", fg="gray")
# img_label.pack(pady=5)

# def browse_image():
#     global img_path
#     path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
#     if path:
#         img_path = path
#         img_label.config(text=os.path.basename(path), fg="black")

# tk.Button(left_frame, text="Browse Image", command=browse_image, bg="#5DADE2", fg="white").pack(pady=5)

# def clear_fields():
#     global img_path
#     name_var.set("")
#     age_var.set("")
#     profession_var.set("")
#     salary_var.set("")
#     img_label.config(text="No image selected", fg="gray")
#     img_path = None

# tk.Button(left_frame, text="Add User", bg="#28B463", fg="white", command=lambda: add_user()).pack(pady=5)
# tk.Button(left_frame, text="Clear Fields", bg="#F1C40F", command=clear_fields).pack(pady=5)

# # =====================================================
# # Right Frame (Table)
# # =====================================================
# right_frame = tk.Frame(root, bg="white", relief="groove", bd=2)
# right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# tk.Label(right_frame, text="User Records", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

# # Search and Filter
# search_frame = tk.Frame(right_frame, bg="white")
# search_frame.pack(fill="x", padx=10, pady=5)

# tk.Label(search_frame, text="Search:", bg="white").pack(side="left")
# search_entry = tk.Entry(search_frame)
# search_entry.pack(side="left", padx=5)

# tk.Label(search_frame, text="Filter by:", bg="white").pack(side="left", padx=10)
# filter_var = tk.StringVar(value="Name")
# filter_dropdown = ttk.Combobox(search_frame, textvariable=filter_var, values=["Name", "Profession"], width=15, state="readonly")
# filter_dropdown.pack(side="left")

# def apply_filter(*args):
#     search = search_entry.get().lower()
#     filter_by = filter_var.get().lower()
#     for widget in table_frame.winfo_children():
#         widget.destroy()
#     display_records([u for u in users if search in str(u[filter_by]).lower()])

# search_entry.bind("<KeyRelease>", lambda e: apply_filter())
# filter_dropdown.bind("<<ComboboxSelected>>", lambda e: apply_filter())

# # =====================================================
# # Table Canvas with Scrollbars
# # =====================================================
# canvas = tk.Canvas(right_frame, bg="white", highlightthickness=0)
# scroll_y = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
# scroll_x = ttk.Scrollbar(right_frame, orient="horizontal", command=canvas.xview)
# canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

# scroll_y.pack(side="right", fill="y")
# scroll_x.pack(side="bottom", fill="x")
# canvas.pack(fill="both", expand=True)

# table_frame = tk.Frame(canvas, bg="white")
# canvas.create_window((0, 0), window=table_frame, anchor="nw")

# def on_frame_configure(event):
#     canvas.configure(scrollregion=canvas.bbox("all"))

# table_frame.bind("<Configure>", on_frame_configure)

# # =====================================================
# # Display Records
# # =====================================================
# def display_records(data):
#     headers = ["Image", "Name", "Age", "Profession", "Salary", "Actions"]

#     for i, col in enumerate(headers):
#         tk.Label(table_frame, text=col, font=("Arial", 10, "bold"), bg="#AED6F1", padx=10, pady=8, borderwidth=1, relief="solid").grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

#     for i, user in enumerate(data, start=1):
#         bg_color = "#F8F9F9" if i % 2 == 0 else "#EBF5FB"

#         img = Image.open(user["image"])
#         img = img.resize((60, 60))
#         photo = ImageTk.PhotoImage(img)
#         img_lbl = tk.Label(table_frame, image=photo, bg=bg_color)
#         img_lbl.image = photo
#         img_lbl.grid(row=i, column=0, padx=10, pady=5)

#         tk.Label(table_frame, text=user["name"], bg=bg_color, width=15).grid(row=i, column=1, padx=10, pady=5)
#         tk.Label(table_frame, text=user["age"], bg=bg_color, width=8).grid(row=i, column=2, padx=10, pady=5)
#         tk.Label(table_frame, text=user["profession"], bg=bg_color, width=18).grid(row=i, column=3, padx=10, pady=5)
#         tk.Label(table_frame, text=user["salary"], bg=bg_color, width=10).grid(row=i, column=4, padx=10, pady=5)

#         btn_frame = tk.Frame(table_frame, bg=bg_color)
#         btn_frame.grid(row=i, column=5, pady=5)

#         update_btn = tk.Button(btn_frame, text="Update", bg="#28B463", fg="white", relief="flat",
#                                command=lambda u=user: update_user(u))
#         delete_btn = tk.Button(btn_frame, text="Delete", bg="#E74C3C", fg="white", relief="flat",
#                                command=lambda u=user: delete_user(u))

#         update_btn.pack(side="left", padx=2)
#         delete_btn.pack(side="left", padx=2)

#         # Hover effects
#         update_btn.bind("<Enter>", lambda e, b=update_btn: b.config(bg="#1D8348"))
#         update_btn.bind("<Leave>", lambda e, b=update_btn: b.config(bg="#28B463"))
#         delete_btn.bind("<Enter>", lambda e, b=delete_btn: b.config(bg="#B03A2E"))
#         delete_btn.bind("<Leave>", lambda e, b=delete_btn: b.config(bg="#E74C3C"))

# # =====================================================
# # CRUD Functions
# # =====================================================
# def add_user():
#     if not (name_var.get() and age_var.get() and profession_var.get() and salary_var.get() and img_path):
#         messagebox.showerror("Error", "Please fill all fields and select an image!")
#         return

#     user = {
#         "name": name_var.get(),
#         "age": age_var.get(),
#         "profession": profession_var.get(),
#         "salary": salary_var.get(),
#         "image": img_path
#     }
#     users.append(user)
#     clear_fields()
#     display_records(users)

# def update_user(user):
#     name_var.set(user["name"])
#     age_var.set(user["age"])
#     profession_var.set(user["profession"])
#     salary_var.set(user["salary"])
#     global img_path
#     img_path = user["image"]

#     users.remove(user)
#     display_records(users)

# def delete_user(user):
#     users.remove(user)
#     display_records(users)

# display_records(users)

# root.mainloop()




# import tkinter as tk
# from tkinter import ttk, filedialog, messagebox
# from PIL import Image, ImageTk
# import os
# import sqlite3

# # =====================================================
# # Database Setup
# # =====================================================
# conn = sqlite2 = sqlite3.connect("Tkinter_Task-2_database.db")
# cursor = conn.cursor()
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT,
#     age TEXT,
#     profession TEXT,
#     salary TEXT,
#     image TEXT
# )
# """)
# conn.commit()

# # =====================================================
# # Tkinter App Setup
# # =====================================================
# root = tk.Tk()
# root.title("Tkinter CRUD App")
# root.geometry("1150x600")
# root.config(bg="white")

# # =====================================================
# # Variables
# # =====================================================
# name_var = tk.StringVar()
# age_var = tk.StringVar()
# profession_var = tk.StringVar()
# salary_var = tk.StringVar()
# img_path = None

# # =====================================================
# # Left Frame (User Input)
# # =====================================================
# left_frame = tk.Frame(root, bg="#dce6f2", width=300, relief="groove", bd=2)
# left_frame.pack(side="left", fill="y", padx=5, pady=5)

# tk.Label(left_frame, text="User Details", font=("Arial", 16, "bold"), bg="#dce6f2").pack(pady=10)

# tk.Label(left_frame, text="Name:", bg="#dce6f2").pack(anchor="w", padx=10)
# tk.Entry(left_frame, textvariable=name_var).pack(fill="x", padx=10)

# tk.Label(left_frame, text="Age:", bg="#dce6f2").pack(anchor="w", padx=10)
# tk.Entry(left_frame, textvariable=age_var).pack(fill="x", padx=10)

# tk.Label(left_frame, text="Profession:", bg="#dce6f2").pack(anchor="w", padx=10)
# tk.Entry(left_frame, textvariable=profession_var).pack(fill="x", padx=10)

# tk.Label(left_frame, text="Salary:", bg="#dce6f2").pack(anchor="w", padx=10)
# tk.Entry(left_frame, textvariable=salary_var).pack(fill="x", padx=10)

# img_label = tk.Label(left_frame, text="No image selected", bg="#dce6f2", fg="gray")
# img_label.pack(pady=5)

# def browse_image():
#     global img_path
#     path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
#     if path:
#         img_path = path
#         img_label.config(text=os.path.basename(path), fg="black")

# tk.Button(left_frame, text="Browse Image", command=browse_image, bg="#5DADE2", fg="white").pack(pady=5)

# def clear_fields():
#     global img_path
#     name_var.set("")
#     age_var.set("")
#     profession_var.set("")
# salary_var.set("")
# img_label.config(text="No image selected", fg="gray")
# img_path = None

# tk.Button(left_frame, text="Add User", bg="#28B463", fg="white", command=lambda: add_user()).pack(pady=5)
# tk.Button(left_frame, text="Clear Fields", bg="#F1C40F", command=clear_fields).pack(pady=5)

# # =====================================================
# # Right Frame (Table)
# # =====================================================
# right_frame = tk.Frame(root, bg="white", relief="groove", bd=2)
# right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

# tk.Label(right_frame, text="User Records", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

# # Search and Filter
# search_frame = tk.Frame(right_frame, bg="white")
# search_frame.pack(fill="x", padx=10, pady=5)

# tk.Label(search_frame, text="Search:", bg="white").pack(side="left")
# search_entry = tk.Entry(search_frame)
# search_entry.pack(side="left", padx=5)

# tk.Label(search_frame, text="Filter by:", bg="white").pack(side="left", padx=10)
# filter_var = tk.StringVar(value="Name")
# filter_dropdown = ttk.Combobox(search_frame, textvariable=filter_var, values=["Name", "Profession"], width=15, state="readonly")
# filter_dropdown.pack(side="left")

# # =====================================================
# # Table Canvas with Scrollbars
# # =====================================================
# canvas = tk.Canvas(right_frame, bg="white", highlightthickness=0)
# scroll_y = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
# scroll_x = ttk.Scrollbar(right_frame, orient="horizontal", command=canvas.xview)
# canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

# scroll_y.pack(side="right", fill="y")
# scroll_x.pack(side="bottom", fill="x")
# canvas.pack(fill="both", expand=True)

# table_frame = tk.Frame(canvas, bg="white")
# canvas.create_window((0, 0), window=table_frame, anchor="nw")

# def on_frame_configure(event):
#     canvas.configure(scrollregion=canvas.bbox("all"))

# table_frame.bind("<Configure>", on_frame_configure)

# # =====================================================
# # CRUD Functions
# # =====================================================
# def display_records(data=None):
#     for widget in table_frame.winfo_children():
#         widget.destroy()

#     headers = ["Image", "Name", "Age", "Profession", "Salary", "Actions"]
#     for i, col in enumerate(headers):
#         tk.Label(table_frame, text=col, font=("Arial", 10, "bold"), bg="#AED6F1", padx=10, pady=8, borderwidth=1, relief="solid").grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

#     if not data:
#         cursor.execute("SELECT * FROM users")
#         data = cursor.fetchall()

#     for i, user in enumerate(data, start=1):
#         bg_color = "#F8F9F9" if i % 2 == 0 else "#EBF5FB"
#         try:
#             img = Image.open(user[5])
#             img = img.resize((60, 60))
#             photo = ImageTk.PhotoImage(img)
#         except:
#             photo = None

#         img_lbl = tk.Label(table_frame, image=photo, bg=bg_color)
#         img_lbl.image = photo
#         img_lbl.grid(row=i, column=0, padx=10, pady=5)

#         tk.Label(table_frame, text=user[1], bg=bg_color, width=15).grid(row=i, column=1, padx=10, pady=5)
#         tk.Label(table_frame, text=user[2], bg=bg_color, width=8).grid(row=i, column=2, padx=10, pady=5)
#         tk.Label(table_frame, text=user[3], bg=bg_color, width=18).grid(row=i, column=3, padx=10, pady=5)
#         tk.Label(table_frame, text=user[4], bg=bg_color, width=10).grid(row=i, column=4, padx=10, pady=5)

#         btn_frame = tk.Frame(table_frame, bg=bg_color)
#         btn_frame.grid(row=i, column=5, pady=5)

#         update_btn = tk.Button(btn_frame, text="Update", bg="#28B463", fg="white", relief="flat",
#                                command=lambda u=user: update_user(u))
#         delete_btn = tk.Button(btn_frame, text="Delete", bg="#E74C3C", fg="white", relief="flat",
#                                command=lambda u=user: delete_user(u[0]))

#         update_btn.pack(side="left", padx=2)
#         delete_btn.pack(side="left", padx=2)

#         update_btn.bind("<Enter>", lambda e, b=update_btn: b.config(bg="#1D8348"))
#         update_btn.bind("<Leave>", lambda e, b=update_btn: b.config(bg="#28B463"))
#         delete_btn.bind("<Enter>", lambda e, b=delete_btn: b.config(bg="#B03A2E"))
#         delete_btn.bind("<Leave>", lambda e, b=delete_btn: b.config(bg="#E74C3C"))

# def add_user():
#     global img_path
#     if not (name_var.get() and age_var.get() and profession_var.get() and salary_var.get() and img_path):
#         messagebox.showerror("Error", "Please fill all fields and select an image!")
#         return

#     cursor.execute("INSERT INTO users (name, age, profession, salary, image) VALUES (?, ?, ?, ?, ?)",
#                    (name_var.get(), age_var.get(), profession_var.get(), salary_var.get(), img_path))
#     conn.commit()
#     clear_fields()
#     display_records()

# def update_user(user):
#     name_var.set(user[1])
#     age_var.set(user[2])
#     profession_var.set(user[3])
#     salary_var.set(user[4])
#     global img_path
#     img_path = user[5]

#     def save_update():
#         cursor.execute("UPDATE users SET name=?, age=?, profession=?, salary=?, image=? WHERE id=?",
#                        (name_var.get(), age_var.get(), profession_var.get(), salary_var.get(), img_path, user[0]))
#         conn.commit()
#         top.destroy()
#         display_records()
#         clear_fields()

#     top = tk.Toplevel(root)
#     top.title("Update User")
#     tk.Label(top, text="Confirm update?", font=("Arial", 12)).pack(pady=10)
#     tk.Button(top, text="Save", bg="#28B463", fg="white", command=save_update).pack(pady=5)

# def delete_user(user_id):
#     cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
#     conn.commit()
#     display_records()

# def apply_filter(*args):
#     search = search_entry.etc().lower()
#     filter_by = filter_var.get().lower()
#     cursor.execute(f"SELECT * FROM users WHERE {filter_by} LIKE ?", ('%' + search + '%',))
#     data = cursor.fetchall()
#     display_records(data)

# search_entry.bind("<KeyRelease>", apply_filter)
# filter_dropdown.bind("<<ComboboxSelected>>", apply_filter)

# display_records()

# root.mainloop()







# import tkinter as tk
# from tkinter import filedialog, messagebox
# from PIL import Image, ImageTk
# import sqlite3
# import os

# DB_PATH = "Tkinter_Task-2_database.db"


# # ---------------- DATABASE ---------------- #
# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             age INTEGER,
#             profession TEXT,
#             salary REAL,
#             image_path TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()


# # ---------------- APP ---------------- #
# class CRUDApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tkinter CRUD App")
#         self.root.geometry("1150x650")
#         self.root.config(bg="#f0f0f0")

#         # temp selections + caches
#         self.selected_image = None
#         self.image_cache = {}  # keep PhotoImage references

#         # ---------- LEFT PANEL (Form) ----------
#         left = tk.Frame(root, bg="#dbeafe", bd=2, relief="groove")
#         left.place(x=10, y=10, width=360, height=630)
#         tk.Label(left, text="User Details", font=("Arial", 18, "bold"), bg="#dbeafe").pack(pady=12)

#         self.name_var = tk.StringVar()
#         self.age_var = tk.StringVar()
#         self.prof_var = tk.StringVar()
#         self.sal_var = tk.StringVar()

#         self._create_field(left, "Name", self.name_var)
#         self._create_field(left, "Age", self.age_var)
#         self._create_field(left, "Profession", self.prof_var)
#         self._create_field(left, "Salary", self.sal_var)

#         tk.Label(left, text="Image:", bg="#dbeafe").pack(anchor="w", padx=12, pady=(6, 0))
#         self.image_label = tk.Label(left, text="No image selected", bg="#dbeafe")
#         self.image_label.pack(pady=(2, 6))
#         tk.Button(left, text="Browse Image", command=self.browse_image, bg="#2563eb", fg="white").pack()

#         tk.Button(left, text="Add User", bg="#16a34a", fg="white", width=20, command=self.add_user).pack(pady=12)
#         tk.Button(left, text="Clear Fields", bg="#facc15", width=20, command=self.clear_fields).pack()

#         # ---------- RIGHT PANEL (Records) ----------
#         right = tk.Frame(root, bg="#e0f2fe", bd=2, relief="groove")
#         right.place(x=380, y=10, width=760, height=630)
#         tk.Label(right, text="User Records", font=("Arial", 18, "bold"), bg="#e0f2fe").pack(pady=10)

#         # container for canvas+scrollbars (use grid inside)
#         right_inner = tk.Frame(right, bg="#e0f2fe")
#         right_inner.pack(fill="both", expand=True, padx=10, pady=(0, 10))

#         # Canvas + scrollbars
#         self.canvas = tk.Canvas(right_inner, bg="white", highlightthickness=0)
#         self.vsb = tk.Scrollbar(right_inner, orient="vertical", command=self.canvas.yview)
#         self.hsb = tk.Scrollbar(right_inner, orient="horizontal", command=self.canvas.xview)
#         self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

#         self.canvas.grid(row=0, column=0, sticky="nsew")
#         self.vsb.grid(row=0, column=1, sticky="ns")
#         self.hsb.grid(row=1, column=0, sticky="ew")

#         right_inner.grid_rowconfigure(0, weight=1)
#         right_inner.grid_columnconfigure(0, weight=1)

#         # Frame inside canvas which will contain the table (headers + rows)
#         self.table_frame = tk.Frame(self.canvas, bg="white")
#         self.canvas_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

#         # keep scrollregion updated
#         self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

#         # mousewheel support (enter/leave to bind/unbind so it scrolls only when over canvas)
#         self.canvas.bind("<Enter>", lambda e: (self.canvas.bind_all("<MouseWheel>", self._on_mousewheel),
#                                                self.canvas.bind_all("<Button-4>", self._on_mousewheel),
#                                                self.canvas.bind_all("<Button-5>", self._on_mousewheel),
#                                                self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)))
#         self.canvas.bind("<Leave>", lambda e: (self.canvas.unbind_all("<MouseWheel>"),
#                                                self.canvas.unbind_all("<Button-4>"),
#                                                self.canvas.unbind_all("<Button-5>"),
#                                                self.canvas.unbind_all("<Shift-MouseWheel>")))

#         # load rows from database
#         self.load_data()

#     # ---------------- helpers ---------------- #
#     def _create_field(self, parent, label_text, var):
#         tk.Label(parent, text=f"{label_text}:", bg="#dbeafe").pack(anchor="w", padx=12, pady=(6, 2))
#         tk.Entry(parent, textvariable=var, width=36).pack(padx=12, pady=(0, 4))

#     def browse_image(self):
#         path = filedialog.askopenfilename(title="Select Image",
#                                           filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
#         if path:
#             self.selected_image = path
#             self.image_label.config(text=os.path.basename(path))

#     def clear_fields(self):
#         self.name_var.set("")
#         self.age_var.set("")
#         self.prof_var.set("")
#         self.sal_var.set("")
#         self.selected_image = None
#         self.image_label.config(text="No image selected")

#     def add_user(self):
#         name = self.name_var.get().strip()
#         age = self.age_var.get().strip()
#         prof = self.prof_var.get().strip()
#         sal = self.sal_var.get().strip()
#         img = self.selected_image

#         if not (name and age and prof and sal and img):
#             messagebox.showwarning("Input Error", "All fields including image are required.")
#             return

#         try:
#             conn = sqlite3.connect(DB_PATH)
#             c = conn.cursor()
#             c.execute("INSERT INTO users (name, age, profession, salary, image_path) VALUES (?, ?, ?, ?, ?)",
#                       (name, age, prof, sal, img))
#             conn.commit()
#             conn.close()
#             messagebox.showinfo("Success", "User added successfully!")
#             self.clear_fields()
#             self.load_data()
#         except Exception as ex:
#             messagebox.showerror("Database Error", str(ex))

#     # ---------------- scrolling helpers ---------------- #
#     def _on_mousewheel(self, event):
#         # vertical scroll
#         if hasattr(event, "delta") and event.delta:
#             # Windows / macOS
#             self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
#         else:
#             # Linux (Button-4 / Button-5)
#             if event.num == 4:
#                 self.canvas.yview_scroll(-3, "units")
#             elif event.num == 5:
#                 self.canvas.yview_scroll(3, "units")

#     def _on_shift_mousewheel(self, event):
#         # horizontal scroll when shift is held
#         if hasattr(event, "delta") and event.delta:
#             self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

#     # ---------------- load & render ---------------- #
#     def load_data(self):
#         # clear existing widgets
#         for w in self.table_frame.winfo_children():
#             w.destroy()
#         self.image_cache.clear()

#         # fetch rows
#         conn = sqlite3.connect(DB_PATH)
#         c = conn.cursor()
#         c.execute("SELECT * FROM users")
#         rows = c.fetchall()
#         conn.close()

#         # Header row
#         headers = ["Image", "Name", "Age", "Profession", "Salary", "Actions"]
#         header_bg = "#93c5fd"
#         for col, text in enumerate(headers):
#             lbl = tk.Label(self.table_frame, text=text, bg=header_bg, font=("Arial", 11, "bold"),
#                            bd=1, relief="ridge", padx=6, pady=6)
#             lbl.grid(row=0, column=col, sticky="nsew", padx=0, pady=0)

#         # Set reasonable column min sizes (this helps horizontal scrollbar appear when needed)
#         self.table_frame.grid_columnconfigure(0, minsize=90)   # image
#         self.table_frame.grid_columnconfigure(1, minsize=200)  # name
#         self.table_frame.grid_columnconfigure(2, minsize=80)   # age
#         self.table_frame.grid_columnconfigure(3, minsize=260)  # profession
#         self.table_frame.grid_columnconfigure(4, minsize=120)  # salary
#         self.table_frame.grid_columnconfigure(5, minsize=160)  # actions

#         # Rows
#         for r, row in enumerate(rows, start=1):
#             uid, name, age, profession, salary, image_path = row
#             row_bg = "#ffffff" if r % 2 == 0 else "#f3f4f6"  # zebra coloring

#             # Thumbnail (slightly larger)
#             if image_path and os.path.exists(image_path):
#                 try:
#                     im = Image.open(image_path)
#                     im.thumbnail((72, 72))  # increased size
#                     photo = ImageTk.PhotoImage(im)
#                     self.image_cache[uid] = photo
#                     lbl_img = tk.Label(self.table_frame, image=photo, bg=row_bg)
#                 except Exception:
#                     lbl_img = tk.Label(self.table_frame, text="No Img", bg=row_bg, width=12, height=4)
#             else:
#                 lbl_img = tk.Label(self.table_frame, text="No Img", bg=row_bg, width=12, height=4)

#             lbl_img.grid(row=r, column=0, padx=6, pady=6, sticky="nsew")

#             # Data columns
#             tk.Label(self.table_frame, text=name, bg=row_bg, anchor="w", padx=8).grid(row=r, column=1, sticky="nsew")
#             tk.Label(self.table_frame, text=age, bg=row_bg, anchor="center").grid(row=r, column=2, sticky="nsew")
#             tk.Label(self.table_frame, text=profession, bg=row_bg, anchor="w", padx=8).grid(row=r, column=3, sticky="nsew")
#             tk.Label(self.table_frame, text=str(salary), bg=row_bg, anchor="e", padx=8).grid(row=r, column=4, sticky="nsew")

#             # Actions (Update / Delete)
#             btn_frame = tk.Frame(self.table_frame, bg=row_bg)
#             upd_btn = tk.Button(btn_frame, text="Update", bg="#16a34a", fg="white",
#                                 relief="raised", padx=8, pady=4,
#                                 command=lambda _id=uid: self.open_update_window(_id))
#             del_btn = tk.Button(btn_frame, text="Delete", bg="#dc2626", fg="white",
#                                 relief="raised", padx=8, pady=4,
#                                 command=lambda _id=uid: self.delete_user(_id))

#             # Hover effects
#             upd_btn.bind("<Enter>", lambda e, b=upd_btn: b.config(bg="#1f7a2e"))
#             upd_btn.bind("<Leave>", lambda e, b=upd_btn: b.config(bg="#16a34a"))
#             del_btn.bind("<Enter>", lambda e, b=del_btn: b.config(bg="#ff5b5b"))
#             del_btn.bind("<Leave>", lambda e, b=del_btn: b.config(bg="#dc2626"))

#             upd_btn.pack(side="left", padx=(0, 6))
#             del_btn.pack(side="left")
#             btn_frame.grid(row=r, column=5, padx=6, pady=6, sticky="nsew")

#         # ensure scrollregion is updated (in case)
#         self.table_frame.update_idletasks()
#         self.canvas.configure(scrollregion=self.canvas.bbox("all"))

#     # ---------------- update flow ---------------- #
#     def open_update_window(self, uid):
#         conn = sqlite3.connect(DB_PATH)
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE id=?", (uid,))
#         data = c.fetchone()
#         conn.close()
#         if not data:
#             messagebox.showerror("Error", "User not found.")
#             return

#         _, name, age, profession, salary, img_path = data

#         win = tk.Toplevel(self.root)
#         win.title("Update User")
#         win.geometry("420x320")
#         win.transient(self.root)

#         # local vars for update window
#         name_v = tk.StringVar(value=name)
#         age_v = tk.StringVar(value=str(age))
#         prof_v = tk.StringVar(value=profession)
#         sal_v = tk.StringVar(value=str(salary))
#         new_image = img_path  # will be modified by change_image()

#         tk.Label(win, text="Name:").pack(anchor="w", padx=12, pady=(12, 0))
#         tk.Entry(win, textvariable=name_v, width=48).pack(padx=12)

#         tk.Label(win, text="Age:").pack(anchor="w", padx=12, pady=(8, 0))
#         tk.Entry(win, textvariable=age_v, width=48).pack(padx=12)

#         tk.Label(win, text="Profession:").pack(anchor="w", padx=12, pady=(8, 0))
#         tk.Entry(win, textvariable=prof_v, width=48).pack(padx=12)

#         tk.Label(win, text="Salary:").pack(anchor="w", padx=12, pady=(8, 0))
#         tk.Entry(win, textvariable=sal_v, width=48).pack(padx=12)

#         img_lbl = tk.Label(win, text=os.path.basename(img_path) if img_path else "No image", fg="blue")
#         img_lbl.pack(pady=(10, 6))

#         def change_image():
#             nonlocal new_image
#             p = filedialog.askopenfilename(title="Select new image",
#                                            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
#             if p:
#                 new_image = p
#                 img_lbl.config(text=os.path.basename(p))

#         tk.Button(win, text="Change Image", command=change_image, bg="#2563eb", fg="white").pack(pady=(0, 6))

#         def save_update():
#             try:
#                 conn = sqlite3.connect(DB_PATH)
#                 c = conn.cursor()
#                 c.execute("""
#                     UPDATE users SET name=?, age=?, profession=?, salary=?, image_path=? WHERE id=?
#                 """, (name_v.get().strip(), age_v.get().strip(), prof_v.get().strip(), sal_v.get().strip(), new_image, uid))
#                 conn.commit()
#                 conn.close()
#                 messagebox.showinfo("Success", "User updated.")
#                 win.destroy()
#                 self.load_data()
#             except Exception as ex:
#                 messagebox.showerror("Error", str(ex))

#         tk.Button(win, text="Save Update", command=save_update, bg="#16a34a", fg="white").pack(pady=10)

#     # ---------------- delete ---------------- #
#     def delete_user(self, uid):
#         if not messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
#             return
#         try:
#             conn = sqlite3.connect(DB_PATH)
#             c = conn.cursor()
#             c.execute("DELETE FROM users WHERE id=?", (uid,))
#             conn.commit()
#             conn.close()
#             self.load_data()
#         except Exception as ex:
#             messagebox.showerror("Error", str(ex))


# # ---------------- run ---------------- #
# if __name__ == "__main__":
#     init_db()
#     root = tk.Tk()
#     app = CRUDApp(root)
#     root.mainloop()





