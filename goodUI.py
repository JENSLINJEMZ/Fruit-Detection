import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter
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
        self.root.title("🍎 AI-Powered Fruit Quality Analyzer")
        self.root.geometry("1400x900")
        
        # Center window on screen
        self.center_window()
        
        # Variables
        self.current_image = None
        self.current_image_cv2 = None
        self.analysis_result = None
        
        # Setup UI
        self.setup_ui()
        
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
        # Main container
        self.main_container = ctk.CTkFrame(self.root, fg_color="#0a0a0a")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Content area with two columns
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="#1a1a1a")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left column - Image and controls
        self.left_column = ctk.CTkFrame(self.content_frame, fg_color="#1a1a1a", width=600)
        self.left_column.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.left_column.pack_propagate(False)
        
        # Right column - Analysis results
        self.right_column = ctk.CTkFrame(self.content_frame, fg_color="#1a1a1a", width=700)
        self.right_column.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        self.right_column.pack_propagate(False)
        
        # Setup left column
        self.setup_left_column()
        
        # Setup right column
        self.setup_right_column()
        
    def create_header(self):
        """Create professional header"""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="#0f0f0f", height=80)
        header_frame.pack(fill="x", padx=10, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Title with gradient effect
        title_label = ctk.CTkLabel(
            header_frame,
            text="🍎 AI-POWERED FRUIT QUALITY ANALYSIS SYSTEM 🍊",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=(10, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text=f"Advanced Computer Vision & AI Analysis | {datetime.now().strftime('%B %d, %Y')}",
            font=ctk.CTkFont(family="Arial", size=14),
            text_color="#888888"
        )
        subtitle_label.pack()
        
    def setup_left_column(self):
        """Setup left column with image display and controls"""
        # Image display frame
        image_frame = ctk.CTkFrame(self.left_column, fg_color="#2a2a2a", corner_radius=15)
        image_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Image label
        self.image_label = ctk.CTkLabel(
            image_frame,
            text="📷 No Image Loaded\n\nClick 'Capture from Camera' or 'Load from URL'",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        )
        self.image_label.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Control buttons frame
        controls_frame = ctk.CTkFrame(self.left_column, fg_color="#1a1a1a", height=150)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        controls_frame.pack_propagate(False)
        
        # Buttons with modern styling
        button_style = {
            "font": ctk.CTkFont(size=16, weight="bold"),
            "height": 45,
            "corner_radius": 10,
            "hover_color": "#2a7a2a"
        }
        
        # Camera button
        self.camera_btn = ctk.CTkButton(
            controls_frame,
            text="📷 Capture from Camera",
            command=self.capture_from_camera,
            fg_color="#1e8e3e",
            **button_style
        )
        self.camera_btn.pack(fill="x", padx=20, pady=(10, 5))
        
        # URL button
        self.url_btn = ctk.CTkButton(
            controls_frame,
            text="🌐 Load from URL",
            command=self.load_from_url,
            fg_color="#1976d2",
            **button_style
        )
        self.url_btn.pack(fill="x", padx=20, pady=5)
        
        # Analyze button (initially disabled)
        self.analyze_btn = ctk.CTkButton(
            controls_frame,
            text="🔬 Analyze Fruit Quality",
            command=self.analyze_image,
            fg_color="#f57c00",
            state="disabled",
            **button_style
        )
        self.analyze_btn.pack(fill="x", padx=20, pady=5)
        
    def setup_right_column(self):
        """Setup right column for analysis results"""
        # Results header
        header_frame = ctk.CTkFrame(self.right_column, fg_color="#2a2a2a", height=60, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        self.results_title = ctk.CTkLabel(
            header_frame,
            text="📊 Analysis Results",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff"
        )
        self.results_title.pack(pady=15)
        
        # Scrollable results area
        self.results_scroll = ctk.CTkScrollableFrame(
            self.right_column,
            fg_color="#1a1a1a",
            corner_radius=10
        )
        self.results_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial message
        self.no_results_label = ctk.CTkLabel(
            self.results_scroll,
            text="🔍 No analysis performed yet\n\nLoad an image and click 'Analyze' to begin",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        )
        self.no_results_label.pack(pady=50)
        
    def capture_from_camera(self):
        """Optimized camera capture"""
        camera_window = ctk.CTkToplevel(self.root)
        camera_window.title("📷 Capture Fruit Image")
        camera_window.geometry("800x600")
        
        # Camera frame
        camera_frame = ctk.CTkFrame(camera_window)
        camera_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = ctk.CTkLabel(
            camera_frame,
            text="Position the fruit in the center and press SPACE to capture",
            font=ctk.CTkFont(size=16)
        )
        instructions.pack(pady=10)
        
        # Video label
        video_label = tk.Label(camera_frame, bg="#1a1a1a")
        video_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Start camera in separate thread
        self.camera_active = True
        self.captured_frame = None
        
        def camera_loop():
            if os.name == 'nt':  # Windows
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                messagebox.showerror("Error", "Could not open camera")
                camera_window.destroy()
                return
            
            # Optimize camera settings
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            while self.camera_active:
                ret, frame = cap.read()
                if ret:
                    # Add overlay guides
                    frame_display = frame.copy()
                    height, width = frame_display.shape[:2]
                    center_x, center_y = width // 2, height // 2
                    
                    # Draw center circle
                    cv2.circle(frame_display, (center_x, center_y), 100, (0, 255, 0), 2)
                    
                    # Draw rectangle
                    rect_size = 150
                    cv2.rectangle(frame_display, 
                                 (center_x - rect_size, center_y - rect_size), 
                                 (center_x + rect_size, center_y + rect_size), 
                                 (0, 255, 0), 2)
                    
                    # Convert to PIL Image
                    cv2image = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(cv2image)
                    img = img.resize((640, 480), Image.Resampling.LANCZOS)
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    # Update video label
                    video_label.configure(image=imgtk)
                    video_label.image = imgtk
                    
                    # Store current frame
                    self.current_frame = frame
                    
                # Small delay
                cv2.waitKey(30)
            
            cap.release()
        
        # Capture function
        def capture_image(event=None):
            if hasattr(self, 'current_frame'):
                self.captured_frame = self.current_frame.copy()
                self.camera_active = False
                camera_window.destroy()
                
                # Update main window with captured image
                self.current_image_cv2 = self.captured_frame
                self.display_image(self.captured_frame)
                self.analyze_btn.configure(state="normal")
                messagebox.showinfo("Success", "Image captured successfully!")
        
        # Bind space key
        camera_window.bind('<space>', capture_image)
        
        # Capture button
        capture_btn = ctk.CTkButton(
            camera_frame,
            text="📸 CAPTURE (SPACE)",
            command=capture_image,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50,
            fg_color="#1e8e3e"
        )
        capture_btn.pack(pady=10)
        
        # Start camera thread
        camera_thread = threading.Thread(target=camera_loop, daemon=True)
        camera_thread.start()
        
        # Handle window close
        def on_closing():
            self.camera_active = False
            camera_window.destroy()
        
        camera_window.protocol("WM_DELETE_WINDOW", on_closing)
        
    def load_from_url(self):
        """Load image from URL with dialog"""
        dialog = ctk.CTkInputDialog(
            text="Enter image URL:",
            title="Load Image from URL"
        )
        url = dialog.get_input()
        
        if url:
            try:
                # Show loading indicator
                self.image_label.configure(text="⏳ Loading image from URL...")
                self.root.update()
                
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    if image is not None:
                        self.current_image_cv2 = image
                        self.display_image(image)
                        self.analyze_btn.configure(state="normal")
                        messagebox.showinfo("Success", "Image loaded successfully!")
                    else:
                        messagebox.showerror("Error", "Could not decode image from URL")
                else:
                    messagebox.showerror("Error", f"Failed to download image. Status code: {response.status_code}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error loading image: {str(e)}")
                self.image_label.configure(text="❌ Failed to load image")
                
    def display_image(self, cv2_image):
        """Display image in the GUI"""
        # Convert CV2 to PIL
        image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Resize to fit
        display_size = (500, 400)
        pil_image.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # Update label
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo  # Keep reference
        
    def analyze_image(self):
        """Perform comprehensive analysis"""
        if self.current_image_cv2 is None:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        # Disable analyze button
        self.analyze_btn.configure(state="disabled", text="🔄 Analyzing...")
        
        # Clear previous results
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        # Show progress
        progress_label = ctk.CTkLabel(
            self.results_scroll,
            text="⏳ Performing comprehensive analysis...",
            font=ctk.CTkFont(size=16)
        )
        progress_label.pack(pady=20)
        
        # Progress bar
        progress_bar = ctk.CTkProgressBar(self.results_scroll, width=400)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        # Perform analysis in thread
        def analysis_thread():
            try:
                # Local analysis
                progress_bar.set(0.3)
                local_results = self.perform_local_analysis(self.current_image_cv2)
                
                # Gemini AI analysis
                progress_bar.set(0.6)
                gemini_results = self.analyze_with_gemini(self.current_image_cv2)
                
                # Combine results
                progress_bar.set(0.9)
                final_result = self.combine_analysis_results(gemini_results, local_results)
                
                progress_bar.set(1.0)
                
                # Update UI in main thread
                self.root.after(100, lambda: self.display_analysis_results(final_result))
                
            except Exception as e:
                self.root.after(100, lambda: messagebox.showerror("Error", f"Analysis failed: {str(e)}"))
            finally:
                self.root.after(100, lambda: self.analyze_btn.configure(
                    state="normal", 
                    text="🔬 Analyze Fruit Quality"
                ))
        
        # Start analysis thread
        thread = threading.Thread(target=analysis_thread, daemon=True)
        thread.start()
        
    def display_analysis_results(self, result):
        """Display analysis results in modern UI"""
        # Clear scroll frame
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        # Store result
        self.analysis_result = result
        
        # Determine theme based on condition
        is_bad = 'BAD' in result['condition'] or 'DISCARD' in result['condition']
        is_excellent = 'EXCELLENT' in result['condition']
        
        if is_bad:
            theme_color = "#ff4444"
            bg_color = "#3a1515"
        elif is_excellent:
            theme_color = "#44ff44"
            bg_color = "#153a15"
        else:
            theme_color = "#4488ff"
            bg_color = "#15253a"
        
        # Main condition card
        condition_card = ctk.CTkFrame(self.results_scroll, fg_color=bg_color, corner_radius=15)
        condition_card.pack(fill="x", padx=10, pady=10)
        
        # Condition text
        condition_label = ctk.CTkLabel(
            condition_card,
            text=result['condition'],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff"
        )
        condition_label.pack(pady=(20, 10))
        
        # Confidence score with circular progress
        confidence_frame = ctk.CTkFrame(condition_card, fg_color="transparent")
        confidence_frame.pack(pady=10)
        
        # Create circular progress using Canvas
        canvas = tk.Canvas(confidence_frame, width=150, height=150, bg=bg_color, highlightthickness=0)
        canvas.pack()
        
        # Draw circular progress
        confidence = result['confidence']
        angle = int(360 * (confidence / 100))
        
        # Background circle
        canvas.create_oval(25, 25, 125, 125, outline="#333333", width=10)
        
        # Progress arc
        canvas.create_arc(25, 25, 125, 125, start=90, extent=-angle, 
                         outline=theme_color, width=10, style="arc")
        
        # Center text
        canvas.create_text(75, 75, text=f"{confidence:.0f}%", 
                          font=("Arial", 28, "bold"), fill="white")
        canvas.create_text(75, 100, text="Confidence", 
                          font=("Arial", 12), fill="#888888")
        
        # Fruit type
        fruit_label = ctk.CTkLabel(
            condition_card,
            text=f"🍎 {result['fruit_type'].upper()}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        fruit_label.pack(pady=(10, 20))
        
        # Action required (if bad)
        if 'action_required' in result:
            action_frame = ctk.CTkFrame(self.results_scroll, fg_color="#ff0000", corner_radius=10)
            action_frame.pack(fill="x", padx=10, pady=5)
            
            action_label = ctk.CTkLabel(
                action_frame,
                text=f"⚠️ {result['action_required'].upper()} ⚠️",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#ffffff"
            )
            action_label.pack(pady=15)
        
        # Quality metrics card
        metrics_card = ctk.CTkFrame(self.results_scroll, fg_color="#2a2a2a", corner_radius=15)
        metrics_card.pack(fill="x", padx=10, pady=10)
        
        metrics_title = ctk.CTkLabel(
            metrics_card,
            text="📊 Quality Metrics",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        metrics_title.pack(pady=(15, 10))
        
        # Metrics data
        local = result['local_analysis']
        metrics_data = [
            ("Brown/Rot Areas", local['brown_rot_percentage'], "#8B4513", True),
            ("Black Spots", local['black_spots_percentage'], "#333333", True),
            ("Freshness Score", local['freshness_score'], "#00ff00", False),
            ("Shape Quality", local['shape_integrity'], "#00bfff", False)
        ]
        
        for metric_name, value, color, is_defect in metrics_data:
            metric_frame = ctk.CTkFrame(metrics_card, fg_color="transparent")
            metric_frame.pack(fill="x", padx=20, pady=5)
            
            # Label
            label = ctk.CTkLabel(
                metric_frame,
                text=metric_name,
                font=ctk.CTkFont(size=14),
                text_color="#cccccc",
                width=150,
                anchor="w"
            )
            label.pack(side="left", padx=(0, 10))
            
            # Progress bar
            progress = ctk.CTkProgressBar(
                metric_frame,
                width=200,
                height=20,
                progress_color=color if not (is_defect and value > 5) else "#ff0000"
            )
            progress.pack(side="left", padx=10)
            progress.set(value / 100)
            
            # Value label
            value_label = ctk.CTkLabel(
                metric_frame,
                text=f"{value:.1f}%",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=color if not (is_defect and value > 5) else "#ff6666"
            )
            value_label.pack(side="left", padx=10)
        
        # AI Analysis details
        if result.get('gemini_analysis'):
            ai_card = ctk.CTkFrame(self.results_scroll, fg_color="#1a2e1a", corner_radius=15)
            ai_card.pack(fill="x", padx=10, pady=10)
            
            ai_title = ctk.CTkLabel(
                ai_card,
                text="🤖 AI Analysis Details",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#ffffff"
            )
            ai_title.pack(pady=(15, 10))
            
            gemini = result['gemini_analysis']
            
            # Details grid
            details_frame = ctk.CTkFrame(ai_card, fg_color="transparent")
            details_frame.pack(fill="x", padx=20, pady=10)
            
            details = [
                ("Ripeness:", gemini.get('ripeness', 'N/A')),
                ("Safety:", gemini.get('safety_assessment', 'N/A')),
                ("Storage:", gemini.get('storage_advice', 'N/A')[:50] + "..." if len(gemini.get('storage_advice', '')) > 50 else gemini.get('storage_advice', 'N/A'))
            ]
            
            for label, value in details:
                detail_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                detail_frame.pack(fill="x", pady=3)
                
                label_widget = ctk.CTkLabel(
                    detail_frame,
                    text=label,
                    font=ctk.CTkFont(size=14),
                    text_color="#888888",
                    width=100,
                    anchor="w"
                )
                label_widget.pack(side="left")
                
                # Determine color
                if 'unsafe' in str(value).lower():
                    value_color = "#ff6666"
                elif 'safe' in str(value).lower():
                    value_color = "#66ff66"
                else:
                    value_color = "#ffffff"
                
                value_widget = ctk.CTkLabel(
                    detail_frame,
                    text=str(value),
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=value_color,
                    anchor="w"
                )
                value_widget.pack(side="left", padx=10)
            
            # Defects found
            if gemini.get('defects_found'):
                defects_frame = ctk.CTkFrame(ai_card, fg_color="#3a1515", corner_radius=10)
                defects_frame.pack(fill="x", padx=20, pady=10)
                
                defects_title = ctk.CTkLabel(
                    defects_frame,
                    text="⚠️ Defects Found:",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#ff6666"
                )
                defects_title.pack(anchor="w", padx=10, pady=(10, 5))
                
                for defect in gemini['defects_found'][:3]:
                    defect_label = ctk.CTkLabel(
                        defects_frame,
                        text=f"• {defect}",
                        font=ctk.CTkFont(size=12),
                        text_color="#ffaaaa",
                        anchor="w"
                    )
                    defect_label.pack(anchor="w", padx=20, pady=2)
        
        # Prevention tips
        if result.get('prevention_tips'):
            tips_card = ctk.CTkFrame(self.results_scroll, fg_color="#2a2a3a", corner_radius=15)
            tips_card.pack(fill="x", padx=10, pady=10)
            
            tips_title = ctk.CTkLabel(
                tips_card,
                text="💡 Prevention Tips",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#ffffff"
            )
            tips_title.pack(pady=(15, 10))
            
            for tip in result['prevention_tips'][:4]:
                tip_label = ctk.CTkLabel(
                    tips_card,
                    text=f"• {tip}",
                    font=ctk.CTkFont(size=13),
                    text_color="#aaaaff",
                    anchor="w",
                    wraplength=600
                )
                tip_label.pack(anchor="w", padx=30, pady=3)
            
            tips_card.pack(pady=(0, 20))  # Extra padding at bottom
        
        # Save report button
        save_btn = ctk.CTkButton(
            self.results_scroll,
            text="💾 Save Analysis Report",
            command=self.save_report,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            fg_color="#4CAF50",
            hover_color="#45a049",
            corner_radius=10
        )
        save_btn.pack(pady=20)
        
        # Show defect overlay
        self.show_defect_overlay()
        
    def show_defect_overlay(self):
        """Show defect overlay on the image"""
        if self.current_image_cv2 is not None and self.analysis_result is not None:
            # Create overlay
            overlay_image = self.create_enhanced_analysis_overlay(
                self.current_image_cv2, 
                self.analysis_result['local_analysis']
            )
            
            # Convert and display
            self.display_image(overlay_image)
            
    def save_report(self):
        """Save analysis report as image"""
        if self.analysis_result is None:
            messagebox.showwarning("Warning", "No analysis to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=f"fruit_analysis_{timestamp}.png"
        )
        
        if filename:
            # Create report image
            self.create_report_image(filename)
            messagebox.showinfo("Success", f"Report saved to {filename}")
            
    def create_report_image(self, filename):
        """Create a professional report image"""
        # Create a large image
        width, height = 1200, 1600
        img = Image.new('RGB', (width, height), color='#0a0a0a')
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 36)
            header_font = ImageFont.truetype("arial.ttf", 24)
            body_font = ImageFont.truetype("arial.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        y_offset = 50
        
        # Title
        title = "AI-POWERED FRUIT QUALITY ANALYSIS REPORT"
        draw.text((width//2, y_offset), title, font=title_font, fill='white', anchor='mt')
        y_offset += 80
        
        # Date
        date_text = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        draw.text((width//2, y_offset), date_text, font=body_font, fill='#888888', anchor='mt')
        y_offset += 60
        
        # Main image
        if self.current_image_cv2 is not None:
            image_rgb = cv2.cvtColor(self.current_image_cv2, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            pil_image.thumbnail((500, 400), Image.Resampling.LANCZOS)
            
            # Paste centered
            x_offset = (width - pil_image.width) // 2
            img.paste(pil_image, (x_offset, y_offset))
            y_offset += pil_image.height + 40
        
        # Results
        result = self.analysis_result
        
        # Condition box
        condition_bg = '#2a0000' if 'BAD' in result['condition'] else '#002a00'
        draw.rectangle((100, y_offset, width-100, y_offset+80), fill=condition_bg, outline=result['color'], width=3)
        draw.text((width//2, y_offset+40), result['condition'], font=header_font, fill='white', anchor='mm')
        y_offset += 100
        
        # Details
        details = [
            f"Fruit Type: {result['fruit_type']}",
            f"Confidence: {result['confidence']:.0f}%",
            f"Freshness: {result['local_analysis']['freshness_score']:.0f}%",
            f"Action: {result.get('action_required', 'Monitor')}",
        ]
        
        for detail in details:
            draw.text((150, y_offset), detail, font=body_font, fill='white')
            y_offset += 35
        
        # Save
        img.save(filename, quality=95)
    
    # Include all the analysis methods from the original code
    def encode_image_base64(self, image):
        """Convert OpenCV image to base64 for Gemini API"""
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    
    def analyze_with_gemini(self, image):
        """Analyze image using Gemini REST API with enhanced prompt"""
        try:
            # Convert image to base64
            image_base64 = self.encode_image_base64(image)
            
            # Enhanced detailed prompt for careful analysis
            prompt = """
            CRITICAL FRUIT QUALITY INSPECTION - ANALYZE VERY CAREFULLY
            
            You are a professional fruit quality inspector. Examine this fruit image with extreme attention to detail.
            
            INSPECTION CHECKLIST - Check each point carefully:
            
            🔍 VISUAL EXAMINATION:
            1. **Fruit Identification**: What specific type of fruit is this? (apple, orange, banana, etc.)
            2. **Surface Condition**: Examine the entire surface for ANY imperfections
            3. **Color Assessment**: Is the color natural and healthy for this fruit type?
            4. **Texture Analysis**: Is the skin smooth, wrinkled, or damaged?
            
            🚨 DEFECT DETECTION (Look very carefully):
            - Brown spots or discoloration (sign of rot/decay)
            - Black spots or dark patches (mold, severe damage)
            - Holes or punctures (insect damage, physical damage)
            - Soft spots or indentations (bruising, overripeness)
            - Wrinkled or shriveled skin (aging, dehydration)
            - Unusual growths or fuzzy patches (mold)
            - Bite marks or chewed areas (pest damage)
            
            🍎 QUALITY CLASSIFICATION:
            - EXCELLENT: Perfect condition, no defects, optimal ripeness
            - GOOD: Minor imperfections, still fresh and edible
            - FAIR: Some defects present, edible but declining quality
            - POOR: Significant defects, questionable for consumption
            - BAD: Severely damaged, rotten, or unsafe to eat
            - INSECT_DAMAGED: Clear signs of pest damage or holes
            
            ⚠️ IMPORTANT: Be very strict in your assessment. If you see ANY signs of decay, rot, mold, or damage, classify accordingly.
            
            🛡️ PREVENTION & REMEDIES:
            Based on the condition, provide:
            - Prevention tips (how to prevent this condition)
            - Storage recommendations
            - Whether to discard or if it can be saved
            - Any treatment suggestions
            
            RESPOND IN THIS EXACT JSON FORMAT:
            {
                "fruit_type": "exact fruit name",
                "condition_category": "EXCELLENT/GOOD/FAIR/POOR/BAD/INSECT_DAMAGED",
                "confidence_score": 90,
                "detailed_analysis": "Very detailed description of what you observe",
                "defects_found": ["list all defects you see"],
                "ripeness": "under-ripe/perfectly-ripe/ripe/overripe/rotten",
                "freshness_score": 85,
                "recommendations": "specific recommendation for this fruit",
                "key_observations": ["list 3-5 key things you noticed"],
                "safety_assessment": "safe/questionable/unsafe to eat",
                "prevention_tips": ["how to prevent this condition in future"],
                "storage_advice": "best storage method for this fruit",
                "action_required": "consume immediately/use within days/discard/remove from batch"
            }
            
            EXAMINE THE IMAGE VERY CAREFULLY - Don't miss any details!
            """

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            },
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
        """Parse Gemini's response and extract structured data"""
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
        """Create structured analysis when JSON parsing fails"""
        text_lower = response_text.lower()

        if any(word in text_lower for word in ['rotten', 'spoiled', 'moldy', 'severely damaged', 'bad condition', 'unsafe', 'decay']):
            condition = "BAD"
            confidence = 85
            action = "discard"
            prevention = ["Store in cool, dry place", "Check fruits regularly", "Remove damaged fruits immediately"]
        elif any(word in text_lower for word in ['insect', 'holes', 'bite marks', 'pest damage', 'chewed', 'puncture']):
            condition = "INSECT_DAMAGED"
            confidence = 80
            action = "remove from batch"
            prevention = ["Use mesh covers", "Regular inspection", "Natural pest repellents"]
        elif any(word in text_lower for word in ['excellent', 'perfect', 'pristine', 'optimal']):
            condition = "EXCELLENT"
            confidence = 90
            action = "consume at leisure"
            prevention = ["Continue current storage", "Maintain temperature"]
        elif any(word in text_lower for word in ['good condition', 'fresh', 'healthy', 'quality']):
            condition = "GOOD"
            confidence = 85
            action = "consume normally"
            prevention = ["Monitor regularly", "Proper ventilation"]
        elif any(word in text_lower for word in ['fair', 'moderate', 'declining', 'some defects']):
            condition = "FAIR"
            confidence = 70
            action = "use within days"
            prevention = ["Improve storage conditions", "Use sooner"]
        else:
            condition = "POOR"
            confidence = 60
            action = "consume immediately"
            prevention = ["Better selection at purchase", "Improved storage"]

        return {
            "fruit_type": "unknown",
            "condition_category": condition,
            "confidence_score": confidence,
            "detailed_analysis": response_text,
            "defects_found": [],
            "ripeness": "unknown",
            "freshness_score": confidence,
            "recommendations": "Based on AI analysis",
            "key_observations": [response_text[:100] + "..."],
            "safety_assessment": "questionable",
            "prevention_tips": prevention,
            "storage_advice": "Store properly",
            "action_required": action
        }

    def perform_local_analysis(self, image):
        """Local computer vision analysis for fruit quality"""
        # Convert to different color spaces
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Perform various analyses
        brown_rot_analysis = self.detect_brown_rot(hsv)
        black_spot_analysis = self.detect_black_spots(hsv)
        color_variance = self.analyze_color_uniformity(image)
        texture_analysis = self.analyze_texture_quality(image)
        contour_analysis = self.analyze_fruit_shape(image)
        freshness_score = self.calculate_freshness_score(hsv, lab)
        
        return {
            'brown_rot_percentage': brown_rot_analysis,
            'black_spots_percentage': black_spot_analysis,
            'color_variance': color_variance,
            'texture_score': texture_analysis,
            'shape_integrity': contour_analysis,
            'freshness_score': freshness_score
        }
    
    def detect_brown_rot(self, hsv_image):
        """Detect brown/rotten areas"""
        brown_lower1 = np.array([8, 50, 20])
        brown_upper1 = np.array([20, 255, 200])
        brown_mask1 = cv2.inRange(hsv_image, brown_lower1, brown_upper1)
        
        brown_lower2 = np.array([10, 30, 10])
        brown_upper2 = np.array([25, 255, 100])
        brown_mask2 = cv2.inRange(hsv_image, brown_lower2, brown_upper2)
        
        combined_brown = cv2.bitwise_or(brown_mask1, brown_mask2)
        total_pixels = hsv_image.shape[0] * hsv_image.shape[1]
        brown_pixels = cv2.countNonZero(combined_brown)
        brown_percentage = (brown_pixels / total_pixels) * 100
        
        return round(brown_percentage, 2)
    
    def detect_black_spots(self, hsv_image):
        """Detect black spots (severe damage/mold)"""
        black_lower = np.array([0, 0, 0])
        black_upper = np.array([180, 255, 30])
        black_mask = cv2.inRange(hsv_image, black_lower, black_upper)
        
        kernel = np.ones((3,3), np.uint8)
        black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_CLOSE, kernel)
        
        total_pixels = hsv_image.shape[0] * hsv_image.shape[1]
        black_pixels = cv2.countNonZero(black_mask)
        black_percentage = (black_pixels / total_pixels) * 100
        
        return round(black_percentage, 2)
    
    def analyze_color_uniformity(self, image):
        """Analyze color uniformity"""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_std = np.std(lab[:,:,0])
        a_std = np.std(lab[:,:,1])
        b_std = np.std(lab[:,:,2])
        color_variance = (l_std + a_std + b_std) / 3
        return round(color_variance, 2)
    
    def analyze_texture_quality(self, image):
        """Analyze texture quality"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernel = np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]])
        texture_response = cv2.filter2D(gray, cv2.CV_32F, kernel)
        texture_score = np.mean(np.abs(texture_response))
        return round(texture_score, 2)
    
    def analyze_fruit_shape(self, image):
        """Analyze fruit shape integrity"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                return min(100, round(circularity * 100, 2))
        return 50
    
    def calculate_freshness_score(self, hsv_image, lab_image):
        """Calculate overall freshness score"""
        brightness = np.mean(lab_image[:,:,0])
        saturation = np.mean(hsv_image[:,:,1])
        brightness_score = min(100, (brightness / 255) * 100)
        saturation_score = min(100, (saturation / 255) * 100)
        freshness = (brightness_score + saturation_score) / 2
        return round(freshness, 2)
    
    def combine_analysis_results(self, gemini_result, local_analysis):
        """Combine Gemini AI and local analysis results - PRIORITIZE GEMINI"""
        return self.make_final_decision_gemini_priority(gemini_result, local_analysis)
    
    def make_final_decision_gemini_priority(self, gemini_result, local_analysis):
        """Make final decision PRIORITIZING Gemini AI result"""
        
        if gemini_result:
            ai_condition = gemini_result.get('condition_category', 'FAIR')
            ai_confidence = gemini_result.get('confidence_score', 50)
            
            condition_mapping = {
                'EXCELLENT': "✅ EXCELLENT CONDITION",
                'GOOD': "✅ GOOD CONDITION",
                'FAIR': "⚠️ FAIR CONDITION", 
                'POOR': "⚠️ POOR CONDITION",
                'BAD': "🚫 BAD CONDITION - DISCARD",
                'INSECT_DAMAGED': "🐛 INSECT DAMAGE - REMOVE"
            }
            
            color_mapping = {
                'EXCELLENT': '#00ff00',
                'GOOD': '#90ee90',
                'FAIR': '#ffa500',
                'POOR': '#ff6347',
                'BAD': '#ff0000',
                'INSECT_DAMAGED': '#8b0000'
            }
            
            condition = condition_mapping.get(ai_condition, "❓ UNCLEAR")
            color = color_mapping.get(ai_condition, '#808080')
            
            local_bad_score = (local_analysis['brown_rot_percentage'] * 2 + 
                              local_analysis['black_spots_percentage'] * 3)
            
            if local_bad_score > 15 and ai_condition in ['EXCELLENT', 'GOOD']:
                confidence = max(ai_confidence - 10, 60)
            else:
                confidence = ai_confidence
                
            description = gemini_result.get('detailed_analysis', 'AI analysis completed')
            if len(description) > 200:
                description = description[:200] + "..."
                
        else:
            # Fallback to local analysis if Gemini fails
            local_bad_score = (local_analysis['brown_rot_percentage'] * 3 + 
                              local_analysis['black_spots_percentage'] * 4)
            
            if local_bad_score > 20:
                condition = "🚫 BAD CONDITION - DISCARD"
                confidence = 75
                color = '#ff0000'
                description = "Local analysis detected significant defects. This fruit should be discarded."
            elif local_bad_score > 10:
                condition = "⚠️ FAIR CONDITION"
                confidence = 65
                color = '#ffa500'
                description = "Local analysis shows some quality issues. Use soon."
            else:
                condition = "✅ GOOD CONDITION"
                confidence = local_analysis['freshness_score']
                color = '#90ee90'
                description = "Local analysis shows good quality"
        
        result = {
            'condition': condition,
            'confidence': round(confidence, 1),
            'description': description,
            'color': color,
            'local_analysis': local_analysis,
            'gemini_analysis': gemini_result,
            'fruit_type': gemini_result.get('fruit_type', 'unknown') if gemini_result else 'unknown',
            'primary_source': 'Advanced AI' if gemini_result else 'Local Analysis',
            'prevention_tips': gemini_result.get('prevention_tips', []) if gemini_result else [],
            'action_required': gemini_result.get('action_required', 'unknown') if gemini_result else 'check manually',
            'storage_advice': gemini_result.get('storage_advice', '') if gemini_result else ''
        }
        
        return result
    
    def create_enhanced_analysis_overlay(self, image, local_analysis):
        """Create enhanced analysis overlay with better visualization"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        overlay = image.copy()
        
        # Brown rot detection
        brown_lower1 = np.array([8, 50, 20])
        brown_upper1 = np.array([20, 255, 200])
        brown_mask1 = cv2.inRange(hsv, brown_lower1, brown_upper1)
        
        # Black spots detection
        black_lower = np.array([0, 0, 0])
        black_upper = np.array([180, 255, 30])
        black_mask = cv2.inRange(hsv, black_lower, black_upper)
        
        # Apply colored overlays
        overlay[brown_mask1 > 0] = [0, 165, 255]  # Orange for brown areas (BGR)
        overlay[black_mask > 0] = [0, 0, 255]      # Red for black spots (BGR)
        
        # Blend with original
        result = cv2.addWeighted(image, 0.6, overlay, 0.4, 0)
        
        # Add text overlay
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(result, "Defect Analysis", (10, 30), font, 1, (255, 255, 255), 2)
        cv2.putText(result, f"Brown: {local_analysis['brown_rot_percentage']:.1f}%", 
                   (10, 60), font, 0.7, (0, 165, 255), 2)
        cv2.putText(result, f"Black: {local_analysis['black_spots_percentage']:.1f}%", 
                   (10, 90), font, 0.7, (0, 0, 255), 2)
        
        return result
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function to run the GUI application"""
    print("\n" + "="*80)
    print("🍎 === ADVANCED FRUIT QUALITY ANALYSIS SYSTEM === 🍊")
    print("🤖 Powered by State-of-the-Art AI & Computer Vision")
    print("="*80 + "\n")
    
    # Check if customtkinter is installed
    try:
        import customtkinter
    except ImportError:
        print("⚠️ CustomTkinter not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "customtkinter"])
        import customtkinter
    
    # Your Gemini API key
    API_KEY = "AIzaSyDkC-9tWhMn6XPkkvHwmighHUfY7FrN8wA"
    
    # Create and run the GUI
    print("🚀 Launching Modern GUI Interface...")
    app = ModernFruitAnalyzerGUI(API_KEY)
    app.run()

if __name__ == '__main__':
    main()
