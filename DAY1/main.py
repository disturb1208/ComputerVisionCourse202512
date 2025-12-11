import cv2
import numpy as np
import os

def process_image(image_path, pipeline_steps):
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    # Load image
    original_img = cv2.imread(image_path)
    if original_img is None:
        print("Error: Failed to load image.")
        return

    # Create a copy for processing (will be converted to Gray)
    # and a copy for displaying results (kept in Color)
    gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    display_img = original_img.copy()
    
    # Current state of the image being processed pipeline
    current_img = gray_img

    print(f"Starting processing for {image_path}...")
    
    # List to store images for simultaneous display
    displayed_steps = []
    displayed_steps.append(("Original Image", original_img.copy()))

    for step in pipeline_steps:
        step_type = step.get("type")
        params = step.get("params", {})
        
        print(f"Running step: {step_type}")

        if step_type == "blur":
            blur_type = params.get("type", "gaussian")
            ksize = params.get("ksize", 9)
            if blur_type == "gaussian":
                # ksize must be odd
                if ksize % 2 == 0: ksize += 1
                current_img = cv2.GaussianBlur(current_img, (ksize, ksize), 0)
            
            displayed_steps.append((f"Result after {step_type}", current_img.copy()))

        elif step_type == "threshold":
            # Binarization step
            thresh_val = params.get("threshold", 127)
            max_val = 255
            # Apply binary thresholding
            _, current_img = cv2.threshold(current_img, thresh_val, max_val, cv2.THRESH_BINARY)
            
            displayed_steps.append((f"Result after {step_type}", current_img.copy()))

        elif step_type == "edge":
            method = params.get("method", "canny")
            if method == "canny":
                t1 = params.get("threshold1", 50)
                t2 = params.get("threshold2", 150)
                aperture = params.get("ksize", 3)
                current_img = cv2.Canny(current_img, t1, t2, apertureSize=aperture)
            
            displayed_steps.append((f"Result after {step_type}", current_img.copy()))

        elif step_type == "contour":
            thresh_val = params.get("thresholdValue", 127)
            mode_str = params.get("retrievalMode", "TREE")
            min_area = params.get("minArea", 0)
            show_bbox = params.get("showBoundingBox", False)
            show_centroid = params.get("showCentroid", True)
            show_label = params.get("showLabel", True)

            # Map retrieval mode
            mode = cv2.RETR_TREE
            if mode_str == "EXTERNAL": mode = cv2.RETR_EXTERNAL
            elif mode_str == "LIST": mode = cv2.RETR_LIST

            # Ensure binary. If previous step was Canny, it's already binary (0/255).
            _, binary_img = cv2.threshold(current_img, thresh_val, 255, cv2.THRESH_BINARY)

            contours, _ = cv2.findContours(binary_img, mode, cv2.CHAIN_APPROX_SIMPLE)

            print(f"Found {len(contours)} contours. Filtering with minArea={min_area}...")

            count = 0
            for i, cnt in enumerate(contours):
                area = cv2.contourArea(cnt)
                if area < min_area:
                    continue
                
                count += 1
                
                # Draw Contours (Green)
                cv2.drawContours(display_img, [cnt], -1, (0, 255, 0), 2)

                # Bounding Box (Blue)
                if show_bbox:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(display_img, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # Centroid (Red Dot)
                M = cv2.moments(cnt)
                cx, cy = 0, 0
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                
                if show_centroid and M['m00'] != 0:
                    cv2.circle(display_img, (cx, cy), 5, (0, 0, 255), -1)

                # Label (Yellow Text)
                if show_label:
                    label_text = f"ID:{i} A:{int(area)}"
                    text_pos = (cx - 20, cy - 10) if M['m00'] != 0 else (cnt[0][0][0], cnt[0][0][1])
                    cv2.putText(display_img, label_text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            print(f"Kept {count} contours after filtering.")
    
    # Add final processed image to the list for display
    displayed_steps.append(("Processed Result (Contours Drawn)", display_img.copy()))

    # Save final result
    output_path = "processed_result.jpg"
    cv2.imwrite(output_path, display_img)
    print(f"Final result saved to {output_path}")

    # Display all collected step results simultaneously
    for window_name, img in displayed_steps:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        h, w = img.shape[:2]
        max_w, max_h = 1280, 720
        scale = min(max_w / w, max_h / h)

        if scale < 1:
            new_w = int(w * scale)
            new_h = int(h * scale)
            cv2.resizeWindow(window_name, new_w, new_h)
            print(f"Display window '{window_name}' resized to {new_w}x{new_h} to fit screen.")
        
        cv2.imshow(window_name, img)
    
    print("Press any key to close all image windows...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Configuration from user request
    pipeline_config = [
      {
        "type": "blur",
        "params": {
          "type": "gaussian",
          "ksize": 9
        }
      },
      {
        "type": "threshold",
        "params": {
          "threshold": 127
        }
      },
      {
        "type": "edge",
        "params": {
          "method": "canny",
          "threshold1": 50,
          "threshold2": 150,
          "ksize": 3
        }
      },
      {
        "type": "contour",
        "params": {
          "thresholdValue": 136,
          "retrievalMode": "TREE",
          "minArea": 550,
          "showBoundingBox": False,
          "showCentroid": True,
          "showLabel": True
        }
      }
    ]
    
    target_image = "Image_20251210104315649.bmp"
    process_image(target_image, pipeline_config)