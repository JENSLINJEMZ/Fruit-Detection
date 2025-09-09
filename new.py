import requests
import cv2
import numpy as np
import os
import tempfile
from datetime import datetime
import base64
import json
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Wedge
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import matplotlib.patheffects as path_effects
from matplotlib import cm
import textwrap
from matplotlib.gridspec import GridSpec
import matplotlib.animation as animation
from matplotlib.backends.backend_agg import FigureCanvasAgg
import threading
import time

# Set style for better visuals
plt.style.use('dark_background')

class GeminiRestFruitAnalyzer:
    def __init__(self, api_key):
        self.API_KEY = api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.API_KEY
        }
        
    def capture_image_from_camera(self):
        """Optimized camera capture with faster initialization"""
        print("🎥 Starting camera... Press SPACE to capture, ESC to exit")
        
        # Try different camera backends for faster initialization
        # DirectShow (Windows) is typically faster
        if os.name == 'nt':  # Windows
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:  # Linux/Mac
            cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            # Fallback to default if DirectShow fails
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ Error: Could not open camera")
                return None
        
        # Set buffer size to reduce lag
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Set lower resolution initially for faster startup
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Warm up camera with a few frames
        print("📸 Warming up camera...")
        for _ in range(5):
            cap.read()
        
        # Now set to desired resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Set FPS for smoother preview
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        captured_image = None
        frame_count = 0
        
        print("✅ Camera ready! Position the fruit and press SPACE to capture")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Failed to read frame")
                break
            
            # Only process every other frame for better performance
            frame_count += 1
            if frame_count % 2 == 0:
                # Enhanced preview
                frame_display = frame.copy()
                
                # Add brightness adjustment for better visibility
                frame_display = cv2.convertScaleAbs(frame_display, alpha=1.1, beta=10)
                
                # Guide overlay
                height, width = frame_display.shape[:2]
                center_x, center_y = width // 2, height // 2
                
                # Draw guides
                cv2.putText(frame_display, "Press SPACE to capture, ESC to exit", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(frame_display, "Position fruit in center with good lighting", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Center guide circle
                cv2.circle(frame_display, (center_x, center_y), 150, (0, 255, 0), 2)
                
                # Focus rectangle
                rect_size = 250
                cv2.rectangle(frame_display, 
                             (center_x - rect_size, center_y - rect_size), 
                             (center_x + rect_size, center_y + rect_size), 
                             (0, 255, 0), 2)
                
                # Crosshair
                cv2.line(frame_display, (center_x - 30, center_y), (center_x + 30, center_y), (0, 255, 0), 1)
                cv2.line(frame_display, (center_x, center_y - 30), (center_x, center_y + 30), (0, 255, 0), 1)
                
                # Show FPS
                cv2.putText(frame_display, f"Ready to capture", 
                           (width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('🍎 Fruit Quality Analyzer - Camera', frame_display)
            
            # Check for key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space pressed
                captured_image = frame.copy()
                print("✅ Image captured!")
                
                # Show captured image briefly
                cv2.putText(frame, "CAPTURED!", (width//2 - 100, height//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
                cv2.imshow('🍎 Fruit Quality Analyzer - Camera', frame)
                cv2.waitKey(500)
                break
                
            elif key == 27:  # ESC pressed
                print("❌ Capture cancelled")
                break
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        
        return captured_image

    def load_image_from_url(self, image_url):
        """Load image from URL"""
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if image is not None:
                    print("✅ Image loaded from URL.")
                    return image
                else:
                    print("❌ Could not decode image from the URL data.")
                    return None
            else:
                print(f"❌ Failed to download image. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error loading image from URL: {e}")
            return None

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

            print("🤖 Analyzing with Advanced AI (Enhanced Detection)...")
            response = requests.post(self.gemini_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    return self.parse_gemini_response(text_response)
                else:
                    print("❌ No candidates in Gemini response")
                    return None
            else:
                print(f"❌ Gemini API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Gemini API Error: {e}")
            return None
    
    def parse_gemini_response(self, response_text):
        """Parse Gemini's response and extract structured data"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Clean up the JSON string
                json_str = re.sub(r'```json|```', '', json_str).strip()
                gemini_analysis = json.loads(json_str)
                return gemini_analysis
            else:
                # If no JSON found, create structured response from text
                return self.create_fallback_analysis(response_text)
        except Exception as e:
            print(f"⚠️ Could not parse JSON response: {e}")
            return self.create_fallback_analysis(response_text)
    
    def create_fallback_analysis(self, response_text):
        """Create structured analysis when JSON parsing fails"""
        text_lower = response_text.lower()
        
        # More detailed condition detection based on keywords
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
        print("🔬 Performing local computer vision analysis...")
        
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
        print("\n🔍 Combining AI and Computer Vision analysis...")
        
        if gemini_result:
            print("🤖 AI Analysis:")
            print(f"   • Fruit Type: {gemini_result.get('fruit_type', 'unknown')}")
            print(f"   • Condition: {gemini_result.get('condition_category', 'unknown')}")
            print(f"   • AI Confidence: {gemini_result.get('confidence_score', 0)}%")
            print(f"   • Ripeness: {gemini_result.get('ripeness', 'unknown')}")
            print(f"   • Action: {gemini_result.get('action_required', 'unknown')}")
            print(f"   • Safety: {gemini_result.get('safety_assessment', 'unknown')}")
        
        print(f"\n🔬 Local Analysis Results:")
        print(f"   • Brown/Rot areas: {local_analysis['brown_rot_percentage']}%")
        print(f"   • Black spots: {local_analysis['black_spots_percentage']}%")
        print(f"   • Freshness score: {local_analysis['freshness_score']}%")
        
        return self.make_final_decision_gemini_priority(gemini_result, local_analysis)
    
    def make_final_decision_gemini_priority(self, gemini_result, local_analysis):
        """Make final decision PRIORITIZING Gemini AI result"""
        
        if gemini_result:
            # GEMINI AI RESULT IS PRIMARY - Use it directly with minor local adjustments
            ai_condition = gemini_result.get('condition_category', 'FAIR')
            ai_confidence = gemini_result.get('confidence_score', 50)
            
            # Map Gemini conditions to display format
            condition_mapping = {
                'EXCELLENT': "✅ EXCELLENT CONDITION",
                'GOOD': "✅ GOOD CONDITION",
                'FAIR': "⚠️ FAIR CONDITION", 
                'POOR': "⚠️ POOR CONDITION",
                'BAD': "🚫 BAD CONDITION - DISCARD",
                'INSECT_DAMAGED': "🐛 INSECT DAMAGE - REMOVE"
            }
            
            color_mapping = {
                'EXCELLENT': '#00ff00',  # Bright green
                'GOOD': '#90ee90',       # Light green
                'FAIR': '#ffa500',       # Orange
                'POOR': '#ff6347',       # Tomato
                'BAD': '#ff0000',        # Red
                'INSECT_DAMAGED': '#8b0000'  # Dark red
            }
            
            condition = condition_mapping.get(ai_condition, "❓ UNCLEAR")
            color = color_mapping.get(ai_condition, '#808080')
            
            # Use Gemini's confidence with small local adjustment
            local_bad_score = (local_analysis['brown_rot_percentage'] * 2 + 
                              local_analysis['black_spots_percentage'] * 3)
            
            # Only adjust confidence slightly based on local analysis
            if local_bad_score > 15 and ai_condition in ['EXCELLENT', 'GOOD']:
                confidence = max(ai_confidence - 10, 60)  # Reduce confidence if local detects issues
            else:
                confidence = ai_confidence
                
            # Create description from Gemini analysis
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
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        overlay = image_rgb.copy()
        
        # Brown rot detection with different intensity
        brown_lower1 = np.array([8, 50, 20])
        brown_upper1 = np.array([20, 255, 200])
        brown_mask1 = cv2.inRange(hsv, brown_lower1, brown_upper1)
        
        # Black spots detection
        black_lower = np.array([0, 0, 0])
        black_upper = np.array([180, 255, 30])
        black_mask = cv2.inRange(hsv, black_lower, black_upper)
        
        # Apply colored overlays
        overlay[brown_mask1 > 0] = [255, 165, 0]  # Orange for brown areas
        overlay[black_mask > 0] = [255, 0, 0]    # Red for black spots
        
        # Blend with original
        result = cv2.addWeighted(image_rgb, 0.6, overlay, 0.4, 0)
        return result

    def create_professional_dashboard(self, image, result):
        """Create an ultra-professional dashboard with proper spacing"""
        # Create figure with proper DPI for crisp text
        fig = plt.figure(figsize=(22, 14), dpi=100)
        fig.patch.set_facecolor('#0a0a0a')
        
        # Add save functionality
        def on_key_press(event):
            if event.key == 's' or event.key == 'S':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"fruit_analysis_report_{timestamp}.png"
                plt.savefig(filename, dpi=300, bbox_inches='tight', 
                           facecolor='#0a0a0a', edgecolor='none')
                print(f"📊 Report saved as: {filename}")
        
        fig.canvas.mpl_connect('key_press_event', on_key_press)
        
        # Determine overall theme based on condition
        is_bad = 'BAD' in result['condition'] or 'DISCARD' in result['condition'] or 'INSECT' in result['condition']
        is_excellent = 'EXCELLENT' in result['condition']
        
        # Theme colors
        if is_bad:
            theme_color = '#ff0000'
            bg_color = '#2a0000'
            accent_color = '#ff6666'
        elif is_excellent:
            theme_color = '#00ff00'
            bg_color = '#002a00'
            accent_color = '#66ff66'
        else:
            theme_color = '#00bfff'
            bg_color = '#001a2a'
            accent_color = '#66d9ff'
        
        # MAIN HEADER
        header_height = 0.08
        fig.text(0.5, 0.96, '🍎 AI-POWERED FRUIT QUALITY ANALYSIS SYSTEM 🍊', 
                ha='center', va='center', fontsize=28, fontweight='bold', color='white',
                bbox=dict(boxstyle="round,pad=0.8", facecolor=bg_color, edgecolor=theme_color, linewidth=3))
        
        fig.text(0.5, 0.93, f'📅 Analysis Date: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', 
                ha='center', va='center', fontsize=12, color='#cccccc')
        
        # Create main content area with proper spacing
        content_top = 0.88
        
        # === SECTION 1: IMAGES ROW ===
        img_width = 0.28
        img_height = 0.25
        img_y = content_top - img_height - 0.02
        
        # Original Image
        ax1 = fig.add_axes([0.05, img_y, img_width, img_height])
        ax1.set_facecolor('#1a1a1a')
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        ax1.imshow(image_rgb, aspect='auto')
        ax1.set_title('📸 ORIGINAL IMAGE', fontsize=14, fontweight='bold', color='white', pad=10)
        ax1.axis('off')
        
        # Add border
        for spine in ['top', 'right', 'bottom', 'left']:
            ax1.spines[spine].set_visible(True)
            ax1.spines[spine].set_color(theme_color)
            ax1.spines[spine].set_linewidth(3)
        
        # Status Panel (Center)
        status_x = 0.36
        ax2 = fig.add_axes([status_x, img_y, img_width, img_height])
        ax2.set_facecolor(bg_color)
        ax2.axis('off')
        
        # Main Condition Display
        condition_text = result['condition'].split(' - ')[0]
        action_text = result['condition'].split(' - ')[1] if ' - ' in result['condition'] else ''
        
        # Large status text
        ax2.text(0.5, 0.75, condition_text, ha='center', va='center', 
                fontsize=20, fontweight='bold', color='white',
                transform=ax2.transAxes,
                bbox=dict(boxstyle="round,pad=0.5", facecolor=result['color'], alpha=0.8))
        
        # Confidence Score
        ax2.text(0.5, 0.5, f"{result['confidence']:.0f}%", 
                ha='center', va='center', fontsize=48, fontweight='bold', 
                color=result['color'], transform=ax2.transAxes)
        
        ax2.text(0.5, 0.35, 'CONFIDENCE SCORE', 
                ha='center', va='center', fontsize=12, 
                color='#888888', transform=ax2.transAxes)
        
        # Fruit Type
        ax2.text(0.5, 0.15, f"🍎 {result['fruit_type'].upper()}", 
                ha='center', va='center', fontsize=16, fontweight='bold',
                color='white', transform=ax2.transAxes)
        
        # Action if bad
        if action_text:
            ax2.text(0.5, 0.05, f"⚠️ {action_text} ⚠️", 
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color='red', transform=ax2.transAxes)
        
        # Defect Analysis Image
        ax3 = fig.add_axes([0.67, img_y, img_width, img_height])
        ax3.set_facecolor('#1a1a1a')
        overlay_image = self.create_enhanced_analysis_overlay(image, result['local_analysis'])
        ax3.imshow(overlay_image, aspect='auto')
        ax3.set_title('🔍 DEFECT ANALYSIS', fontsize=14, fontweight='bold', color='white', pad=10)
        ax3.axis('off')
        
        # === SECTION 2: METRICS AND DETAILS ===
        metrics_y = img_y - 0.32
        panel_height = 0.25
        panel_width = 0.28
        
        # Quality Metrics Panel
        ax4 = fig.add_axes([0.05, metrics_y, panel_width, panel_height])
        ax4.set_facecolor('#1a1a2e')
        ax4.axis('off')
        
        # Title
        ax4.text(0.5, 0.92, '📊 QUALITY METRICS', fontsize=14, fontweight='bold',
                ha='center', color='white', transform=ax4.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=theme_color, alpha=0.3))
        
        # Metrics with bars
        local = result['local_analysis']
        metrics_data = [
            ('Brown/Rot Areas', local['brown_rot_percentage'], '#8B4513', True),
            ('Black Spots', local['black_spots_percentage'], '#333333', True),
            ('Freshness Score', local['freshness_score'], '#00ff00', False),
            ('Shape Quality', local['shape_integrity'], '#00bfff', False)
        ]
        
        y_pos = 0.75
        for metric_name, value, default_color, is_defect in metrics_data:
            # Determine color
            if is_defect and value > 5:
                bar_color = '#ff0000'
                text_color = '#ff6666'
            else:
                bar_color = default_color
                text_color = 'white'
            
            # Label
            ax4.text(0.05, y_pos, metric_name, fontsize=10, color=text_color, 
                    va='center', transform=ax4.transAxes)
            
            # Background bar
            bar_bg = Rectangle((0.05, y_pos - 0.035), 0.6, 0.03,
                             facecolor='#333333', alpha=0.5, transform=ax4.transAxes)
            ax4.add_patch(bar_bg)
            
            # Value bar
            bar_length = 0.6 * (value / 100)
            value_bar = Rectangle((0.05, y_pos - 0.035), bar_length, 0.03,
                                facecolor=bar_color, alpha=0.8, transform=ax4.transAxes)
            ax4.add_patch(value_bar)
            
            # Value text
            ax4.text(0.7, y_pos, f'{value:.1f}%', fontsize=10, fontweight='bold',
                    color=text_color, va='center', transform=ax4.transAxes)
            
            y_pos -= 0.15
        
        # AI Analysis Details
        ax5 = fig.add_axes([0.36, metrics_y, panel_width, panel_height])
        ax5.set_facecolor('#1a2e1a')
        ax5.axis('off')
        
        ax5.text(0.5, 0.92, '🤖 AI ANALYSIS', fontsize=14, fontweight='bold',
                ha='center', color='white', transform=ax5.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=theme_color, alpha=0.3))
        
        if result['gemini_analysis']:
            gemini = result['gemini_analysis']
            
            y_pos = 0.75
            details = [
                ('Condition:', gemini.get('condition_category', 'N/A')),
                ('Ripeness:', gemini.get('ripeness', 'N/A')),
                ('Safety:', gemini.get('safety_assessment', 'N/A')),
                ('Action:', gemini.get('action_required', 'N/A'))
            ]
            
            for label, value in details:
                # Determine color
                if 'unsafe' in str(value).lower() or 'discard' in str(value).lower():
                    value_color = '#ff6666'
                elif 'safe' in str(value).lower():
                    value_color = '#66ff66'
                else:
                    value_color = 'white'
                
                ax5.text(0.1, y_pos, label, fontsize=11, color='#cccccc',
                        transform=ax5.transAxes)
                ax5.text(0.4, y_pos, str(value).upper(), fontsize=11, 
                        fontweight='bold', color=value_color, transform=ax5.transAxes)
                y_pos -= 0.15
            
            # Defects
            defects = gemini.get('defects_found', [])
            if defects:
                ax5.text(0.1, 0.2, 'Defects:', fontsize=10, color='red',
                    fontweight='bold', transform=ax5.transAxes)
                ax5.text(0.1, 0.1, f"• {defects[0] if defects else 'None'}",
                    fontsize=9, color='#ff9999', transform=ax5.transAxes)
        
        # Prevention & Action Panel
        ax6 = fig.add_axes([0.67, metrics_y, panel_width, panel_height])
        ax6.set_facecolor('#2e1a1a' if is_bad else '#1a1a2e')
        ax6.axis('off')
        
        title = '🚨 IMMEDIATE ACTION' if is_bad else '💡 RECOMMENDATIONS'
        title_color = '#ff0000' if is_bad else theme_color
        
        ax6.text(0.5, 0.92, title, fontsize=14, fontweight='bold',
                ha='center', color='white', transform=ax6.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=title_color, alpha=0.3))
        
        # Action Box
        if is_bad:
            action_box = FancyBboxPatch((0.1, 0.65), 0.8, 0.15, 
                                      boxstyle="round,pad=0.02", 
                                      facecolor='darkred', alpha=0.8,
                                      edgecolor='red', linewidth=3,
                                      transform=ax6.transAxes)
            ax6.add_patch(action_box)
            
            ax6.text(0.5, 0.725, result.get('action_required', 'DISCARD').upper(), 
                    fontsize=12, fontweight='bold', ha='center', 
                    color='white', transform=ax6.transAxes)
        
        # Prevention Tips
        tips = result.get('prevention_tips', []) or self.get_default_prevention_tips(result['condition'])
        y_pos = 0.55 if is_bad else 0.75
        
        ax6.text(0.1, y_pos, '🛡️ Prevention:', fontsize=11, fontweight='bold',
                color='white', transform=ax6.transAxes)
        y_pos -= 0.1
        
        for i, tip in enumerate(tips[:3]):
            # Truncate long tips
            if len(tip) > 35:
                tip = tip[:35] + '...'
            ax6.text(0.1, y_pos, f"• {tip}", fontsize=9, 
                    color='#ffaaaa' if is_bad else '#aaffaa',
                    transform=ax6.transAxes)
            y_pos -= 0.08
        
        # === SECTION 3: HEALTH STATUS ===
        health_y = 0.1
        health_width = 0.9
        health_height = 0.15
        
        ax7 = fig.add_axes([0.05, health_y, health_width, health_height])
        ax7.set_facecolor('#0d0d0d')
        ax7.axis('off')
        
        # Health Status Bar
        if is_bad:
            # Bad fruit - Red theme
            status_color = '#ff0000'
            status_bg = '#330000'
            status_text = '⚠️ CRITICAL - UNSAFE TO CONSUME - DISCARD IMMEDIATELY ⚠️'
            
            # Create pulsing effect with multiple rectangles
            for i in range(3):
                warning_box = Rectangle((0.02 + i*0.01, 0.3 - i*0.05), 
                                      0.96 - i*0.02, 0.4 + i*0.1,
                                      facecolor=status_color, alpha=0.2 - i*0.05,
                                      transform=ax7.transAxes)
                ax7.add_patch(warning_box)
            
            # Main warning box
            main_box = FancyBboxPatch((0.05, 0.35), 0.9, 0.3, 
                                    boxstyle="round,pad=0.02", 
                                    facecolor=status_bg, 
                                    edgecolor=status_color, linewidth=4,
                                    transform=ax7.transAxes)
            ax7.add_patch(main_box)
            
            # Warning text
            ax7.text(0.5, 0.5, status_text, fontsize=18, fontweight='bold',
                    ha='center', va='center', color='white', 
                    transform=ax7.transAxes)
            
            # Action icons
            icons = ['🚫', '☣️', '🗑️']
            labels = ['UNSAFE', 'HAZARD', 'DISPOSE']
            x_positions = [0.25, 0.5, 0.75]
            
            for icon, label, x_pos in zip(icons, labels, x_positions):
                ax7.text(x_pos, 0.15, icon, fontsize=24, ha='center',
                        transform=ax7.transAxes)
                ax7.text(x_pos, 0.05, label, fontsize=10, ha='center',
                        color='red', fontweight='bold', transform=ax7.transAxes)
        
        elif 'POOR' in result['condition']:
            # Poor condition - Orange theme
            status_color = '#ffa500'
            status_text = '⚠️ POOR QUALITY - USE IMMEDIATELY OR DISCARD'
            
            warning_box = FancyBboxPatch((0.1, 0.35), 0.8, 0.3, 
                                       boxstyle="round,pad=0.02", 
                                       facecolor='#332200', 
                                       edgecolor=status_color, linewidth=3,
                                       transform=ax7.transAxes)
            ax7.add_patch(warning_box)
            
            ax7.text(0.5, 0.5, status_text, fontsize=16, fontweight='bold',
                    ha='center', va='center', color=status_color, 
                    transform=ax7.transAxes)
        
        else:
            # Good condition - Green theme
            status_color = '#00ff00'
            status_text = '✅ SAFE TO CONSUME - GOOD QUALITY'
            
            safe_box = FancyBboxPatch((0.1, 0.35), 0.8, 0.3, 
                                    boxstyle="round,pad=0.02", 
                                    facecolor='#003300', 
                                    edgecolor=status_color, linewidth=3,
                                    transform=ax7.transAxes)
            ax7.add_patch(safe_box)
            
            ax7.text(0.5, 0.5, status_text, fontsize=16, fontweight='bold',
                    ha='center', va='center', color='white', 
                    transform=ax7.transAxes)
            
            # Positive icons
            icons = ['✅', '🍽️', '📦']
            labels = ['SAFE', 'EDIBLE', 'STORE']
            x_positions = [0.25, 0.5, 0.75]
            
            for icon, label, x_pos in zip(icons, labels, x_positions):
                ax7.text(x_pos, 0.15, icon, fontsize=24, ha='center',
                        transform=ax7.transAxes)
                ax7.text(x_pos, 0.05, label, fontsize=10, ha='center',
                        color='green', fontweight='bold', transform=ax7.transAxes)
        
        # Footer
        fig.text(0.5, 0.04, "💾 Press 'S' to Save Report  |  🤖 Powered by Advanced AI & Computer Vision", 
                ha='center', va='center', fontsize=14, fontweight='bold', color='white',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#1a1a1a', edgecolor=theme_color))
        
        # Quality Badge
        quality_badge = self.get_quality_badge(result['condition'])
        fig.text(0.5, 0.01, quality_badge, ha='center', va='center', 
                fontsize=12, color=theme_color, style='italic')
        
        plt.tight_layout()
        plt.show()
    
    def get_default_prevention_tips(self, condition):
        """Get default prevention tips based on condition"""
        if 'BAD' in condition or 'DISCARD' in condition:
            return [
                "Check fruits daily",
                "Store in cool, dry place",
                "Remove damaged fruits",
                "Use proper ventilation"
            ]
        elif 'INSECT' in condition:
            return [
                "Use mesh covers",
                "Apply organic repellents",
                "Clean storage area",
                "Regular inspection"
            ]
        elif 'FAIR' in condition or 'POOR' in condition:
            return [
                "Use within 2-3 days",
                "Refrigerate if possible",
                "Separate from others",
                "Monitor daily"
            ]
        else:
            return [
                "Maintain temperature",
                "Handle gently",
                "Rotate stock",
                "Check regularly"
            ]
    
    def get_quality_badge(self, condition):
        """Get quality badge based on condition"""
        if 'EXCELLENT' in condition:
            return '⭐⭐⭐⭐⭐ Premium Quality Fruit'
        elif 'GOOD' in condition:
            return '⭐⭐⭐⭐ High Quality Fruit'
        elif 'FAIR' in condition:
            return '⭐⭐⭐ Acceptable Quality'
        elif 'POOR' in condition:
            return '⭐⭐ Low Quality - Use Soon'
        else:
            return '⚠️ Quality Severely Compromised - Do Not Consume'

    def display_comprehensive_results(self, image, result):
        """Display the enhanced professional dashboard"""
        self.create_professional_dashboard(image, result)

def main():
    print("\n" + "="*80)
    print("🍎 === ADVANCED FRUIT QUALITY ANALYSIS SYSTEM === 🍊")
    print("🤖 Powered by State-of-the-Art AI & Computer Vision")
    print("="*80 + "\n")
    
    # Your Gemini API key
    API_KEY = "AIzaSyDkC-9tWhMn6XPkkvHwmighHUfY7FrN8wA"
    
    # Initialize analyzer
    analyzer = GeminiRestFruitAnalyzer(API_KEY)
    
    print("📋 MENU OPTIONS:")
    print("1. 📷 Capture from Camera (Fast Mode)")
    print("2. 🌐 Analyze from URL")
    print("3. 🚪 Exit")
    print("-"*40)
    
    while True:
        choice = input("\n➤ Enter your choice (1-3): ")
        
        if choice == "1":
            print("\n📷 === CAMERA MODE ACTIVATED ===")
            print("🚀 Initializing fast camera mode...")
            
            captured_image = analyzer.capture_image_from_camera()
            
            if captured_image is not None:
                print("\n🔬 Initiating comprehensive analysis...")
                print("⏳ This may take a few moments...")
                
                # Show loading indicator
                print("📊 Processing: ", end='')
                for i in range(5):
                    print("█", end='', flush=True)
                    time.sleep(0.2)
                print(" Complete!")
                
                # Local analysis
                local_results = analyzer.perform_local_analysis(captured_image)
                
                # Gemini AI analysis (PRIMARY)
                gemini_results = analyzer.analyze_with_gemini(captured_image)
                
                # Combine results (Gemini Priority)
                final_result = analyzer.combine_analysis_results(gemini_results, local_results)
                
                print(f"\n{'='*80}")
                print(f"🎯 ANALYSIS COMPLETE")
                print(f"{'='*80}")
                print(f"📊 Result: {final_result['condition']}")
                print(f"🎯 Confidence: {final_result['confidence']}%")
                print(f"🍎 Fruit Type: {final_result['fruit_type'].title()}")
                print(f"⚡ Action: {final_result['action_required'].upper()}")
                print(f"{'='*80}")
                
                # Display professional dashboard
                print("\n🖼️ Generating professional analysis report...")
                analyzer.display_comprehensive_results(captured_image, final_result)
        
        elif choice == "2":
            print("\n🌐 === URL MODE ACTIVATED ===")
            image_url = input("Enter the image URL: ")
            
            print("📥 Downloading image...")
            image_from_url = analyzer.load_image_from_url(image_url)
            
            if image_from_url is not None:
                print("\n🔬 Initiating comprehensive analysis...")
                print("⏳ Processing image from URL...")
                
                # Show loading indicator
                print("📊 Processing: ", end='')
                for i in range(5):
                    print("█", end='', flush=True)
                    time.sleep(0.2)
                print(" Complete!")
                
                # Local analysis
                local_results = analyzer.perform_local_analysis(image_from_url)
                
                # Gemini AI analysis (PRIMARY)
                gemini_results = analyzer.analyze_with_gemini(image_from_url)
                
                # Combine results (Gemini Priority)
                final_result = analyzer.combine_analysis_results(gemini_results, local_results)
                
                print(f"\n{'='*80}")
                print(f"🎯 ANALYSIS COMPLETE")
                print(f"{'='*80}")
                print(f"📊 Result: {final_result['condition']}")
                print(f"🎯 Confidence: {final_result['confidence']}%")
                print(f"🍎 Fruit Type: {final_result['fruit_type'].title()}")
                print(f"⚡ Action: {final_result['action_required'].upper()}")
                print(f"{'='*80}")
                
                # Display professional dashboard
                print("\n🖼️ Generating professional analysis report...")
                analyzer.display_comprehensive_results(image_from_url, final_result)
            else:
                print("❌ Error: Could not load image from URL. Please check the URL and try again.")
        
        elif choice == "3":
            print("\n" + "="*80)
            print("👋 Thank you for using the Advanced Fruit Quality Analysis System!")
            print("🌟 Stay healthy, eat quality fruits!")
            print("="*80 + "\n")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == '__main__':
    main()
