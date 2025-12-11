import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os

class VisionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vision Pipeline Inspector")
        self.root.geometry("1500x850") # Further widen window for sidebar
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Pipeline Configuration (Default)
        self.pipeline_config = [
            {"type": "blur", "params": {"type": "gaussian", "ksize": 9}},
            {"type": "threshold", "params": {"threshold": 127}},
            {"type": "edge", "params": {"method": "canny", "threshold1": 50, "threshold2": 150, "ksize": 3}},
            {"type": "hough_circle", "params": {
                "dp": 1, "minDist": 50, "param1": 100, "param2": 30, "minRadius": 10, "maxRadius": 100
            }},
            {"type": "contour", "params": {"thresholdValue": 136, "retrievalMode": "TREE", "minArea": 550, 
                                           "showBoundingBox": False, "showCentroid": True, "showLabel": True}}
        ]

        self.current_image_path = None
        self.pixel_ratio = None # mm per pixel

        self._setup_ui()

    def _setup_ui(self):
        # --- Top Control Panel ---
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_load = ttk.Button(control_frame, text="📂 Load Image", command=self.load_image)
        self.btn_load.pack(side=tk.LEFT, padx=5)

        self.btn_run = ttk.Button(control_frame, text="⚙️ Run Pipeline", command=self.run_pipeline, state=tk.DISABLED)
        self.btn_run.pack(side=tk.LEFT, padx=5)
        
        # --- Main Layout (PanedWindow) ---
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Image Tabs
        self.notebook = ttk.Notebook(self.paned_window)
        self.paned_window.add(self.notebook, weight=3)
        
        # Right: Data Sidebar
        self.sidebar_frame = ttk.Frame(self.paned_window, padding="5", relief=tk.RIDGE)
        self.paned_window.add(self.sidebar_frame, weight=1)

        # --- Treeview Section ---
        ttk.Label(self.sidebar_frame, text="Contour Data", font=("Helvetica", 12, "bold")).pack(side=tk.TOP, pady=5)
        
        columns = ("ID", "Type", "Area", "Px Dia/Peri", "Circ", "Real(mm)")
        self.tree = ttk.Treeview(self.sidebar_frame, columns=columns, show="headings", selectmode="browse")
        
        # Define headings and column widths
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=40, anchor=tk.CENTER)
        
        self.tree.heading("Type", text="Type")
        self.tree.column("Type", width=70, anchor=tk.CENTER) # Increased width
        
        self.tree.heading("Area", text="Area")
        self.tree.column("Area", width=60, anchor=tk.E) # Increased width

        self.tree.heading("Px Dia/Peri", text="Px Dia/Peri")
        self.tree.column("Px Dia/Peri", width=80, anchor=tk.E) # Increased width
        
        self.tree.heading("Circ", text="Circ")
        self.tree.column("Circ", width=60, anchor=tk.E) # Increased width

        self.tree.heading("Real(mm)", text="Real(mm)")
        self.tree.column("Real(mm)", width=80, anchor=tk.E) # Increased width
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.sidebar_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, in_=self.tree) # Pack inside tree frame effectively

        # --- Calibration Section ---
        calib_frame = ttk.LabelFrame(self.sidebar_frame, text="Calibration", padding="10")
        calib_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        ttk.Label(calib_frame, text="Select a contour above and enter its real size:").pack(fill=tk.X)
        
        input_frame = ttk.Frame(calib_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="True Size (mm):").pack(side=tk.LEFT)
        self.entry_real_size = ttk.Entry(input_frame, width=10)
        self.entry_real_size.pack(side=tk.LEFT, padx=5)

        ttk.Button(calib_frame, text="Calibrate & Update", command=self.calibrate_and_update).pack(fill=tk.X, pady=5)
        
        self.lbl_ratio = ttk.Label(calib_frame, text="Current Ratio: Not Calibrated", foreground="blue")
        self.lbl_ratio.pack(fill=tk.X)


        # Create an initial empty tab
        self.start_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.start_frame, text="Welcome")
        lbl_instruction = ttk.Label(self.start_frame, text="Please load an image to start.", font=("Helvetica", 14))
        lbl_instruction.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.bmp *.jpg *.jpeg *.png *.tif")]
        )
        if file_path:
            self.current_image_path = file_path
            self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
            self.btn_run.config(state=tk.NORMAL)
            self.pixel_ratio = None # Reset calibration
            self.lbl_ratio.config(text="Current Ratio: Not Calibrated")
            
            # Show original image immediately
            img = cv2.imread(file_path)
            if img is not None:
                self.reset_tabs()
                self.add_tab("Original", img)
                self.status_var.set(f"Loaded: {os.path.basename(file_path)} - Ready to process")
            else:
                messagebox.showerror("Error", "Failed to load image.")

    def reset_tabs(self):
        # Remove all existing tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_tab(self, title, cv_image):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        
        if len(cv_image.shape) == 2:
            img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
        pil_img = Image.fromarray(img_rgb)
        
        display_w = self.notebook.winfo_width() # Use notebook width
        display_h = self.notebook.winfo_height()
        
        # Ensure we have reasonable fallback dimensions if winfo_width/height are not yet available
        if display_w < 100: display_w = 800 
        if display_h < 100: display_h = 600
        
        w_percent = (display_w / float(pil_img.size[0]))
        h_percent = (display_h / float(pil_img.size[1]))
        resize_scale = min(w_percent, h_percent, 1.0) # Don't upscale
        
        new_w = int((float(pil_img.size[0]) * float(resize_scale)))
        new_h = int((float(pil_img.size[1]) * float(resize_scale)))
        
        pil_img_resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(pil_img_resized)
        
        lbl = ttk.Label(frame, image=tk_img)
        lbl.image = tk_img 
        lbl.pack(expand=True)
        
        self.notebook.select(frame)

    def calibrate_and_update(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a contour from the list first.")
            return
        
        try:
            real_size_mm = float(self.entry_real_size.get())
            if real_size_mm <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid positive number for True Size (mm).")
            return

        item_values = self.tree.item(selected_item, "values")
        pixel_val_str = item_values[3] # Column 3 is 'Px Dia/Peri'
        
        if pixel_val_str == "-" or pixel_val_str == "":
             messagebox.showerror("Error", "Selected item has no valid pixel dimension to calibrate against. "
                                   "Please select a contour/circle with a 'Px Dia/Peri' value.")
             return
             
        try:
            pixel_val = float(pixel_val_str)
        except ValueError:
             messagebox.showerror("Error", "Selected item's pixel dimension is not a number. "
                                   "Please select a contour/circle with a valid 'Px Dia/Peri' value.")
             return

        # Calculate Ratio: mm / pixel
        self.pixel_ratio = real_size_mm / pixel_val
        self.lbl_ratio.config(text=f"Current Ratio: {self.pixel_ratio:.5f} mm/px")
        
        # Update all rows
        for item_id in self.tree.get_children():
            row_vals = list(self.tree.item(item_id, "values"))
            px_val_to_convert_str = row_vals[3] # 'Px Dia/Peri' column
            
            if px_val_to_convert_str != "-" and px_val_to_convert_str != "":
                try:
                    px_val_to_convert = float(px_val_to_convert_str)
                    real_val = px_val_to_convert * self.pixel_ratio
                    row_vals[5] = f"{real_val:.2f}" # Update Real(mm) column
                except ValueError:
                    row_vals[5] = "-" # Cannot convert, set to default
            else:
                row_vals[5] = "-" # No pixel value, set to default
            
            self.tree.item(item_id, values=row_vals)
            
        self.status_var.set("Calibration applied. Real sizes updated.")


    def run_pipeline(self):
        if not self.current_image_path:
            return
            
        self.status_var.set("Processing...")
        self.root.update_idletasks() 
        
        # Clear previous data in tree for new run
        for item in self.tree.get_children():
            self.tree.delete(item)

        original_img = cv2.imread(self.current_image_path)
        if original_img is None:
            return

        gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        current_img = gray_img
        display_img = original_img.copy() 
        
        step_idx = 1
        
        try:
            for step in self.pipeline_config:
                step_type = step.get("type")
                params = step.get("params", {})
                
                step_title = f"{step_idx}. {step_type.capitalize()}"

                if step_type == "blur":
                    blur_type = params.get("type", "gaussian")
                    ksize = params.get("ksize", 9)
                    if blur_type == "gaussian":
                        if ksize % 2 == 0: ksize += 1
                        current_img = cv2.GaussianBlur(current_img, (ksize, ksize), 0)
                    self.add_tab(step_title, current_img)

                elif step_type == "threshold":
                    thresh_val = params.get("threshold", 127)
                    _, current_img = cv2.threshold(current_img, thresh_val, 255, cv2.THRESH_BINARY)
                    self.add_tab(step_title, current_img)

                elif step_type == "edge":
                    method = params.get("method", "canny")
                    if method == "canny":
                        t1 = params.get("threshold1", 50)
                        t2 = params.get("threshold2", 150)
                        aperture = params.get("ksize", 3)
                        current_img = cv2.Canny(current_img, t1, t2, apertureSize=aperture)
                    self.add_tab(step_title, current_img)

                elif step_type == "hough_circle":
                    hough_input = cv2.GaussianBlur(gray_img, (9, 9), 2)
                    dp = params.get("dp", 1)
                    minDist = params.get("minDist", 20)
                    param1 = params.get("param1", 50)
                    param2 = params.get("param2", 30)
                    minRadius = params.get("minRadius", 0)
                    maxRadius = params.get("maxRadius", 0)

                    circles = cv2.HoughCircles(hough_input, cv2.HOUGH_GRADIENT, dp, minDist,
                                               param1=param1, param2=param2,
                                               minRadius=minRadius, maxRadius=maxRadius)

                    hough_display = original_img.copy()

                    if circles is not None:
                        circles = np.uint16(np.around(circles))
                        for i, c in enumerate(circles[0, :]):
                            center = (c[0], c[1])
                            radius = c[2]
                            cv2.circle(hough_display, center, 1, (0, 100, 100), 3)
                            cv2.circle(hough_display, center, radius, (255, 0, 255), 3)
                            
                            diameter = radius * 2
                            label_text = f"ID:H{i} D:{int(diameter)}"
                            cv2.putText(hough_display, label_text, (c[0]-20, c[1]-10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                            
                            # Real size calculation if ratio exists
                            real_val_str = "-"
                            if self.pixel_ratio:
                                real_val_str = f"{diameter * self.pixel_ratio:.2f}"

                            self.tree.insert("", "end", values=(f"H{i}", "Hough", "-", f"{int(diameter)}", "-", real_val_str))
                                        
                        self.status_var.set(f"Hough Circle: Found {len(circles[0])} circles.")
                    else:
                        self.status_var.set("Hough Circle: No circles found.")

                    self.add_tab(step_title, hough_display)


                elif step_type == "contour":
                    thresh_val = params.get("thresholdValue", 127)
                    mode_str = params.get("retrievalMode", "TREE")
                    min_area = params.get("minArea", 0)
                    show_bbox = params.get("showBoundingBox", False)
                    show_centroid = params.get("showCentroid", True)
                    show_label = params.get("showLabel", True)

                    mode = cv2.RETR_TREE
                    if mode_str == "EXTERNAL": mode = cv2.RETR_EXTERNAL
                    elif mode_str == "LIST": mode = cv2.RETR_LIST

                    if len(current_img.shape) == 3 or np.max(current_img) > 1:
                         _, binary_img = cv2.threshold(current_img, 127, 255, cv2.THRESH_BINARY)
                    else:
                        binary_img = current_img

                    contours, _ = cv2.findContours(binary_img, mode, cv2.CHAIN_APPROX_SIMPLE)
                    
                    count = 0
                    for i, cnt in enumerate(contours):
                        area = cv2.contourArea(cnt)
                        if area < min_area:
                            continue
                        count += 1
                        
                        perimeter = cv2.arcLength(cnt, True)
                        if perimeter == 0: continue
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        
                        is_circle = circularity > 0.8
                        
                        shape_type = "Circle" if is_circle else "Contour"
                        dia_peri_val = ""
                        pixel_val_for_calib = 0
                        
                        if is_circle:
                            ((cx_f, cy_f), radius) = cv2.minEnclosingCircle(cnt)
                            diameter = radius * 2
                            pixel_val_for_calib = diameter
                            dia_peri_val = f"{int(diameter)}"
                            
                            label_text = f"ID:{i} D:{int(diameter)}"
                            text_color = (0, 0, 0)
                            font_scale = 0.8
                            thickness = 2
                        else:
                            pixel_val_for_calib = perimeter
                            dia_peri_val = f"{int(perimeter)}"
                            label_text = f"ID:{i} A:{int(area)}"
                            text_color = (0, 255, 255)
                            font_scale = 0.5
                            thickness = 1
                        
                        # Calculate real value if ratio exists
                        real_val_str = "-"
                        if self.pixel_ratio:
                            real_val_str = f"{pixel_val_for_calib * self.pixel_ratio:.2f}"

                        self.tree.insert("", "end", values=(i, shape_type, int(area), dia_peri_val, f"{circularity:.3f}", real_val_str))

                        cv2.drawContours(display_img, [cnt], -1, (0, 255, 0), 2)
                        
                        if show_bbox:
                            x, y, w, h = cv2.boundingRect(cnt)
                            cv2.rectangle(display_img, (x, y), (x+w, y+h), (255, 0, 0), 2)

                        M = cv2.moments(cnt)
                        cx, cy = 0, 0
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                        
                        if show_centroid and M['m00'] != 0:
                            cv2.circle(display_img, (cx, cy), 5, (0, 0, 255), -1)

                        if show_label:
                            text_pos = (cx - 20, cy - 10) if M['m00'] != 0 else (cnt[0][0][0], cnt[0][0][1])
                            cv2.putText(display_img, label_text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
                    
                    self.add_tab("Final Result", display_img)
                    self.status_var.set(f"Processing Complete. Found {count} valid contours.")
                
                step_idx += 1

        except Exception as e:
            messagebox.showerror("Processing Error", str(e))
            self.status_var.set("Error during processing.")

if __name__ == "__main__":
    try:
        import PIL
    except ImportError:
        print("Error: This GUI requires the 'Pillow' library.")
        print("Please install it using: pip install Pillow")
        exit(1)

    root = tk.Tk()
    app = VisionGUI(root)
    root.mainloop()
