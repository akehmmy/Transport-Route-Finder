from PIL import Image
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import random
from route_logic_backup import RouteGenerator
from map_renderer import MapRenderer
from multiprocessing import Process
import os
import subprocess

# -------------------- APP SETTINGS --------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# -------------------- COLOUR TOKENS --------------------

BG_DARK      = "#0d1117"   # window / outer background
BG_PANEL     = "#161b22"   # left / right panel cards
BG_INPUT     = "#1c2128"   # entry / textbox fill
BG_TILE      = "#1c2128"   # metric tiles
BORDER       = "#30363d"   # subtle borders
ACCENT_BLUE  = "#3b82f6"   # primary buttons / highlights
ACCENT_HOVER = "#2563eb"
TEXT_PRIMARY = "#e6edf3"
TEXT_MUTED   = "#8b949e"
BTN_DARK     = "#21262d"   # "View All Reviews" dark button
BTN_DARK_H   = "#30363d"


class TransportRouteApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent Transport Route Planner")
        self.root.geometry("1280x800")
        self.root.minsize(1100, 720)
        self.root.configure(fg_color=BG_DARK)

       
	self.api_key = 'YOUR_OPENROUTESERVICE_API_KEY'

        self.route_generator = RouteGenerator(self.api_key)
        self.map_renderer    = MapRenderer()

        self._build_ui()

    # ================================================================
    # UI CONSTRUCTION
    # ================================================================

    def _build_ui(self):
        # ---- ROOT GRID ----
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_body()

    # ----------------------------------------------------------------
    # HEADER
    # ----------------------------------------------------------------

    def _build_header(self):
        header = ctk.CTkFrame(
            self.root,
            fg_color="#0d1f3c",      # deep navy — differentiates from body
            corner_radius=0,
            height=120,
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        # Map illustration placeholder (circle + icon)
        icon_frame = ctk.CTkFrame(
            header,
            width=72, height=72,
            fg_color="#122145",
            corner_radius=36,
        )
        icon_frame.place(x=40, rely=0.5, anchor="w")
        icon_frame.grid_propagate(False)

        icon_lbl = ctk.CTkLabel(
            icon_frame,
            text="🗺️",
            font=("Segoe UI Emoji", 30),
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Text block
        text_frame = ctk.CTkFrame(header, fg_color="transparent")
        text_frame.place(x=128, rely=0.5, anchor="w")

        ctk.CTkLabel(
            text_frame,
            text="Intelligent Transport Route Planner",
            font=("Segoe UI", 26, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_frame,
            text="Generate routes, estimate travel time and simulate traffic conditions",
            font=("Segoe UI", 12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

    # ----------------------------------------------------------------
    # BODY
    # ----------------------------------------------------------------

    def _build_body(self):
        body = ctk.CTkFrame(self.root, fg_color=BG_DARK, corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew", padx=18, pady=18)
        body.grid_columnconfigure(0, weight=0)   # left panel fixed
        body.grid_columnconfigure(1, weight=1)   # right panel grows
        body.grid_rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_right_panel(body)

    # ----------------------------------------------------------------
    # LEFT PANEL
    # ----------------------------------------------------------------

    def _build_left_panel(self, parent):
        # Outer container keeps the fixed width and border styling
        outer = ctk.CTkFrame(
            parent,
            width=340,
            fg_color=BG_PANEL,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        outer.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        outer.grid_propagate(False)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # Scrollable inner frame — ensures buttons are never clipped
        scroll = ctk.CTkScrollableFrame(
            outer,
            fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT_BLUE,
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        panel = scroll   # alias — rest of the method uses `panel`

        # ---- ROUTE INPUT SECTION ----
        self._section_label(panel, "Route Input").pack(
            anchor="w", padx=22, pady=(22, 16)
        )

        # Start Location
        self._field_label(panel, "Start Location").pack(anchor="w", padx=22)
        self.start_entry = self._entry(panel, "e.g. Abuja", icon="📍")
        self.start_entry.pack(padx=22, pady=(4, 12), fill="x")

        # Destination
        self._field_label(panel, "Destination").pack(anchor="w", padx=22)
        self.end_entry = self._entry(panel, "e.g. Lagos", icon="📍")
        self.end_entry.pack(padx=22, pady=(4, 12), fill="x")

        # Transport Mode
        self._field_label(panel, "Transport Mode").pack(anchor="w", padx=22)
        self.transport_mode = ctk.CTkComboBox(
            panel,
            values=["Car", "Walk", "Bike", "Train"],
            height=40,
            fg_color=BG_INPUT,
            border_color=BORDER,
            button_color=BORDER,
            button_hover_color=ACCENT_BLUE,
            dropdown_fg_color=BG_PANEL,
            font=("Segoe UI", 13),
            text_color=TEXT_PRIMARY,
        )
        self.transport_mode.set("Car")
        self.transport_mode.pack(padx=22, pady=(4, 18), fill="x")

        # Generate Route button
        self.generate_btn = ctk.CTkButton(
            panel,
            text="  ⇄  Generate Route",
            height=44,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_HOVER,
            font=("Segoe UI", 14, "bold"),
            corner_radius=10,
            command=self.generate_route,
        )
        self.generate_btn.pack(padx=22, pady=(0, 22), fill="x")

        # Divider
        self._divider(panel).pack(fill="x", padx=22, pady=(0, 18))

        # ---- USER REVIEWS SECTION ----
        self._section_label(panel, "User Reviews").pack(anchor="w", padx=22, pady=(0, 12))

        self.review_entry = ctk.CTkTextbox(
            panel,
            height=110,
            corner_radius=10,
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            font=("Segoe UI", 13),
            text_color=TEXT_PRIMARY,
        )
        self.review_entry.insert("1.0", "")
        self.review_entry.pack(padx=22, pady=(0, 12), fill="x")

        # Placeholder simulation
        self._add_placeholder(self.review_entry, "Write your review here...")

        ctk.CTkButton(
            panel,
            text="  ➤  Submit Review",
            height=42,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_HOVER,
            font=("Segoe UI", 13, "bold"),
            corner_radius=10,
            command=self.submit_review,
        ).pack(padx=22, pady=(0, 10), fill="x")

        ctk.CTkButton(
            panel,
            text="  👁  View All Reviews",
            height=42,
            fg_color=BTN_DARK,
            hover_color=BTN_DARK_H,
            font=("Segoe UI", 13, "bold"),
            corner_radius=10,
            command=self.view_reviews,
        ).pack(padx=22, pady=(0, 22), fill="x")

    # ----------------------------------------------------------------
    # RIGHT PANEL
    # ----------------------------------------------------------------

    def _build_right_panel(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color=BG_PANEL,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # ---- ROUTE SUMMARY ----
        self._section_label(panel, "Route Summary").grid(
            row=0, column=0, sticky="w", padx=26, pady=(22, 14)
        )

        # Metric tiles row
        tiles_frame = ctk.CTkFrame(panel, fg_color="transparent")
        tiles_frame.grid(row=1, column=0, sticky="ew", padx=26, pady=(0, 22))
        for i in range(4):
            tiles_frame.grid_columnconfigure(i, weight=1, uniform="tile")

        tile_defs = [
            ("📍", "Distance",        "-- km"),
            ("🕐", "Estimated Time",  "-- minutes"),
            ("🚦", "Traffic Condition", "--"),
            ("⏱", "Adjusted Time",   "-- minutes"),
        ]

        self._tile_vars = {}
        for col, (icon, label, default) in enumerate(tile_defs):
            tile = ctk.CTkFrame(
                tiles_frame,
                fg_color=BG_TILE,
                corner_radius=10,
                border_width=1,
                border_color=BORDER,
            )
            tile.grid(row=0, column=col, sticky="ew", padx=(0, 10) if col < 3 else 0, ipady=10)

            ctk.CTkLabel(
                tile,
                text=icon,
                font=("Segoe UI Emoji", 20),
            ).pack(pady=(10, 2))

            ctk.CTkLabel(
                tile,
                text=label,
                font=("Segoe UI", 11),
                text_color=TEXT_MUTED,
            ).pack()

            var = tk.StringVar(value=default)
            self._tile_vars[label] = var

            ctk.CTkLabel(
                tile,
                textvariable=var,
                font=("Segoe UI", 13, "bold"),
                text_color=ACCENT_BLUE,
            ).pack(pady=(2, 10))

        # ---- TURN-BY-TURN DIRECTIONS ----
        self._section_label(panel, "Turn-by-Turn Directions").grid(
            row=3, column=0, sticky="w", padx=26, pady=(0, 10)
        )

        self.directions_text_widget = ctk.CTkTextbox(
            panel,
            corner_radius=10,
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            font=("Segoe UI", 13),
            text_color=TEXT_PRIMARY,
            scrollbar_button_color=BORDER,
        )
        self.directions_text_widget.grid(
            row=4, column=0, sticky="nsew", padx=26, pady=(0, 26)
        )
        panel.grid_rowconfigure(4, weight=1)
        self.directions_text_widget.configure(state="disabled")

    # ================================================================
    # HELPER WIDGETS
    # ================================================================

    def _section_label(self, parent, text):
        """Bold blue-accented section heading with underline bar."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(
            frame,
            text=text,
            font=("Segoe UI", 18, "bold"),
            text_color=ACCENT_BLUE,
        ).pack(anchor="w")
        ctk.CTkFrame(frame, height=2, fg_color=ACCENT_BLUE, corner_radius=1).pack(
            fill="x", pady=(3, 0)
        )
        return frame

    def _field_label(self, parent, text):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=("Segoe UI", 13),
            text_color=TEXT_MUTED,
        )

    def _entry(self, parent, placeholder, icon=""):
        """CTkEntry styled to match the screenshot (dark fill, pin icon)."""
        frame = ctk.CTkFrame(parent, fg_color=BG_INPUT, corner_radius=8,
                             border_width=1, border_color=BORDER)

        inner = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder,
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 13),
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
        )
        inner.pack(side="left", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(frame, text=icon, font=("Segoe UI Emoji", 14),
                     text_color=TEXT_MUTED).pack(side="right", padx=10)

        # expose .get() and .delete() / .insert() pass-through
        frame.get    = inner.get
        frame.delete = inner.delete
        frame.insert = inner.insert
        return frame

    def _divider(self, parent):
        return ctk.CTkFrame(parent, height=1, fg_color=BORDER, corner_radius=0)

    def _add_placeholder(self, textbox, text):
        """Simple placeholder for CTkTextbox."""
        textbox.insert("1.0", text)
        textbox.configure(text_color=TEXT_MUTED)

        def on_focus_in(e):
            if textbox.get("1.0", "end-1c") == text:
                textbox.delete("1.0", "end")
                textbox.configure(text_color=TEXT_PRIMARY)

        def on_focus_out(e):
            if not textbox.get("1.0", "end-1c").strip():
                textbox.insert("1.0", text)
                textbox.configure(text_color=TEXT_MUTED)

        textbox.bind("<FocusIn>",  on_focus_in)
        textbox.bind("<FocusOut>", on_focus_out)

    # ================================================================
    # ROUTE GENERATION
    # ================================================================

    def generate_route(self):
        start_place = self.start_entry.get()
        end_place   = self.end_entry.get()
        mode        = self.transport_mode.get().lower()

        if not start_place or not end_place:
            messagebox.showwarning("Input Error", "Please enter both start and destination.")
            return

        self._set_tiles("--", "--", "Calculating…", "--")
        self.root.update()

        start_coords = self.route_generator.geocode(start_place)
        end_coords   = self.route_generator.geocode(end_place)

        if not start_coords or not end_coords:
            self._set_tiles("N/A", "N/A", "Location error", "N/A")
            return

        mode_profile = {
            'car':   'driving-car',
            'walk':  'foot-walking',
            'bike':  'cycling-regular',
        }.get(mode, 'driving-car')

        distance, duration, route_coords, steps = self.route_generator.get_route_info(
            start_coords, end_coords, mode_profile
        )

        if distance is None or duration is None:
            self._set_tiles("N/A", "N/A", "Route error", "N/A")
            return

        # Traffic simulation
        traffic_conditions = {"Free Flow": 0.9, "Moderate": 1.2, "Heavy": 1.5}
        traffic_status     = random.choice(list(traffic_conditions.keys()))
        traffic_multiplier = traffic_conditions[traffic_status]
        adjusted_time      = round(duration * traffic_multiplier, 2)

        self._set_tiles(
            f"{distance} km",
            f"{duration} min",
            traffic_status,
            f"{adjusted_time} min",
        )

        # Directions
        directions_output = "\n".join(
            f"{i}. {step['instruction']}  ({round(step['distance'], 1)} m)"
            for i, step in enumerate(steps, 1)
        )

        self.directions_text_widget.configure(state="normal")
        self.directions_text_widget.delete("1.0", "end")
        self.directions_text_widget.insert("end", directions_output)
        self.directions_text_widget.configure(state="disabled")

        # Map
        map_obj = self.map_renderer.show_route_map(route_coords, start_place, end_place)
        if map_obj:
            self.map_renderer.save_html(map_obj)
            Process(target=self.map_renderer.launch_map_view).start()

    def _set_tiles(self, distance, est_time, traffic, adj_time):
        self._tile_vars["Distance"].set(distance)
        self._tile_vars["Estimated Time"].set(est_time)
        self._tile_vars["Traffic Condition"].set(traffic)
        self._tile_vars["Adjusted Time"].set(adj_time)

    # ================================================================
    # REVIEWS
    # ================================================================

    def submit_review(self):
        text = self.review_entry.get("1.0", "end").strip()
        placeholder = "Write your review here..."
        if not text or text == placeholder:
            messagebox.showwarning("Empty Review", "Please write something before submitting.")
            return
        try:
            with open("reviews.txt", "a", encoding="utf-8") as f:
                f.write(f"{text}\n\n")
            self.review_entry.delete("1.0", "end")
            self._add_placeholder(self.review_entry, placeholder)
            messagebox.showinfo("Thank you!", "Review submitted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save review:\n{e}")

    def view_reviews(self):
        filepath = "reviews.txt"
        if os.path.exists(filepath):
            try:
                os.startfile(filepath)
            except AttributeError:
                try:
                    subprocess.call(["open", filepath])
                except Exception:
                    subprocess.call(["xdg-open", filepath])
        else:
            messagebox.showinfo("No Reviews", "No reviews have been submitted yet.")


# -------------------- ENTRY POINT --------------------

if __name__ == "__main__":
    root = ctk.CTk()
    app  = TransportRouteApp(root)
    root.mainloop()
