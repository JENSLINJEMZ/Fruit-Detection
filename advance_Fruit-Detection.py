import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
import cv2
import numpy as np
import os
import tempfile
from datetime import datetime
import base64
import json
import threading
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import webbrowser

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class ModernFruitAnalyzerGUI:
    def __init__(self, api_key):
        self.API_KEY = api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.API_KEY
        }
        
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("🍎 Advanced Fruit Health Analyzer Pro")
        self.root.geometry("1500x950")
        self.root.minsize(1200, 800)
        
        # Center window on screen
        self.center_window()
        
        # Variables
        self.current_image = None
        self.current_image_cv2 = None
        self.analysis_result = None
        self.comparison_mode = False
        self.history = []
        
        # Setup UI
        self.setup_ui()
        
        # Add keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.load_from_file())
        self.root.bind('<Control-s>', lambda e: self.save_report())
        self.root.bind('<Control-c>', lambda e: self.capture_from_camera())
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """Setup the modern UI"""
        # Main container with gradient effect
        self.main_container = ctk.CTkFrame(self.root, fg_color="#0a0a0a")
        self.main_container.pack(fill="both", expand=True)
        
        # Header
        self.create_header()
        
        # Create tabview for different sections
        self.tabview = ctk.CTkTabview(self.main_container, 
                                      fg_color="#1a1a1a",
                                      segmented_button_fg_color="#2a2a2a",
                                      segmented_button_selected_color="#1e8e3e")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Add tabs
        self.tabview.add("🔍 Analysis")
        self.tabview.add("📊 Comparison")
        self.tabview.add("📈 History")
        self.tabview.add("💡 Tips & Guide")
        
        # Setup each tab
        self.setup_analysis_tab()
        self.setup_comparison_tab()
        self.setup_history_tab()
        self.setup_tips_tab()
        
    def create_header(self):
        """Create professional header with animated gradient"""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="#0f0f0f", height=100)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Create gradient background
        gradient_frame = ctk.CTkFrame(header_frame, fg_color="#1a1a1a", height=100)
        gradient_frame.pack(fill="both", expand=True)
        
        # Title with animation effect
        title_label = ctk.CTkLabel(
            gradient_frame,
            text="🍎 ADVANCED FRUIT HEALTH ANALYZER PRO 🍊",
            font=ctk.CTkFont(family="Arial Black", size=32, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=(15, 5))
        
        # Subtitle with date and features
        subtitle_frame = ctk.CTkFrame(gradient_frame, fg_color="transparent")
        subtitle_frame.pack()
        
        features = ["AI-Powered", "Disease Detection", "Quality Analysis", "Prevention Tips"]
        for i, feature in enumerate(features):
            label = ctk.CTkLabel(
                subtitle_frame,
                text=f"✓ {feature}",
                font=ctk.CTkFont(family="Arial", size=12),
                text_color="#4CAF50"
            )
            label.grid(row=0, column=i, padx=15)
        
        # Date and time
        self.time_label = ctk.CTkLabel(
            gradient_frame,
            text=datetime.now().strftime('%B %d, %Y | %I:%M %p'),
            font=ctk.CTkFont(family="Arial", size=11),
            text_color="#888888"
        )
        self.time_label.pack()
        
        # Update time every second
        self.update_time()
        
    def update_time(self):
        """Update time display"""
        self.time_label.configure(text=datetime.now().strftime('%B %d, %Y | %I:%M %p'))
        self.root.after(1000, self.update_time)
        
    def setup_analysis_tab(self):
        """Setup main analysis tab"""
        analysis_frame = self.tabview.tab("🔍 Analysis")
        
        # Create three columns
        left_frame = ctk.CTkFrame(analysis_frame, fg_color="#1a1a1a", width=450)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        middle_frame = ctk.CTkFrame(analysis_frame, fg_color="#1a1a1a", width=450)
        middle_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        right_frame = ctk.CTkFrame(analysis_frame, fg_color="#1a1a1a")
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Left column - Image display
        self.setup_image_display(left_frame)
        
        # Middle column - Quick results
        self.setup_quick_results(middle_frame)
        
        # Right column - Detailed analysis
        self.setup_detailed_results(right_frame)
        
    def setup_image_display(self, parent):
        """Setup image display section"""
        # Image frame with border
        image_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a", corner_radius=15,
                                  border_width=2, border_color="#333333")
        image_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Image label
        self.image_label = ctk.CTkLabel(
            image_frame,
            text="📷 No Image Loaded\n\nDrag & Drop or Click buttons below",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        )
        self.image_label.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Enable drag and drop
        self.enable_drag_drop(self.image_label)
        
        # Control buttons
        controls_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", height=200)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        controls_frame.pack_propagate(False)
        
        # Button grid
        button_style = {
            "font": ctk.CTkFont(size=14, weight="bold"),
            "height": 40,
            "corner_radius": 8,
            "border_width": 2
        }
        
        # Row 1
        btn_frame1 = ctk.CTkFrame(controls_frame, fg_color="transparent")
        btn_frame1.pack(fill="x", pady=5)
        
        self.camera_btn = ctk.CTkButton(
            btn_frame1,
            text="📷 Camera",
            command=self.capture_from_camera,
            fg_color="#1e8e3e",
            hover_color="#2ba84a",
            border_color="#1e8e3e",
            **button_style
        )
        self.camera_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        self.file_btn = ctk.CTkButton(
            btn_frame1,
            text="📁 File",
            command=self.load_from_file,
            fg_color="#1976d2",
            hover_color="#2196f3",
            border_color="#1976d2",
            **button_style
        )
        self.file_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # Row 2
        btn_frame2 = ctk.CTkFrame(controls_frame, fg_color="transparent")
        btn_frame2.pack(fill="x", pady=5)
        
        self.url_btn = ctk.CTkButton(
            btn_frame2,
            text="🌐 URL",
            command=self.load_from_url,
            fg_color="#9c27b0",
            hover_color="#ab47bc",
            border_color="#9c27b0",
            **button_style
        )
        self.url_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        self.clear_btn = ctk.CTkButton(
            btn_frame2,
            text="🗑️ Clear",
            command=self.clear_image,
            fg_color="#f44336",
            hover_color="#ef5350",
            border_color="#f44336",
            **button_style
        )
        self.clear_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # Analyze button (prominent)
        self.analyze_btn = ctk.CTkButton(
            controls_frame,
            text="🔬 ANALYZE FRUIT HEALTH",
            command=self.analyze_image,
            fg_color="#ff6f00",
            hover_color="#ff8f00",
            border_color="#ff6f00",
            state="disabled",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=10,
            border_width=3
        )
        self.analyze_btn.pack(fill="x", padx=10, pady=15)
        
        # Add keyboard shortcut hints
        shortcuts_label = ctk.CTkLabel(
            controls_frame,
            text="Shortcuts: Ctrl+O (File) | Ctrl+C (Camera) | Ctrl+S (Save)",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        shortcuts_label.pack()
        
    def setup_quick_results(self, parent):
        """Setup quick results section"""
        # Header
        header_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a", height=50, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="⚡ Quick Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        header_label.pack(pady=12)
        
        # Results container
        self.quick_results_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        self.quick_results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial state
        self.no_quick_results = ctk.CTkLabel(
            self.quick_results_frame,
            text="⏳ Awaiting analysis...\n\nLoad an image and click 'Analyze'",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.no_quick_results.pack(expand=True)
        
    def setup_detailed_results(self, parent):
        """Setup detailed results section"""
        # Header
        header_frame = ctk.CTkFrame(parent, fg_color="#2a2a2a", height=50, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="📋 Detailed Report",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        header_label.pack(pady=12)
        
        # Scrollable results
        self.detailed_scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="#1a1a1a",
            corner_radius=10
        )
        self.detailed_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial message
        self.no_detailed_results = ctk.CTkLabel(
            self.detailed_scroll,
            text="📊 No detailed analysis yet\n\nDetailed results will appear here",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.no_detailed_results.pack(pady=50)
        
    def setup_comparison_tab(self):
        """Setup comparison tab for before/after analysis"""
        comparison_frame = self.tabview.tab("📊 Comparison")
        
        info_label = ctk.CTkLabel(
            comparison_frame,
            text="🔄 Compare fruits or track changes over time",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        )
        info_label.pack(pady=20)
        
        # Two image frames side by side
        images_frame = ctk.CTkFrame(comparison_frame, fg_color="transparent")
        images_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Before frame
        before_frame = ctk.CTkFrame(images_frame, fg_color="#2a2a2a", corner_radius=15)
        before_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        before_label = ctk.CTkLabel(
            before_frame,
            text="📷 Before\n\nLoad first image",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        before_label.pack(expand=True)
        
        # After frame
        after_frame = ctk.CTkFrame(images_frame, fg_color="#2a2a2a", corner_radius=15)
        after_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        after_label = ctk.CTkLabel(
            after_frame,
            text="📷 After\n\nLoad second image",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        after_label.pack(expand=True)
        
    def setup_history_tab(self):
        """Setup history tab"""
        history_frame = self.tabview.tab("📈 History")
        
        # History list
        self.history_list = ctk.CTkScrollableFrame(history_frame, fg_color="#1a1a1a")
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        if not self.history:
            no_history = ctk.CTkLabel(
                self.history_list,
                text="📜 No analysis history yet\n\nYour previous analyses will appear here",
                font=ctk.CTkFont(size=14),
                text_color="#666666"
            )
            no_history.pack(pady=50)
            
    def setup_tips_tab(self):
        """Setup tips and guide tab"""
        tips_frame = self.tabview.tab("💡 Tips & Guide")
        
        # Scrollable tips area
        tips_scroll = ctk.CTkScrollableFrame(tips_frame, fg_color="#1a1a1a")
        tips_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tips categories
        tips_data = {
            "🍎 Fruit Selection Tips": [
                "Choose fruits with vibrant, consistent colors",
                "Avoid fruits with soft spots or bruises",
                "Check for firmness - should feel solid but not rock hard",
                "Look for smooth, unblemished skin",
                "Smell the fruit - it should have a pleasant aroma"
            ],
            "🌡️ Storage Guidelines": [
                "Store apples in cool, dry place (32-35°F)",
                "Keep bananas at room temperature",
                "Refrigerate berries immediately",
                "Don't wash fruits until ready to eat",
                "Keep ethylene-producing fruits separate"
            ],
            "🦠 Disease Prevention": [
                "Inspect fruits regularly for early signs",
                "Remove infected fruits immediately",
                "Maintain proper humidity levels",
                "Use natural fungicides like vinegar spray",
                "Ensure good air circulation in storage"
            ],
            "📸 Best Practices for Analysis": [
                "Use good lighting when taking photos",
                "Capture the entire fruit in frame",
                "Show any problem areas clearly",
                "Take multiple angles if needed",
                "Ensure image is in focus"
            ]
        }
        
        for category, tips in tips_data.items():
            # Category header
            category_frame = ctk.CTkFrame(tips_scroll, fg_color="#2a2a2a", corner_radius=10)
            category_frame.pack(fill="x", padx=10, pady=10)
            
            category_label = ctk.CTkLabel(
                category_frame,
                text=category,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#4CAF50"
            )
            category_label.pack(anchor="w", padx=20, pady=(15, 10))
            
            # Tips list
            for tip in tips:
                tip_label = ctk.CTkLabel(
                    category_frame,
                    text=f"• {tip}",
                    font=ctk.CTkFont(size=13),
                    text_color="#cccccc",
                    anchor="w",
                    wraplength=800
                )
                tip_label.pack(anchor="w", padx=40, pady=3)
            
            category_frame.pack(pady=(0, 5))
            
    def enable_drag_drop(self, widget):
        """Enable drag and drop functionality"""
        # This is a placeholder - actual implementation would require platform-specific code
        pass
        
    def load_from_file(self):
        """Load image from file"""
        file_path = filedialog.askopenfilename(
            title="Select Fruit Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Load with OpenCV
                image = cv2.imread(file_path)
                if image is not None:
                    self.current_image_cv2 = image
                    self.display_image(image)
                    self.analyze_btn.configure(state="normal")
                    messagebox.showinfo("Success", "Image loaded successfully!")
                else:
                    messagebox.showerror("Error", "Could not load image file")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading image: {str(e)}")
                
    def clear_image(self):
        """Clear current image and results"""
        self.current_image_cv2 = None
        self.current_image = None
        self.analysis_result = None
        
        # Reset image display
        self.image_label.configure(
            image=None,
            text="📷 No Image Loaded\n\nDrag & Drop or Click buttons below"
        )
        
        # Clear results
        for widget in self.quick_results_frame.winfo_children():
            widget.destroy()
        self.no_quick_results = ctk.CTkLabel(
            self.quick_results_frame,
            text="⏳ Awaiting analysis...\n\nLoad an image and click 'Analyze'",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.no_quick_results.pack(expand=True)
        
        for widget in self.detailed_scroll.winfo_children():
            widget.destroy()
        self.no_detailed_results = ctk.CTkLabel(
            self.detailed_scroll,
            text="📊 No detailed analysis yet\n\nDetailed results will appear here",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.no_detailed_results.pack(pady=50)
        
        # Disable analyze button
        self.analyze_btn.configure(state="disabled")
        
    def capture_from_camera(self):
        """Enhanced camera capture with preview"""
        camera_window = ctk.CTkToplevel(self.root)
        camera_window.title("📷 Capture Fruit Image")
        camera_window.geometry("900x700")
        camera_window.transient(self.root)
        
        # Main frame
        main_frame = ctk.CTkFrame(camera_window, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instructions
        instruction_frame = ctk.CTkFrame(main_frame, fg_color="#2a2a2a", corner_radius=10)
        instruction_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        instructions = ctk.CTkLabel(
            instruction_frame,
            text="📸 Position the fruit in the center circle and press SPACE or click CAPTURE",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        instructions.pack(pady=15)
        
        # Video frame
        video_frame = ctk.CTkFrame(main_frame, fg_color="#000000", corner_radius=15,
                                  border_width=3, border_color="#4CAF50")
        video_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        video_label = tk.Label(video_frame, bg="#000000")
        video_label.pack(fill="both", expand=True)
        
        # Control panel
        control_panel = ctk.CTkFrame(main_frame, fg_color="#2a2a2a", corner_radius=10)
        control_panel.pack(fill="x", padx=10, pady=10)
        
        # Camera controls
        controls_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        controls_frame.pack(pady=10)
        
        # Brightness slider
        brightness_label = ctk.CTkLabel(controls_frame, text="Brightness:")
        brightness_label.grid(row=0, column=0, padx=10)
        
        self.brightness_slider = ctk.CTkSlider(
            controls_frame,
            from_=0.5,
            to=2.0,
            number_of_steps=30,
            command=self.update_camera_settings
        )
        self.brightness_slider.set(1.0)
        self.brightness_slider.grid(row=0, column=1, padx=10)
        
        # Start camera
        self.camera_active = True
        self.captured_frame = None
        self.camera_brightness = 1.0
        
        def camera_loop():
            if os.name == 'nt':  # Windows
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                messagebox.showerror("Error", "Could not open camera")
                camera_window.destroy()
                return
            
            # Optimize camera
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            while self.camera_active:
                ret, frame = cap.read()
                if ret:
                    # Apply brightness
                    frame = cv2.convertScaleAbs(frame, alpha=self.camera_brightness, beta=0)
                    
                    # Add overlay
                    frame_display = self.add_camera_overlay(frame)
                    
                    # Convert to PIL
                    cv2image = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(cv2image)
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Update display
                    video_label.configure(image=imgtk)
                    video_label.image = imgtk
                    
                    # Store current frame
                    self.current_frame = frame
                    
                cv2.waitKey(30)
            
            cap.release()
        
        def capture_image(event=None):
            if hasattr(self, 'current_frame'):
                self.captured_frame = self.current_frame.copy()
                self.camera_active = False
                camera_window.destroy()
                
                # Update main window
                self.current_image_cv2 = self.captured_frame
                self.display_image(self.captured_frame)
                self.analyze_btn.configure(state="normal")
                
                # Success feedback
                self.show_notification("✅ Image captured successfully!", "success")
        
        # Bind keys
        camera_window.bind('<space>', capture_image)
        camera_window.bind('<Return>', capture_image)
        
        # Capture button
        capture_btn = ctk.CTkButton(
            control_panel,
            text="📸 CAPTURE (SPACE)",
            command=capture_image,
            font=ctk.CTkFont(size=20, weight="bold"),
            height=60,
            fg_color="#4CAF50",
            hover_color="#45a049",
            corner_radius=30
        )
        capture_btn.pack(pady=(10, 20))
        
        # Start camera thread
        camera_thread = threading.Thread(target=camera_loop, daemon=True)
        camera_thread.start()
        
        # Handle close
        def on_closing():
            self.camera_active = False
            camera_window.destroy()
        
        camera_window.protocol("WM_DELETE_WINDOW", on_closing)
        
    def add_camera_overlay(self, frame):
        """Add professional overlay to camera feed"""
        height, width = frame.shape[:2]
        overlay = frame.copy()
        
        # Center coordinates
        center_x, center_y = width // 2, height // 2
        
        # Draw center circle (target area)
        cv2.circle(overlay, (center_x, center_y), 150, (0, 255, 0), 3)
        cv2.circle(overlay, (center_x, center_y), 148, (0, 0, 0), 1)
        
        # Draw corner brackets
        bracket_length = 50
        bracket_thickness = 3
        corners = [
            (center_x - 200, center_y - 200),
            (center_x + 200, center_y - 200),
            (center_x - 200, center_y + 200),
            (center_x + 200, center_y + 200)
        ]
        
        for i, (x, y) in enumerate(corners):
            if i == 0:  # Top-left
                cv2.line(overlay, (x, y), (x + bracket_length, y), (0, 255, 0), bracket_thickness)
                cv2.line(overlay, (x, y), (x, y + bracket_length), (0, 255, 0), bracket_thickness)
            elif i == 1:  # Top-right
                cv2.line(overlay, (x, y), (x - bracket_length, y), (0, 255, 0), bracket_thickness)
                cv2.line(overlay, (x, y), (x, y + bracket_length), (0, 255, 0), bracket_thickness)
            elif i == 2:  # Bottom-left
                cv2.line(overlay, (x, y), (x + bracket_length, y), (0, 255, 0), bracket_thickness)
                cv2.line(overlay, (x, y), (x, y - bracket_length), (0, 255, 0), bracket_thickness)
            else:  # Bottom-right
                cv2.line(overlay, (x, y), (x - bracket_length, y), (0, 255, 0), bracket_thickness)
                cv2.line(overlay, (x, y), (x, y - bracket_length), (0, 255, 0), bracket_thickness)
        
        # Add text overlays
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(overlay, "FRUIT DETECTION AREA", (center_x - 120, center_y - 180),
                   font, 0.8, (0, 255, 0), 2)
        
        # Grid lines
        grid_spacing = 100
        for i in range(0, width, grid_spacing):
            cv2.line(overlay, (i, 0), (i, height), (50, 50, 50), 1)
        for i in range(0, height, grid_spacing):
            cv2.line(overlay, (0, i), (width, i), (50, 50, 50), 1)
        
        # Blend overlay
        return cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
    def update_camera_settings(self, value):
        """Update camera brightness"""
        self.camera_brightness = float(value)
        
    def load_from_url(self):
        """Load image from URL"""
        dialog = ctk.CTkInputDialog(
            text="Enter image URL:",
            title="Load Image from URL"
        )
        url = dialog.get_input()
        
        if url:
            try:
                self.show_loading("Downloading image...")
                
                response = requests.get(url, stream=True, timeout=10)
                if response.status_code == 200:
                    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    if image is not None:
                        self.current_image_cv2 = image
                        self.display_image(image)
                        self.analyze_btn.configure(state="normal")
                        self.show_notification("✅ Image loaded successfully!", "success")
                    else:
                        self.show_notification("❌ Could not decode image", "error")
                else:
                    self.show_notification(f"❌ Download failed: {response.status_code}", "error")
                    
            except Exception as e:
                self.show_notification(f"❌ Error: {str(e)}", "error")
            finally:
                self.hide_loading()
                
    def display_image(self, cv2_image):
        """Display image with better scaling"""
        # Convert CV2 to PIL
        image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Calculate display size maintaining aspect ratio
        display_width = 420
        aspect_ratio = pil_image.height / pil_image.width
        display_height = int(display_width * aspect_ratio)
        
        # Limit height
        if display_height > 350:
            display_height = 350
            display_width = int(display_height / aspect_ratio)
        
        # Resize
        pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        # Add border
        border_color = (76, 175, 80)  # Green
        bordered_image = Image.new('RGB', 
                                  (pil_image.width + 6, pil_image.height + 6), 
                                  border_color)
        bordered_image.paste(pil_image, (3, 3))
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(bordered_image)
        
        # Update label
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo
        
    def analyze_image(self):
        """Enhanced analysis with better feedback"""
        if self.current_image_cv2 is None:
            self.show_notification("⚠️ No image loaded", "warning")
            return
        
        # Disable button and show progress
        self.analyze_btn.configure(state="disabled", text="🔄 ANALYZING...")
        
        # Clear previous results
        self.clear_results()
        
        # Show progress in quick results
        progress_frame = ctk.CTkFrame(self.quick_results_frame, fg_color="transparent")
        progress_frame.pack(expand=True)
        
        progress_label = ctk.CTkLabel(
            progress_frame,
            text="🔬 Performing Deep Analysis...",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        progress_label.pack(pady=20)
        
        # Progress bar
        progress_bar = ctk.CTkProgressBar(progress_frame, width=300, height=20,
                                         progress_color="#4CAF50")
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        # Status label
        status_label = ctk.CTkLabel(
            progress_frame,
            text="Initializing...",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        status_label.pack(pady=5)
        
        # Perform analysis in thread
        def analysis_thread():
            try:
                # Stage 1: Local analysis
                status_label.configure(text="🔍 Analyzing visual features...")
                progress_bar.set(0.3)
                local_results = self.perform_local_analysis(self.current_image_cv2)
                
                # Stage 2: AI analysis
                status_label.configure(text="🤖 AI examining fruit condition...")
                progress_bar.set(0.6)
                gemini_results = self.analyze_with_gemini(self.current_image_cv2)
                
                # Stage 3: Combine results
                status_label.configure(text="📊 Generating comprehensive report...")
                progress_bar.set(0.9)
                final_result = self.combine_analysis_results(gemini_results, local_results)
                
                # Complete
                progress_bar.set(1.0)
                status_label.configure(text="✅ Analysis complete!")
                
                # Update UI
                self.root.after(500, lambda: self.display_analysis_results(final_result))
                
                # Add to history
                self.add_to_history(final_result)
                
            except Exception as e:
                self.root.after(100, lambda: self.show_notification(f"❌ Analysis failed: {str(e)}", "error"))
            finally:
                self.root.after(100, lambda: self.analyze_btn.configure(
                    state="normal", 
                    text="🔬 ANALYZE FRUIT HEALTH"
                ))
        
        # Start analysis
        thread = threading.Thread(target=analysis_thread, daemon=True)
        thread.start()
        
    def clear_results(self):
        """Clear all result displays"""
        for widget in self.quick_results_frame.winfo_children():
            widget.destroy()
        for widget in self.detailed_scroll.winfo_children():
            widget.destroy()
            
    def display_analysis_results(self, result):
        """Display results with enhanced visual feedback"""
        # Clear previous results
        self.clear_results()
        
        # Store result
        self.analysis_result = result
        
        # Display quick results
        self.display_quick_results(result)
        
        # Display detailed results
        self.display_detailed_results(result)
        
        # Update image with overlay
        self.show_defect_overlay()
        
        # Show notification based on condition
        condition = result.get('condition', '')
        if 'EXCELLENT' in condition:
            self.show_notification("🎉 Excellent quality fruit detected!", "success")
        elif 'GOOD' in condition:
            self.show_notification("✅ Good quality fruit!", "success")
        elif 'FAIR' in condition:
            self.show_notification("⚠️ Fair quality - monitor closely", "warning")
        elif 'POOR' in condition:
            self.show_notification("⚠️ Poor quality - use immediately", "warning")
        elif 'BAD' in condition or 'DISCARD' in condition:
            self.show_notification("🚨 Bad condition - DO NOT CONSUME!", "error")
        elif 'INSECT' in condition:
            self.show_notification("🐛 Insect damage detected - remove from batch", "error")
            
    def display_quick_results(self, result):
        """Display quick results with visual indicators"""
        # Determine condition colors
        condition = result.get('condition', '')
        is_bad = 'BAD' in condition or 'DISCARD' in condition or 'INSECT' in condition
        is_excellent = 'EXCELLENT' in condition
        is_good = 'GOOD' in condition
        is_fair = 'FAIR' in condition
        is_poor = 'POOR' in condition
        
        # Set color scheme
        if is_bad:
            bg_color = "#ff0000"
            text_color = "#ffffff"
            icon = "🚫"
            pulse_color = "#ff6666"
        elif is_poor:
            bg_color = "#ff6347"
            text_color = "#ffffff"
            icon = "⚠️"
            pulse_color = "#ff9999"
        elif is_fair:
            bg_color = "#ffa500"
            text_color = "#000000"
            icon = "⚠️"
            pulse_color = "#ffcc66"
        elif is_good:
            bg_color = "#32cd32"
            text_color = "#ffffff"
            icon = "✅"
            pulse_color = "#66ff66"
        elif is_excellent:
            bg_color = "#00ff00"
            text_color = "#000000"
            icon = "🌟"
            pulse_color = "#66ff99"
        else:
            bg_color = "#808080"
            text_color = "#ffffff"
            icon = "❓"
            pulse_color = "#cccccc"
        
        # Main condition card with animation
        condition_card = ctk.CTkFrame(self.quick_results_frame, 
                                     fg_color=bg_color, 
                                     corner_radius=20,
                                     border_width=3,
                                     border_color=pulse_color)
        condition_card.pack(fill="x", padx=10, pady=10)
        
        # Condition display with large text
        condition_frame = ctk.CTkFrame(condition_card, fg_color="transparent")
        condition_frame.pack(pady=20)
        
        # Icon and condition text
        icon_label = ctk.CTkLabel(
            condition_frame,
            text=icon,
            font=ctk.CTkFont(size=48),
            text_color=text_color
        )
        icon_label.pack()
        
        condition_text = result['condition'].replace(' - ', '\n')
        condition_label = ctk.CTkLabel(
            condition_frame,
            text=condition_text,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=text_color
        )
        condition_label.pack(pady=10)
        
        # Confidence meter
        confidence_frame = ctk.CTkFrame(condition_card, fg_color="transparent")
        confidence_frame.pack(pady=10)
        
        confidence_label = ctk.CTkLabel(
            confidence_frame,
            text="AI Confidence:",
            font=ctk.CTkFont(size=14),
            text_color=text_color
        )
        confidence_label.pack()
        
        # Visual confidence bar
        confidence_bar = ctk.CTkProgressBar(
            confidence_frame,
            width=250,
            height=25,
            corner_radius=12,
            fg_color="#333333",
            progress_color=text_color,
            border_width=2,
            border_color=text_color
        )
        confidence_bar.pack(pady=5)
        confidence_bar.set(result['confidence'] / 100)
        
        confidence_percent = ctk.CTkLabel(
            confidence_frame,
            text=f"{result['confidence']:.0f}%",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=text_color
        )
        confidence_percent.pack()
        
        # Key metrics grid
        metrics_frame = ctk.CTkFrame(self.quick_results_frame, fg_color="#2a2a2a", corner_radius=15)
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        # Title
        metrics_title = ctk.CTkLabel(
            metrics_frame,
            text="📊 Key Metrics",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        metrics_title.pack(pady=(15, 10))
        
        # Metrics grid
        metrics_grid = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        metrics_grid.pack(pady=10)
        
        local = result['local_analysis']
        
        # Create metric cards
        metrics = [
            ("🍎 Fruit Type", result.get('fruit_type', 'Unknown').upper(), "#4CAF50"),
            ("💚 Freshness", f"{local['freshness_score']:.0f}%", 
             "#ff0000" if local['freshness_score'] < 50 else "#ffa500" if local['freshness_score'] < 75 else "#4CAF50"),
            ("🦠 Decay Level", f"{local['brown_rot_percentage']:.1f}%", 
             "#4CAF50" if local['brown_rot_percentage'] < 5 else "#ffa500" if local['brown_rot_percentage'] < 15 else "#ff0000"),
            ("⚫ Black Spots", f"{local['black_spots_percentage']:.1f}%",
             "#4CAF50" if local['black_spots_percentage'] < 2 else "#ffa500" if local['black_spots_percentage'] < 10 else "#ff0000")
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            metric_card = ctk.CTkFrame(metrics_grid, fg_color="#333333", corner_radius=10)
            metric_card.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            
            label_widget = ctk.CTkLabel(
                metric_card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            label_widget.pack(pady=(10, 0))
            
            value_widget = ctk.CTkLabel(
                metric_card,
                text=value,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            )
            value_widget.pack(pady=(0, 10))
        
        # Action required card (if needed)
        if is_bad or is_poor:
            action_card = ctk.CTkFrame(self.quick_results_frame, 
                                      fg_color="#ff0000" if is_bad else "#ff6347",
                                      corner_radius=15,
                                      border_width=2,
                                      border_color="#ffffff")
            action_card.pack(fill="x", padx=10, pady=10)
            
            action_label = ctk.CTkLabel(
                action_card,
                text=f"⚠️ ACTION REQUIRED ⚠️\n{result.get('action_required', 'Check fruit condition').upper()}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ffffff"
            )
            action_label.pack(pady=15)
        
        # Prevention tips (quick view)
        if result.get('prevention_tips'):
            tips_card = ctk.CTkFrame(self.quick_results_frame, fg_color="#1a3a1a", corner_radius=15)
            tips_card.pack(fill="x", padx=10, pady=10)
            
            tips_title = ctk.CTkLabel(
                tips_card,
                text="💡 Quick Tips",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#4CAF50"
            )
            tips_title.pack(pady=(10, 5))
            
            # Show first 2 tips
            for tip in result['prevention_tips'][:2]:
                tip_label = ctk.CTkLabel(
                    tips_card,
                    text=f"• {tip}",
                    font=ctk.CTkFont(size=12),
                    text_color="#90EE90",
                    wraplength=350
                )
                tip_label.pack(anchor="w", padx=20, pady=2)
            
            tips_card.pack(pady=(0, 10))
            
    def display_detailed_results(self, result):
        """Display comprehensive detailed results"""
        # AI Analysis Section
        if result.get('gemini_analysis'):
            self.create_ai_analysis_section(result['gemini_analysis'])
        
        # Disease & Defects Section
        self.create_defects_section(result)
        
        # Recommendations Section
        self.create_recommendations_section(result)
        
        # Technical Analysis Section
        self.create_technical_section(result['local_analysis'])
        
        # Save & Export Options
        self.create_export_section()
        
    def create_ai_analysis_section(self, gemini_data):
        """Create AI analysis section"""
        section = self.create_section("🤖 AI Expert Analysis", "#1a2e1a")
        
        # Ripeness status with visual indicator
        ripeness = gemini_data.get('ripeness', 'unknown')
        ripeness_colors = {
            'under-ripe': ('#90EE90', '🟢'),
            'perfectly-ripe': ('#00FF00', '🟢'),
            'ripe': ('#FFD700', '🟡'),
            'overripe': ('#FFA500', '🟠'),
            'rotten': ('#FF0000', '🔴')
        }
        
        color, icon = ripeness_colors.get(ripeness, ('#808080', '⚪'))
        
        ripeness_frame = ctk.CTkFrame(section, fg_color="#2a3a2a", corner_radius=10)
        ripeness_frame.pack(fill="x", pady=5)
        
        ripeness_label = ctk.CTkLabel(
            ripeness_frame,
            text=f"{icon} Ripeness: {ripeness.replace('-', ' ').title()}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color
        )
        ripeness_label.pack(pady=10)
        
        # Safety assessment with clear visual
        safety = gemini_data.get('safety_assessment', 'unknown')
        safety_frame = ctk.CTkFrame(section, fg_color="#2a3a2a", corner_radius=10)
        safety_frame.pack(fill="x", pady=5)
        
        if 'unsafe' in safety.lower():
            safety_color = "#FF0000"
            safety_icon = "🚫"
            safety_bg = "#3a1a1a"
        elif 'questionable' in safety.lower():
            safety_color = "#FFA500"
            safety_icon = "⚠️"
            safety_bg = "#3a2a1a"
        else:
            safety_color = "#00FF00"
            safety_icon = "✅"
            safety_bg = "#1a3a1a"
        
        safety_frame.configure(fg_color=safety_bg)
        
        safety_label = ctk.CTkLabel(
            safety_frame,
            text=f"{safety_icon} Safety: {safety.upper()}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=safety_color
        )
        safety_label.pack(pady=12)
        
        # Detailed observations
        if gemini_data.get('key_observations'):
            obs_frame = ctk.CTkFrame(section, fg_color="#2a3a2a", corner_radius=10)
            obs_frame.pack(fill="x", pady=5)
            
            obs_title = ctk.CTkLabel(
                obs_frame,
                text="🔍 Key Observations:",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ffffff"
            )
            obs_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            for obs in gemini_data['key_observations']:
                obs_label = ctk.CTkLabel(
                    obs_frame,
                    text=f"• {obs}",
                    font=ctk.CTkFont(size=12),
                    text_color="#cccccc",
                    wraplength=600,
                    anchor="w",
                    justify="left"
                )
                obs_label.pack(anchor="w", padx=30, pady=2)
        
        # Storage advice
        if gemini_data.get('storage_advice'):
            storage_frame = ctk.CTkFrame(section, fg_color="#2a3a2a", corner_radius=10)
            storage_frame.pack(fill="x", pady=5)
            
            storage_title = ctk.CTkLabel(
                storage_frame,
                text="📦 Storage Recommendations:",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#4CAF50"
            )
            storage_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            storage_label = ctk.CTkLabel(
                storage_frame,
                text=gemini_data['storage_advice'],
                font=ctk.CTkFont(size=12),
                text_color="#90EE90",
                wraplength=600,
                anchor="w",
                justify="left"
            )
            storage_label.pack(anchor="w", padx=30, pady=(0, 10))
            
    def create_defects_section(self, result):
        """Create defects and disease section"""
        gemini_data = result.get('gemini_analysis', {})
        defects = gemini_data.get('defects_found', [])
        
        if defects or result['local_analysis']['brown_rot_percentage'] > 5 or result['local_analysis']['black_spots_percentage'] > 2:
            section = self.create_section("🦠 Defects & Diseases Detected", "#3a1a1a")
            
            # Defects list
            if defects:
                for defect in defects:
                    defect_frame = ctk.CTkFrame(section, fg_color="#4a2a2a", corner_radius=8)
                    defect_frame.pack(fill="x", pady=3)
                    
                    defect_label = ctk.CTkLabel(
                        defect_frame,
                        text=f"⚠️ {defect}",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#ff6666",
                        wraplength=600,
                        anchor="w",
                        justify="left"
                    )
                    defect_label.pack(anchor="w", padx=15, pady=8)
            
            # Visual indicators for severity
            severity_frame = ctk.CTkFrame(section, fg_color="#2a2a2a", corner_radius=10)
            severity_frame.pack(fill="x", pady=10)
            
            severity_title = ctk.CTkLabel(
                severity_frame,
                text="Severity Indicators:",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ffffff"
            )
            severity_title.pack(pady=(10, 5))
            
            # Create severity bars
            local = result['local_analysis']
            severity_data = [
                ("Brown/Rot Areas", local['brown_rot_percentage'], 
                 "Low" if local['brown_rot_percentage'] < 5 else "Medium" if local['brown_rot_percentage'] < 15 else "High"),
                ("Black Spots", local['black_spots_percentage'],
                 "Low" if local['black_spots_percentage'] < 2 else "Medium" if local['black_spots_percentage'] < 10 else "High")
            ]
            
            for name, value, level in severity_data:
                self.create_severity_indicator(severity_frame, name, value, level)
                
    def create_severity_indicator(self, parent, name, value, level):
        """Create visual severity indicator"""
        indicator_frame = ctk.CTkFrame(parent, fg_color="transparent")
        indicator_frame.pack(fill="x", padx=20, pady=5)
        
        # Label
        label = ctk.CTkLabel(
            indicator_frame,
            text=f"{name}: {value:.1f}%",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        )
        label.pack(side="left", padx=(0, 10))
        
        # Level indicator
        level_colors = {
            "Low": "#4CAF50",
            "Medium": "#FFA500",
            "High": "#FF0000"
        }
        
        level_label = ctk.CTkLabel(
            indicator_frame,
            text=level,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=level_colors.get(level, "#808080")
        )
        level_label.pack(side="left")
        
    def create_recommendations_section(self, result):
        """Create comprehensive recommendations section"""
        section = self.create_section("💡 Expert Recommendations", "#1a1a3a")
        
        # Immediate actions
        if result.get('action_required'):
            action_frame = ctk.CTkFrame(section, 
                                       fg_color="#ff6347" if 'discard' in result['action_required'].lower() else "#2a3a4a",
                                       corner_radius=10)
            action_frame.pack(fill="x", pady=5)
            
            action_title = ctk.CTkLabel(
                action_frame,
                text="🚨 Immediate Action:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffffff"
            )
            action_title.pack(pady=(10, 5))
            
            action_text = ctk.CTkLabel(
                action_frame,
                text=result['action_required'].upper(),
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ffffff"
            )
            action_text.pack(pady=(0, 10))
        
        # Prevention tips
        if result.get('prevention_tips'):
            prev_frame = ctk.CTkFrame(section, fg_color="#2a3a4a", corner_radius=10)
            prev_frame.pack(fill="x", pady=5)
            
            prev_title = ctk.CTkLabel(
                prev_frame,
                text="🛡️ Prevention Tips:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#4CAF50"
            )
            prev_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            for i, tip in enumerate(result['prevention_tips'], 1):
                tip_frame = ctk.CTkFrame(prev_frame, fg_color="transparent")
                tip_frame.pack(fill="x", padx=30, pady=3)
                
                number = ctk.CTkLabel(
                    tip_frame,
                    text=f"{i}.",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#4CAF50",
                    width=20
                )
                number.pack(side="left", anchor="n")
                
                tip_text = ctk.CTkLabel(
                    tip_frame,
                    text=tip,
                    font=ctk.CTkFont(size=12),
                    text_color="#cccccc",
                    wraplength=550,
                    anchor="w",
                    justify="left"
                )
                tip_text.pack(side="left", fill="x", expand=True)
                
            prev_frame.pack(pady=(0, 10))
            
        # Treatment suggestions
        self.add_treatment_suggestions(section, result)
        
    def add_treatment_suggestions(self, parent, result):
        """Add treatment suggestions based on condition"""
        condition = result.get('condition', '')
        
        treatments = {
            'FAIR': [
                "Monitor daily for changes",
                "Store in cool, dry place",
                "Use within 2-3 days",
                "Keep separate from other fruits"
            ],
            'POOR': [
                "Use immediately or freeze",
                "Cut away affected areas",
                "Consider cooking or juicing",
                "Do not store with healthy fruits"
            ],
            'INSECT': [
                "Remove from batch immediately",
                "Check all nearby fruits",
                "Clean storage area thoroughly",
                "Consider organic pest control"
            ]
        }
        
        # Find matching treatment
        treatment_list = None
        for key in treatments:
            if key in condition:
                treatment_list = treatments[key]
                break
                
        if treatment_list:
            treat_frame = ctk.CTkFrame(parent, fg_color="#3a3a2a", corner_radius=10)
            treat_frame.pack(fill="x", pady=5)
            
            treat_title = ctk.CTkLabel(
                treat_frame,
                text="🏥 Treatment Options:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FFA500"
            )
            treat_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            for treatment in treatment_list:
                treat_label = ctk.CTkLabel(
                    treat_frame,
                    text=f"→ {treatment}",
                    font=ctk.CTkFont(size=12),
                    text_color="#FFD700",
                    anchor="w"
                )
                treat_label.pack(anchor="w", padx=30, pady=2)
                
            treat_frame.pack(pady=(0, 10))
            
    def create_technical_section(self, local_analysis):
        """Create technical analysis section"""
        section = self.create_section("🔬 Technical Analysis", "#2a2a2a")
        
        # Create data visualization
        tech_frame = ctk.CTkFrame(section, fg_color="#333333", corner_radius=10)
        tech_frame.pack(fill="x", pady=5)
        
        # Metrics grid
        metrics = [
            ("Color Variance", f"{local_analysis['color_variance']:.2f}", 
             "Uniform" if local_analysis['color_variance'] < 20 else "Variable"),
            ("Texture Score", f"{local_analysis['texture_score']:.2f}",
             "Smooth" if local_analysis['texture_score'] < 30 else "Rough"),
            ("Shape Integrity", f"{local_analysis['shape_integrity']:.0f}%",
             "Good" if local_analysis['shape_integrity'] > 70 else "Irregular"),
            ("Overall Freshness", f"{local_analysis['freshness_score']:.0f}%",
             "Fresh" if local_analysis['freshness_score'] > 75 else "Declining")
        ]
        
        for i, (metric, value, status) in enumerate(metrics):
            metric_frame = ctk.CTkFrame(tech_frame, fg_color="transparent")
            metric_frame.pack(fill="x", padx=20, pady=8)
            
            # Metric name and value
            left_frame = ctk.CTkFrame(metric_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="x", expand=True)
            
            name_label = ctk.CTkLabel(
                left_frame,
                text=metric,
                font=ctk.CTkFont(size=12),
                text_color="#888888",
                anchor="w"
            )
            name_label.pack(anchor="w")
            
            value_label = ctk.CTkLabel(
                left_frame,
                text=value,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffffff",
                anchor="w"
            )
            value_label.pack(anchor="w")
            
            # Status
            status_color = "#4CAF50" if status in ["Uniform", "Smooth", "Good", "Fresh"] else "#FFA500"
            status_label = ctk.CTkLabel(
                metric_frame,
                text=status,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=status_color
            )
            status_label.pack(side="right", padx=20)
            
    def create_export_section(self):
        """Create export and save options"""
        section = self.create_section("💾 Export Options", "#1a1a1a")
        
        # Button frame
        button_frame = ctk.CTkFrame(section, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Export buttons
        buttons = [
            ("📄 Save Report", self.save_report, "#4CAF50"),
            ("📊 Export Data", self.export_data, "#2196F3"),
            ("📧 Email Report", self.email_report, "#FF9800"),
            ("🖨️ Print", self.print_report, "#9C27B0")
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                fg_color=color,
                hover_color=color,
                font=ctk.CTkFont(size=12, weight="bold"),
                height=35,
                width=140,
                corner_radius=8
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)
            
    def create_section(self, title, bg_color="#2a2a2a"):
        """Create a section with title"""
        section_frame = ctk.CTkFrame(self.detailed_scroll, fg_color=bg_color, corner_radius=15)
        section_frame.pack(fill="x", padx=5, pady=10)
        
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=(15, 10))
        
        return section_frame
        
    def show_defect_overlay(self):
        """Show enhanced defect overlay with annotations"""
        if self.current_image_cv2 is not None and self.analysis_result is not None:
            # Create annotated image
            overlay_image = self.create_enhanced_analysis_overlay(
                self.current_image_cv2, 
                self.analysis_result
            )
            
            # Display
            self.display_image(overlay_image)
            
    def create_enhanced_analysis_overlay(self, image, result):
        """Create enhanced overlay with detailed annotations"""
        overlay = image.copy()
        height, width = overlay.shape[:2]
        
        # Get analysis data
        local_analysis = result['local_analysis']
        condition = result.get('condition', '')
        
        # Apply defect highlighting
        hsv = cv2.cvtColor(overlay, cv2.COLOR_BGR2HSV)
        
        # Brown rot detection
        brown_lower = np.array([8, 50, 20])
        brown_upper = np.array([20, 255, 200])
        brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)
        
        # Black spots detection
        black_lower = np.array([0, 0, 0])
        black_upper = np.array([180, 255, 30])
        black_mask = cv2.inRange(hsv, black_lower, black_upper)
        
        # Apply colored overlays with transparency
        if local_analysis['brown_rot_percentage'] > 0:
            overlay[brown_mask > 0] = [0, 165, 255]  # Orange for brown
            
        if local_analysis['black_spots_percentage'] > 0:
            overlay[black_mask > 0] = [0, 0, 255]  # Red for black
            
        # Blend with original
        result_image = cv2.addWeighted(image, 0.6, overlay, 0.4, 0)
        
        # Add condition banner
        banner_height = 60
        banner = np.zeros((banner_height, width, 3), dtype=np.uint8)
        
        # Set banner color based on condition
        if 'BAD' in condition or 'DISCARD' in condition:
            banner[:] = [0, 0, 255]  # Red
            text_color = (255, 255, 255)
        elif 'POOR' in condition:
            banner[:] = [0, 100, 255]  # Orange-red
            text_color = (255, 255, 255)
        elif 'FAIR' in condition:
            banner[:] = [0, 165, 255]  # Orange
            text_color = (0, 0, 0)
        elif 'GOOD' in condition:
            banner[:] = [0, 255, 0]  # Green
            text_color = (0, 0, 0)
        elif 'EXCELLENT' in condition:
            banner[:] = [0, 255, 127]  # Bright green
            text_color = (0, 0, 0)
        else:
            banner[:] = [128, 128, 128]  # Gray
            text_color = (255, 255, 255)
            
        # Add text to banner
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = result['condition'].replace(' - ', ' | ')
        text_size = cv2.getTextSize(text, font, 0.8, 2)[0]
        text_x = (width - text_size[0]) // 2
        cv2.putText(banner, text, (text_x, 40), font, 0.8, text_color, 2)
        
        # Combine banner with result
        final_image = np.vstack([banner, result_image])
        
        # Add analysis info overlay
        info_y = banner_height + 30
        cv2.putText(final_image, "AI ANALYSIS OVERLAY", (10, info_y), 
                   font, 0.6, (255, 255, 255), 1)
        
        # Add legend
        legend_y = height + banner_height - 100
        legend_items = [
            ("Orange: Brown/Rot", (0, 165, 255)),
            ("Red: Black Spots", (0, 0, 255)),
            (f"Freshness: {local_analysis['freshness_score']:.0f}%", 
             (0, 255, 0) if local_analysis['freshness_score'] > 75 else (0, 165, 255))
        ]
        
        for i, (label, color) in enumerate(legend_items):
            y = legend_y + i * 25
            cv2.rectangle(final_image, (10, y-10), (30, y+5), color, -1)
            cv2.putText(final_image, label, (40, y), font, 0.5, (255, 255, 255), 1)
            
        return final_image
        
    def show_notification(self, message, type="info"):
        """Show temporary notification"""
        colors = {
            "success": "#4CAF50",
            "error": "#FF0000",
            "warning": "#FFA500",
            "info": "#2196F3"
        }
        
        notification = ctk.CTkFrame(self.root, 
                                   fg_color=colors.get(type, "#2196F3"),
                                   corner_radius=10,
                                   height=50)
        notification.place(relx=0.5, rely=0.95, anchor="s")
        
        label = ctk.CTkLabel(
            notification,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        label.pack(padx=20, pady=10)
        
        # Auto-hide after 3 seconds
        self.root.after(3000, notification.destroy)
        
    def show_loading(self, message="Loading..."):
        """Show loading overlay"""
        self.loading_overlay = ctk.CTkFrame(self.root, fg_color="#000000")
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        loading_label = ctk.CTkLabel(
            self.loading_overlay,
            text=message,
            font=ctk.CTkFont(size=20),
            text_color="#ffffff"
        )
        loading_label.place(relx=0.5, rely=0.5, anchor="center")
        
    def hide_loading(self):
        """Hide loading overlay"""
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.destroy()
            
    def add_to_history(self, result):
        """Add analysis to history"""
        history_entry = {
            'timestamp': datetime.now(),
            'fruit_type': result.get('fruit_type', 'Unknown'),
            'condition': result.get('condition', 'Unknown'),
            'confidence': result.get('confidence', 0),
            'image': self.current_image_cv2.copy() if self.current_image_cv2 is not None else None
        }
        
        self.history.append(history_entry)
        
        # Update history tab
        self.update_history_display()
        
    def update_history_display(self):
        """Update history tab display"""
        # Clear existing
        for widget in self.history_list.winfo_children():
            widget.destroy()
            
        if not self.history:
            return
            
        # Display history entries
        for i, entry in enumerate(reversed(self.history[-10:])):  # Show last 10
            entry_frame = ctk.CTkFrame(self.history_list, fg_color="#2a2a2a", corner_radius=10)
            entry_frame.pack(fill="x", padx=10, pady=5)
            
            # Timestamp
            time_label = ctk.CTkLabel(
                entry_frame,
                text=entry['timestamp'].strftime("%m/%d/%Y %I:%M %p"),
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            time_label.pack(anchor="w", padx=15, pady=(10, 5))
            
            # Details
            details_text = f"{entry['fruit_type']} - {entry['condition']} ({entry['confidence']:.0f}%)"
            details_label = ctk.CTkLabel(
                entry_frame,
                text=details_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffffff"
            )
            details_label.pack(anchor="w", padx=15, pady=(0, 10))
            
    def save_report(self):
        """Save comprehensive analysis report"""
        if self.analysis_result is None:
            self.show_notification("⚠️ No analysis to save", "warning")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ],
            initialfile=f"fruit_analysis_report_{timestamp}"
        )
        
        if filename:
            if filename.endswith('.png'):
                self.save_as_image(filename)
            else:
                self.save_as_pdf(filename)
            self.show_notification(f"✅ Report saved successfully!", "success")
            
    def save_as_image(self, filename):
        """Save report as high-quality image"""
        # Create report image
        width, height = 1400, 2000
        img = Image.new('RGB', (width, height), color='#0a0a0a')
        draw = ImageDraw.Draw(img)
        
        # Try to load better fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            header_font = ImageFont.truetype("arial.ttf", 32)
            body_font = ImageFont.truetype("arial.ttf", 24)
            small_font = ImageFont.truetype("arial.ttf", 18)
        except:
            # Fallback to default
            title_font = ImageFont.load_default()
            header_font = title_font
            body_font = title_font
            small_font = title_font
            
        y_offset = 50
        
        # Header
        draw.text((width//2, y_offset), "FRUIT QUALITY ANALYSIS REPORT", 
                 font=title_font, fill='white', anchor='mt')
        y_offset += 80
        
        # Date
        draw.text((width//2, y_offset), datetime.now().strftime("%B %d, %Y at %I:%M %p"), 
                 font=small_font, fill='#888888', anchor='mt')
        y_offset += 60
        
        # Main image
        if self.current_image_cv2 is not None:
            # Convert and resize
            image_rgb = cv2.cvtColor(self.current_image_cv2, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            pil_image.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
            # Center and paste
            x_offset = (width - pil_image.width) // 2
            img.paste(pil_image, (x_offset, y_offset))
            y_offset += pil_image.height + 40
        
        # Condition banner
        result = self.analysis_result
        condition = result['condition']
        
        # Draw condition box with color
        if 'BAD' in condition or 'DISCARD' in condition:
            box_color = '#FF0000'
        elif 'POOR' in condition:
            box_color = '#FF6347'
        elif 'FAIR' in condition:
            box_color = '#FFA500'
        elif 'GOOD' in condition:
            box_color = '#32CD32'
        elif 'EXCELLENT' in condition:
            box_color = '#00FF00'
        else:
            box_color = '#808080'
        
        # Draw colored rectangle
        draw.rectangle((100, y_offset, width-100, y_offset+100), 
                      fill=box_color, outline='white', width=3)
        draw.text((width//2, y_offset+50), condition, 
                 font=header_font, fill='white', anchor='mm')
        y_offset += 120
        
        # Key metrics
        draw.text((150, y_offset), "KEY METRICS", font=header_font, fill='#4CAF50')
        y_offset += 50
        
        metrics = [
            f"Fruit Type: {result.get('fruit_type', 'Unknown')}",
            f"AI Confidence: {result['confidence']:.0f}%",
            f"Freshness Score: {result['local_analysis']['freshness_score']:.0f}%",
            f"Decay Level: {result['local_analysis']['brown_rot_percentage']:.1f}%",
            f"Black Spots: {result['local_analysis']['black_spots_percentage']:.1f}%",
            f"Shape Integrity: {result['local_analysis']['shape_integrity']:.0f}%"
        ]
        
        for metric in metrics:
            draw.text((200, y_offset), f"• {metric}", font=body_font, fill='white')
            y_offset += 35
        
        # AI Analysis
        if result.get('gemini_analysis'):
            y_offset += 30
            draw.text((150, y_offset), "AI EXPERT ANALYSIS", font=header_font, fill='#4CAF50')
            y_offset += 50
            
            gemini = result['gemini_analysis']
            ai_details = [
                f"Ripeness: {gemini.get('ripeness', 'N/A')}",
                f"Safety Assessment: {gemini.get('safety_assessment', 'N/A')}",
                f"Storage Advice: {gemini.get('storage_advice', 'N/A')[:80]}..."
            ]
            
            for detail in ai_details:
                draw.text((200, y_offset), f"• {detail}", font=body_font, fill='white')
                y_offset += 35
        
        # Recommendations
        if result.get('prevention_tips'):
            y_offset += 30
            draw.text((150, y_offset), "RECOMMENDATIONS", font=header_font, fill='#4CAF50')
            y_offset += 50
            
            for i, tip in enumerate(result['prevention_tips'][:5], 1):
                # Wrap long text
                if len(tip) > 70:
                    tip = tip[:70] + "..."
                draw.text((200, y_offset), f"{i}. {tip}", font=body_font, fill='#90EE90')
                y_offset += 35
        
        # Footer
        y_offset = height - 100
        draw.text((width//2, y_offset), "Generated by AI-Powered Fruit Quality Analyzer", 
                 font=small_font, fill='#666666', anchor='mt')
        
        # Save
        img.save(filename, quality=95)
        
    def save_as_pdf(self, filename):
        """Save report as PDF (requires additional library)"""
        # For now, save as image and inform user
        png_filename = filename.replace('.pdf', '.png')
        self.save_as_image(png_filename)
        self.show_notification("📄 Saved as PNG (PDF support coming soon)", "info")
        
    def export_data(self):
        """Export analysis data as JSON"""
        if self.analysis_result is None:
            self.show_notification("⚠️ No data to export", "warning")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"fruit_analysis_data_{timestamp}.json"
        )
        
        if filename:
            # Prepare data for export
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'analysis_result': self.analysis_result,
                'metadata': {
                    'analyzer_version': '2.0',
                    'api_used': 'Gemini AI'
                }
            }
            
            # Remove image data from export
            if 'gemini_analysis' in export_data['analysis_result']:
                export_data['analysis_result']['gemini_analysis'].pop('image', None)
            
            # Save JSON
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=4)
                
            self.show_notification("✅ Data exported successfully!", "success")
            
    def email_report(self):
        """Placeholder for email functionality"""
        self.show_notification("📧 Email feature coming soon!", "info")
        
    def print_report(self):
        """Placeholder for print functionality"""
        self.show_notification("🖨️ Print feature coming soon!", "info")
        
    # Include all the analysis methods from original code
    def encode_image_base64(self, image):
        """Convert OpenCV image to base64 for Gemini API"""
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    
    def analyze_with_gemini(self, image):
        """Enhanced Gemini prompt for more accurate analysis"""
        try:
            image_base64 = self.encode_image_base64(image)
            
            # Enhanced prompt with specific focus on accuracy
            prompt = """
            You are an expert agricultural scientist and fruit quality inspector with 20+ years of experience.
            Analyze this fruit image with EXTREME precision and attention to detail.
            
            CRITICAL INSPECTION PROTOCOL:
            
            1. FRUIT IDENTIFICATION - Be 100% certain:
               - What exact type and variety of fruit is this?
               - Consider shape, color patterns, size, texture
            
            2. VISUAL QUALITY ASSESSMENT - Check every visible area:
               - Surface condition (smooth, rough, damaged)
               - Color uniformity and appropriateness for the fruit type
               - Any discoloration, dark spots, or unusual marks
               - Signs of physical damage (cuts, bruises, pressure marks)
            
            3. DISEASE & INFECTION DETECTION - Look very carefully for:
               - Fungal infections (fuzzy growth, mold spots)
               - Bacterial infections (wet spots, oozing)
               - Viral symptoms (ring spots, mottling)
               - Insect damage (holes, tunnels, bite marks)
               - Early rot signs (soft spots, brown areas)
            
            4. RIPENESS EVALUATION:
               - under-ripe: Hard, green tinge, no aroma
               - perfectly-ripe: Ideal color, slight give, sweet aroma
               - ripe: Full color, soft to touch, strong aroma
               - overripe: Very soft, wrinkled, overly sweet smell
               - rotten: Brown/black areas, foul odor, mushy
            
            5. QUALITY CLASSIFICATION - BE VERY STRICT:
               - EXCELLENT: Perfect specimen, no flaws, ideal ripeness
               - GOOD: Minor cosmetic imperfections only, fresh
               - FAIR: Some quality issues but still edible
               - POOR: Significant problems, use immediately
               - BAD: Inedible, health risk, must discard
               - INSECT_DAMAGED: Clear pest damage present
            
            6. HEALTH & SAFETY ASSESSMENT:
               - Is this fruit safe to eat?
               - Any toxins or harmful conditions?
               - Risk level for consumption
            
            7. DETAILED RECOMMENDATIONS:
               - Specific storage method for this exact condition
               - How many days it will last
               - Prevention tips for the issues found
               - Treatment options if applicable
            
            RESPOND IN THIS EXACT JSON FORMAT:
            {
                "fruit_type": "exact fruit name and variety if identifiable",
                "condition_category": "EXCELLENT/GOOD/FAIR/POOR/BAD/INSECT_DAMAGED",
                "confidence_score": 95,
                "detailed_analysis": "comprehensive description of what you observe",
                "defects_found": ["list every defect, disease, or issue found"],
                "disease_identification": "specific disease name if detected",
                "ripeness": "under-ripe/perfectly-ripe/ripe/overripe/rotten",
                "freshness_score": 85,
                "color_analysis": "description of color uniformity and health",
                "texture_analysis": "surface texture observations",
                "recommendations": "specific actions for this fruit",
                "key_observations": ["5 most important findings"],
                "safety_assessment": "safe/questionable/unsafe to eat",
                "health_risks": ["list any health risks if consumed"],
                "storage_method": "exact storage instructions",
                "shelf_life": "estimated days remaining",
                "prevention_tips": ["5 specific prevention methods"],
                "treatment_options": ["ways to salvage if applicable"],
                "disposal_method": "how to properly dispose if needed",
                "similar_fruits_affected": "should nearby fruits be checked?",
                "action_required": "consume immediately/use within X days/cook only/juice only/compost/discard"
            }
            
            BE EXTREMELY THOROUGH AND ACCURATE. This analysis could affect someone's health.
            If you see ANY concerning signs, classify appropriately and warn clearly.
            """

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            }

            response = requests.post(self.gemini_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    return self.parse_gemini_response(text_response)
            return None
                
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return None
    
    def parse_gemini_response(self, response_text):
        """Parse Gemini's response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                json_str = re.sub(r'```json|```', '', json_str).strip()
                gemini_analysis = json.loads(json_str)
                return gemini_analysis
            else:
                return self.create_fallback_analysis(response_text)
        except Exception as e:
            return self.create_fallback_analysis(response_text)
    
    def create_fallback_analysis(self, response_text):
        """Enhanced fallback analysis"""
        text_lower = response_text.lower()
        
        # More detailed condition detection
        conditions = {
            'BAD': ['rotten', 'spoiled', 'moldy', 'decay', 'inedible', 'toxic', 'dangerous'],
            'INSECT_DAMAGED': ['insect', 'bug', 'worm', 'pest', 'holes', 'tunnels', 'larvae'],
            'POOR': ['poor', 'bad quality', 'deteriorating', 'declining'],
            'FAIR': ['fair', 'moderate', 'acceptable', 'okay'],
            'GOOD': ['good', 'fresh', 'healthy', 'nice'],
            'EXCELLENT': ['excellent', 'perfect', 'pristine', 'ideal', 'premium']
        }
        
        condition = "FAIR"  # Default
        confidence = 60
        
        for cond, keywords in conditions.items():
            if any(keyword in text_lower for keyword in keywords):
                condition = cond
                confidence = 70 if cond in ['FAIR', 'POOR'] else 85
                break
        
        # Set action based on condition
        actions = {
            'BAD': "discard immediately",
            'INSECT_DAMAGED': "remove from batch",
            'POOR': "use within 24 hours",
            'FAIR': "use within 2-3 days",
            'GOOD': "consume normally",
            'EXCELLENT': "enjoy at your leisure"
        }
        
        prevention_tips = {
            'BAD': [
                "Store fruits in cool, dry place",
                "Check daily for spoilage",
                "Remove bad fruits immediately",
                "Improve air circulation",
                "Use within optimal timeframe"
            ],
            'INSECT_DAMAGED': [
                "Use protective mesh covers",
                "Apply organic pest deterrents",
                "Inspect fruits before storage",
                "Keep storage area clean",
                "Use pheromone traps"
            ],
            'default': [
                "Store at proper temperature",
                "Handle with care",
                "Check regularly",
                "Maintain cleanliness",
                "Use first-in-first-out rotation"
            ]
        }
        
        return {
            "fruit_type": "unknown fruit",
            "condition_category": condition,
            "confidence_score": confidence,
            "detailed_analysis": response_text[:200] + "...",
            "defects_found": [],
            "ripeness": "unknown",
            "freshness_score": 50,
            "recommendations": f"Based on visual analysis: {actions.get(condition, 'monitor closely')}",
            "key_observations": ["AI analysis incomplete - based on limited data"],
            "safety_assessment": "questionable" if condition in ['BAD', 'POOR'] else "likely safe",
            "prevention_tips": prevention_tips.get(condition, prevention_tips['default']),
            "storage_advice": "Store properly based on fruit type",
            "action_required": actions.get(condition, "check manually")
        }
    
    def perform_local_analysis(self, image):
        """Enhanced local computer vision analysis"""
        # Convert to different color spaces
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhanced analysis functions
        brown_rot_analysis = self.detect_brown_rot_enhanced(hsv, lab)
        black_spot_analysis = self.detect_black_spots_enhanced(hsv, gray)
        color_variance = self.analyze_color_uniformity(image)
        texture_analysis = self.analyze_texture_quality(image)
        contour_analysis = self.analyze_fruit_shape(image)
        freshness_score = self.calculate_freshness_score_enhanced(hsv, lab, image)
        
        return {
            'brown_rot_percentage': brown_rot_analysis,
            'black_spots_percentage': black_spot_analysis,
            'color_variance': color_variance,
            'texture_score': texture_analysis,
            'shape_integrity': contour_analysis,
            'freshness_score': freshness_score
        }
    
    def detect_brown_rot_enhanced(self, hsv_image, lab_image):
        """Enhanced brown rot detection using multiple color spaces"""
        # HSV detection
        brown_lower1 = np.array([8, 50, 20])
        brown_upper1 = np.array([20, 255, 200])
        brown_mask_hsv = cv2.inRange(hsv_image, brown_lower1, brown_upper1)
        
        # LAB detection for brown tones
        l_channel = lab_image[:,:,0]
        a_channel = lab_image[:,:,1]
        b_channel = lab_image[:,:,2]
        
        # Brown in LAB space
        brown_mask_lab = ((l_channel < 150) & 
                         (a_channel > 5) & (a_channel < 30) & 
                         (b_channel > 10) & (b_channel < 40)).astype(np.uint8) * 255
        
        # Combine masks
        combined_mask = cv2.bitwise_or(brown_mask_hsv, brown_mask_lab)
        
        # Morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        
        # Calculate percentage
        total_pixels = hsv_image.shape[0] * hsv_image.shape[1]
        brown_pixels = cv2.countNonZero(combined_mask)
        brown_percentage = (brown_pixels / total_pixels) * 100
        
        return round(brown_percentage, 2)
    
    def detect_black_spots_enhanced(self, hsv_image, gray_image):
        """Enhanced black spot detection"""
        # HSV detection for very dark areas
        black_lower = np.array([0, 0, 0])
        black_upper = np.array([180, 255, 50])
        black_mask_hsv = cv2.inRange(hsv_image, black_lower, black_upper)
        
        # Gray scale detection for dark spots
        _, black_mask_gray = cv2.threshold(gray_image, 30, 255, cv2.THRESH_BINARY_INV)
        
        # Combine masks
        combined_mask = cv2.bitwise_and(black_mask_hsv, black_mask_gray)
        
        # Remove small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours and filter by size
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Only count significant black spots
        significant_mask = np.zeros_like(combined_mask)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 20:  # Minimum area threshold
                cv2.drawContours(significant_mask, [contour], -1, 255, -1)
        
        # Calculate percentage
        total_pixels = hsv_image.shape[0] * hsv_image.shape[1]
        black_pixels = cv2.countNonZero(significant_mask)
        black_percentage = (black_pixels / total_pixels) * 100
        
        return round(black_percentage, 2)
    
    def analyze_color_uniformity(self, image):
        """Analyze color uniformity across the fruit"""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Calculate standard deviation in each channel
        l_std = np.std(lab[:,:,0])
        a_std = np.std(lab[:,:,1])
        b_std = np.std(lab[:,:,2])
        
        # Weighted average (L channel is more important for uniformity)
        color_variance = (l_std * 0.5 + a_std * 0.25 + b_std * 0.25)
        
        return round(color_variance, 2)
    
    def analyze_texture_quality(self, image):
        """Enhanced texture analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Multiple texture measures
        # 1. Laplacian variance (focus measure)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_score1 = laplacian.var()
        
        # 2. Gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        texture_score2 = np.mean(magnitude)
        
        # 3. Local Binary Pattern (simplified)
        kernel = np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]])
        texture_response = cv2.filter2D(gray, cv2.CV_32F, kernel)
        texture_score3 = np.mean(np.abs(texture_response))
        
        # Combine scores
        texture_score = (texture_score1 * 0.3 + texture_score2 * 0.3 + texture_score3 * 0.4)
        
        return round(min(100, texture_score), 2)
    
    def analyze_fruit_shape(self, image):
        """Analyze fruit shape integrity"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Preprocessing
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive threshold for better edge detection
        edges = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find largest contour (assumed to be the fruit)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate shape metrics
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Circularity measure
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # Convexity measure
                hull = cv2.convexHull(largest_contour)
                hull_area = cv2.contourArea(hull)
                convexity = area / hull_area if hull_area > 0 else 0
                
                # Combined shape score
                shape_score = (circularity * 0.6 + convexity * 0.4) * 100
                
                return min(100, round(shape_score, 2))
        
        return 50  # Default if no contour found
    
    def calculate_freshness_score_enhanced(self, hsv_image, lab_image, bgr_image):
        """Enhanced freshness calculation using multiple factors"""
        # Brightness from LAB
        brightness = np.mean(lab_image[:,:,0])
        brightness_score = min(100, (brightness / 255) * 120)
        
        # Saturation from HSV
        saturation = np.mean(hsv_image[:,:,1])
        saturation_score = min(100, (saturation / 255) * 110)
        
        # Color vibrancy from BGR
        b, g, r = cv2.split(bgr_image)
        color_vibrancy = np.std(r) + np.std(g) + np.std(b)
        vibrancy_score = min(100, color_vibrancy * 0.7)
        
        # Edge sharpness (indicates firmness)
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = (cv2.countNonZero(edges) / edges.size) * 100
        sharpness_score = min(100, edge_density * 10)
        
        # Combine scores with weights
        freshness = (
            brightness_score * 0.25 +
            saturation_score * 0.35 +
            vibrancy_score * 0.25 +
            sharpness_score * 0.15
        )
        
        return round(freshness, 2)
    
    def combine_analysis_results(self, gemini_result, local_analysis):
        """Combine AI and local analysis with Gemini priority"""
        if gemini_result:
            # Use Gemini as primary source
            ai_condition = gemini_result.get('condition_category', 'FAIR')
            ai_confidence = gemini_result.get('confidence_score', 50)
            
            # Enhanced condition mapping with emojis and clear messages
            condition_mapping = {
                'EXCELLENT': "🌟 EXCELLENT CONDITION - PREMIUM QUALITY",
                'GOOD': "✅ GOOD CONDITION - FRESH & HEALTHY",
                'FAIR': "⚠️ FAIR CONDITION - MONITOR CLOSELY", 
                'POOR': "⚠️ POOR CONDITION - USE IMMEDIATELY",
                'BAD': "🚫 BAD CONDITION - DO NOT CONSUME",
                'INSECT_DAMAGED': "🐛 INSECT DAMAGE - REMOVE FROM BATCH"
            }
            
            color_mapping = {
                'EXCELLENT': '#00ff00',
                'GOOD': '#32cd32',
                'FAIR': '#ffa500',
                'POOR': '#ff6347',
                'BAD': '#ff0000',
                'INSECT_DAMAGED': '#8b0000'
            }
            
            condition = condition_mapping.get(ai_condition, "❓ UNCLEAR - CHECK MANUALLY")
            color = color_mapping.get(ai_condition, '#808080')
            
            # Adjust confidence based on local analysis agreement
            local_bad_score = (local_analysis['brown_rot_percentage'] * 2.5 + 
                              local_analysis['black_spots_percentage'] * 3.5)
            
            if local_bad_score > 20 and ai_condition in ['EXCELLENT', 'GOOD']:
                # Local analysis disagrees with positive AI assessment
                confidence = max(ai_confidence - 15, 50)
                condition = "⚠️ CONFLICTING RESULTS - MANUAL CHECK NEEDED"
                color = '#ff6347'
            elif local_bad_score < 5 and ai_condition in ['BAD', 'POOR']:
                # Local analysis disagrees with negative AI assessment
                confidence = max(ai_confidence - 10, 60)
            else:
                # Agreement between AI and local
                confidence = min(ai_confidence + 5, 95)
                
            description = gemini_result.get('detailed_analysis', 'AI analysis completed')
            
        else:
            # Fallback to local analysis only
            local_bad_score = (local_analysis['brown_rot_percentage'] * 3 + 
                              local_analysis['black_spots_percentage'] * 4)
            freshness = local_analysis['freshness_score']
            
            if local_bad_score > 25 or freshness < 30:
                condition = "🚫 BAD CONDITION - DO NOT CONSUME"
                confidence = 75
                color = '#ff0000'
                description = "Significant decay and quality issues detected."
            elif local_bad_score > 15 or freshness < 50:
                condition = "⚠️ POOR CONDITION - USE IMMEDIATELY"
                confidence = 70
                color = '#ff6347'
                description = "Quality declining rapidly. Use within 24 hours."
            elif local_bad_score > 8 or freshness < 70:
                condition = "⚠️ FAIR CONDITION - MONITOR CLOSELY"
                confidence = 65
                color = '#ffa500'
                description = "Some quality concerns. Monitor daily."
            elif freshness > 85 and local_bad_score < 3:
                condition = "🌟 EXCELLENT CONDITION - PREMIUM QUALITY"
                confidence = 80
                color = '#00ff00'
                description = "Outstanding quality fruit."
            else:
                condition = "✅ GOOD CONDITION - FRESH & HEALTHY"
                confidence = 75
                color = '#32cd32'
                description = "Good quality fruit suitable for consumption."
        
        # Build comprehensive result
        result = {
            'condition': condition,
            'confidence': round(confidence, 1),
            'description': description,
            'color': color,
            'local_analysis': local_analysis,
            'gemini_analysis': gemini_result,
            'fruit_type': gemini_result.get('fruit_type', 'Unknown') if gemini_result else 'Unknown',
            'primary_source': 'AI Expert Analysis' if gemini_result else 'Computer Vision Analysis',
            'prevention_tips': gemini_result.get('prevention_tips', self.get_default_prevention_tips(condition)) if gemini_result else self.get_default_prevention_tips(condition),
            'action_required': gemini_result.get('action_required', self.get_default_action(condition)) if gemini_result else self.get_default_action(condition),
            'storage_advice': gemini_result.get('storage_method', 'Store in cool, dry place') if gemini_result else 'Store appropriately',
            'shelf_life': gemini_result.get('shelf_life', 'Check daily') if gemini_result else 'Monitor condition',
            'health_risks': gemini_result.get('health_risks', []) if gemini_result else [],
            'disease_identification': gemini_result.get('disease_identification', 'None detected') if gemini_result else 'Visual inspection needed'
        }
        
        return result
    
    def get_default_prevention_tips(self, condition):
        """Get condition-specific prevention tips"""
        tips = {
            'EXCELLENT': [
                "Continue current storage practices",
                "Maintain stable temperature",
                "Handle gently to preserve quality",
                "Keep away from ethylene producers",
                "Use within optimal timeframe"
            ],
            'GOOD': [
                "Store in proper conditions",
                "Check daily for changes",
                "Maintain good air circulation",
                "Keep dry to prevent mold",
                "Separate from overripe fruits"
            ],
            'FAIR': [
                "Improve storage conditions immediately",
                "Increase monitoring frequency",
                "Consider refrigeration if applicable",
                "Remove any damaged portions",
                "Use within 2-3 days maximum"
            ],
            'POOR': [
                "Use immediately or process",
                "Separate from healthy fruits",
                "Consider cooking or juicing",
                "Check for spread to other fruits",
                "Improve storage for future"
            ],
            'BAD': [
                "Dispose of properly in compost",
                "Sanitize storage area",
                "Check all nearby fruits",
                "Review storage practices",
                "Purchase fresher produce"
            ],
            'INSECT': [
                "Inspect all fruits carefully",
                "Use protective coverings",
                "Apply organic deterrents",
                "Clean storage thoroughly",
                "Consider professional pest control"
            ]
        }
        
        # Find matching tips
        for key in tips:
            if key in condition:
                return tips[key]
        
        return tips.get('FAIR', [])  # Default tips
    
    def get_default_action(self, condition):
        """Get default action based on condition"""
        actions = {
            'EXCELLENT': "Enjoy at your convenience - peak quality",
            'GOOD': "Consume normally - good for several days",
            'FAIR': "Use within 2-3 days - quality declining",
            'POOR': "Use immediately - process if needed",
            'BAD': "Discard immediately - health risk",
            'INSECT': "Remove from batch - check others"
        }
        
        for key in actions:
            if key in condition:
                return actions[key]
                
        return "Monitor condition closely"
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function to run the GUI application"""
    print("\n" + "="*80)
    print("🍎 === ADVANCED FRUIT HEALTH ANALYZER PRO === 🍊")
    print("🤖 AI-Powered Disease Detection & Quality Analysis")
    print("="*80 + "\n")
    
    # Check dependencies
    try:
        import customtkinter
    except ImportError:
        print("⚠️ Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "customtkinter", "opencv-python", "pillow", "requests", "numpy"])
        import customtkinter
    
    # Your Gemini API key
    API_KEY = "AIzaSyDkC-9tWhMn6XPkkvHwmighHUfY7FrN8wA"
    
    # Create and run the GUI
    print("🚀 Launching Advanced Fruit Health Analyzer...")
    print("✨ Features: Real-time analysis, Disease detection, Prevention tips")
    print("📸 Ready to analyze fruit quality and health!\n")
    
    app = ModernFruitAnalyzerGUI(API_KEY)
    app.run()

if __name__ == '__main__':
    main()
