#!/usr/bin/env python3
"""
Logo Processing Script for Reserka Gothic
Crops letters from animated GIF and makes background transparent
"""

from PIL import Image, ImageChops
import numpy as np
from pathlib import Path

def process_gif_logo(input_path: str, output_path: str):
    """
    Process animated GIF to crop letters and make background transparent
    """
    print(f"🎨 Processing animated logo: {input_path}")
    
    # Open the original GIF
    with Image.open(input_path) as img:
        frames = []
        durations = []
        
        try:
            frame_count = 0
            while True:
                # Get current frame
                current_frame = img.copy()
                
                # Get frame duration
                duration = img.info.get('duration', 100)
                durations.append(duration)
                
                # Convert to RGBA for transparency support
                if current_frame.mode != 'RGBA':
                    current_frame = current_frame.convert('RGBA')
                
                # Process frame to make background transparent
                processed_frame = make_background_transparent(current_frame)
                
                # Crop to content (letters only)
                cropped_frame = crop_to_content(processed_frame)
                
                frames.append(cropped_frame)
                frame_count += 1
                
                # Move to next frame
                img.seek(img.tell() + 1)
                
        except EOFError:
            # End of frames
            pass
        
        print(f"  ✓ Processed {len(frames)} frames")
        
        # Save the processed animated GIF
        if frames:
            # Use the first frame as the base
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,  # Infinite loop
                transparency=0,
                disposal=2  # Clear to background color
            )
            
            print(f"  ✅ Saved transparent logo: {output_path}")
            print(f"  📏 Frame size: {frames[0].size}")
            return True
        
        return False

def make_background_transparent(image):
    """
    Make background transparent by detecting and removing background color
    """
    # Convert to numpy array for processing
    data = np.array(image)
    
    # Get the background color from corners (assuming corners are background)
    corners = [
        data[0, 0],      # Top-left
        data[0, -1],     # Top-right  
        data[-1, 0],     # Bottom-left
        data[-1, -1]     # Bottom-right
    ]
    
    # Find most common corner color as background
    bg_color = corners[0]  # Use top-left as default
    
    # Create mask for background pixels
    # Allow some tolerance for similar colors
    tolerance = 30
    
    # Calculate difference from background color
    diff = np.abs(data[:, :, :3].astype(int) - bg_color[:3].astype(int))
    mask = np.all(diff <= tolerance, axis=2)
    
    # Set alpha channel to 0 for background pixels
    data[mask, 3] = 0
    
    # Convert back to PIL Image
    return Image.fromarray(data, 'RGBA')

def crop_to_content(image):
    """
    Crop image to the bounding box of non-transparent content
    """
    # Get the bounding box of non-transparent pixels
    bbox = image.getbbox()
    
    if bbox:
        # Add some padding around the content
        padding = 10
        width, height = image.size
        
        left = max(0, bbox[0] - padding)
        top = max(0, bbox[1] - padding)
        right = min(width, bbox[2] + padding)
        bottom = min(height, bbox[3] + padding)
        
        return image.crop((left, top, right, bottom))
    
    return image

def auto_detect_letters_region(image):
    """
    Automatically detect the region containing letters
    """
    # Convert to grayscale for analysis
    gray = image.convert('L')
    data = np.array(gray)
    
    # Find non-background regions (assuming dark text on light background)
    threshold = np.mean(data) * 0.7  # Adaptive threshold
    text_mask = data < threshold
    
    # Find bounding box of text regions
    if np.any(text_mask):
        coords = np.where(text_mask)
        top, left = np.min(coords, axis=1)
        bottom, right = np.max(coords, axis=1)
        
        # Add padding
        padding = 20
        height, width = data.shape
        
        top = max(0, top - padding)
        left = max(0, left - padding)
        bottom = min(height, bottom + padding)
        right = min(width, right + padding)
        
        return (left, top, right, bottom)
    
    return image.getbbox()

def create_optimized_version(input_path: str, output_path: str, max_size: tuple = (400, 200)):
    """
    Create an optimized version with size constraints
    """
    print(f"🔄 Creating optimized version...")
    
    with Image.open(input_path) as img:
        frames = []
        durations = []
        
        # Calculate scaling factor to fit within max_size
        original_size = img.size
        scale_x = max_size[0] / original_size[0]
        scale_y = max_size[1] / original_size[1]
        scale = min(scale_x, scale_y, 1.0)  # Don't upscale
        
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        print(f"  📏 Scaling from {original_size} to {new_size}")
        
        try:
            while True:
                current_frame = img.copy()
                duration = img.info.get('duration', 100)
                durations.append(duration)
                
                # Resize frame
                if current_frame.mode != 'RGBA':
                    current_frame = current_frame.convert('RGBA')
                
                resized_frame = current_frame.resize(new_size, Image.Resampling.LANCZOS)
                frames.append(resized_frame)
                
                img.seek(img.tell() + 1)
                
        except EOFError:
            pass
        
        # Save optimized version
        if frames:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                optimize=True
            )
            
            print(f"  ✅ Saved optimized logo: {output_path}")
            return True
    
    return False

def main():
    """
    Main processing function
    """
    input_file = "assets/logo.gif"
    output_file = "assets/logo_transparent.gif"
    output_optimized = "assets/logo_optimized.gif"
    
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        return
    
    print("🎨 Starting logo processing...")
    
    try:
        # Process the logo to make background transparent and crop
        success = process_gif_logo(input_file, output_file)
        
        if success:
            # Create an optimized version for better game performance
            create_optimized_version(output_file, output_optimized, max_size=(300, 150))
            
            print("\n🎉 Logo processing complete!")
            print(f"📁 Files created:")
            print(f"  • {output_file} - Full transparent version")
            print(f"  • {output_optimized} - Optimized for game use")
            
            # Show file sizes
            original_size = Path(input_file).stat().st_size
            transparent_size = Path(output_file).stat().st_size
            optimized_size = Path(output_optimized).stat().st_size
            
            print(f"\n📊 File sizes:")
            print(f"  • Original: {original_size / 1024 / 1024:.1f} MB")
            print(f"  • Transparent: {transparent_size / 1024 / 1024:.1f} MB")
            print(f"  • Optimized: {optimized_size / 1024 / 1024:.1f} MB")
            
        else:
            print("❌ Failed to process logo")
            
    except Exception as e:
        print(f"❌ Error processing logo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
