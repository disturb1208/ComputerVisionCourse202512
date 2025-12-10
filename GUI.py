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
        self.root.geometry("1024x768")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Pipeline Configuration (Default)
        self.pipeline_config = [
            {"type": "blur", "params": {"type": "gaussian", "ksize": 9}},
            {"type": "threshold", "params": {"threshold": 127}},
            {"type": "edge", "params": {"method": "canny", "threshold1": 50, "threshold2": 150, "ksize": 3}},
            {"type": "contour", "params": {"thresholdValue": 136, "retrievalMode": "TREE", "minArea": 550, 
                                           "showBoundingBox": False, "showCentroid": True, "showLabel": True}}
        ]

        self.current_image_path = None
        self.processed_images = {} # Store (name, image_data)

        self._setup_ui()

    def _setup_ui(self):
        # --- Top Control Panel ---
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_load = ttk.Button(control_frame, text="📂 Load Image", command=self.load_image)
        self.btn_load.pack(side=tk.LEFT, padx=5)

        self.btn_run = ttk.Button(control_frame, text="⚙️ Run Pipeline", command=self.run_pipeline, state=tk.DISABLED)
        self.btn_run.pack(side=tk.LEFT, padx=5)
        
        # --- Main Display Area (Tabs) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
        self.processed_images = {}

    def add_tab(self, title, cv_image):
        """
        Adds a new tab to the notebook with the given image.
        Handles resizing and color conversion.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        
        # Convert CV2 (BGR) to PIL (RGB)
        if len(cv_image.shape) == 2: # Grayscale
            img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
        pil_img = Image.fromarray(img_rgb)
        
        # Calculate resize to fit window (roughly)
        display_w = self.root.winfo_width() - 40
        display_h = self.root.winfo_height() - 100
        if display_w < 100: display_w = 800 # Fallback if window not drawn yet
        if display_h < 100: display_h = 600
        
        # Resize logic
        w_percent = (display_w / float(pil_img.size[0]))
        h_percent = (display_h / float(pil_img.size[1]))
        resize_scale = min(w_percent, h_percent, 1.0) # Don't upscale
        
        new_w = int((float(pil_img.size[0]) * float(resize_scale)))
        new_h = int((float(pil_img.size[1]) * float(resize_scale)))
        
        pil_img_resized = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(pil_img_resized)
        
        # Label to hold image
        lbl = ttk.Label(frame, image=tk_img)
        lbl.image = tk_img # Keep reference!
        lbl.pack(expand=True)
        
        # Select this tab
        self.notebook.select(frame)

    def run_pipeline(self):
        if not self.current_image_path:
            return
            
        self.status_var.set("Processing...")
        self.root.update_idletasks() # Force UI update
        
        original_img = cv2.imread(self.current_image_path)
        if original_img is None:
            return

        # Initialize pipeline vars
        gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        current_img = gray_img
        display_img = original_img.copy() # For final drawing
        
        # We already showed Original, let's process steps
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

                elif step_type == "contour":
                    # Logic specific to contour drawing on the FINAL image
                    thresh_val = params.get("thresholdValue", 127) # Not really used if input is binary
                    mode_str = params.get("retrievalMode", "TREE")
                    min_area = params.get("minArea", 0)
                    show_bbox = params.get("showBoundingBox", False)
                    show_centroid = params.get("showCentroid", True)
                    show_label = params.get("showLabel", True)

                    mode = cv2.RETR_TREE
                    if mode_str == "EXTERNAL": mode = cv2.RETR_EXTERNAL
                    elif mode_str == "LIST": mode = cv2.RETR_LIST

                    # Ensure binary
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
                        
                        # Draw on the COLOR display image
                        cv2.drawContours(display_img, [cnt], -1, (0, 255, 0), 2)
                        
                        # Bounding Box
                        if show_bbox:
                            x, y, w, h = cv2.boundingRect(cnt)
                            cv2.rectangle(display_img, (x, y), (x+w, y+h), (255, 0, 0), 2)

                        # Centroid
                        M = cv2.moments(cnt)
                        cx, cy = 0, 0
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                        
                        if show_centroid and M['m00'] != 0:
                            cv2.circle(display_img, (cx, cy), 5, (0, 0, 255), -1)

                        if show_label:
                            label_text = f"ID:{i} A:{int(area)}"
                            text_pos = (cx - 20, cy - 10) if M['m00'] != 0 else (cnt[0][0][0], cnt[0][0][1])
                            cv2.putText(display_img, label_text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    
                    self.add_tab("Final Result", display_img)
                    self.status_var.set(f"Processing Complete. Found {count} valid contours.")
                
                step_idx += 1

        except Exception as e:
            messagebox.showerror("Processing Error", str(e))
            self.status_var.set("Error during processing.")

if __name__ == "__main__":
    # Ensure Pillow is installed
    try:
        import PIL
    except ImportError:
        print("Error: This GUI requires the 'Pillow' library.")
        print("Please install it using: pip install Pillow")
        exit(1)

    root = tk.Tk()
    app = VisionGUI(root)
    root.mainloop()
