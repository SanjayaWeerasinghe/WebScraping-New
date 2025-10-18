"""
Color extraction script for fashion products.
Based on FashionColor-0 methodology: https://github.com/morawi/FashionColor-0

Uses advanced color extraction with:
1. Background removal (GrabCut algorithm)
2. K-means clustering for dominant colors
3. Hue-based color combination
4. Probability-based filtering

See: Probabilistic color modeling of clothing elements
http://www.tara.tcd.ie/handle/2262/93334
"""

import json
import requests
from PIL import Image
from io import BytesIO
import numpy as np
from sklearn.cluster import KMeans
from skimage import color as skcolor
import cv2
from collections import Counter
import sys
import os
from pathlib import Path

# Add FashionColor-0 to path to use ColorNames
sys.path.append(str(Path(__file__).parent / 'FashionColor-0'))
from color_names import ColorNames


class FashionColorExtractor:
    """
    Extract dominant colors from fashion product images using FashionColor-0 methodology.

    This implementation follows the three-stage approach:
    1. Segment/isolate the clothing item (background removal)
    2. Cluster colors into predefined number of groups
    3. Combine detected colors based on hue scores and probability
    """

    def __init__(self, num_colors=13, hue_threshold=15, probability_threshold=0.05,
                 remove_background=True):
        """
        Initialize color extractor.

        Args:
            num_colors: Number of color clusters to extract (default: 13 as per paper)
            hue_threshold: Threshold for combining similar hues in degrees (default: 15)
            probability_threshold: Minimum probability for a color to be included (default: 0.05)
            remove_background: Whether to apply background removal (default: True)
        """
        self.num_colors = num_colors
        self.hue_threshold = hue_threshold
        self.probability_threshold = probability_threshold
        self.remove_background = remove_background
        self.color_namer = ColorNames()

    def download_image(self, image_url, timeout=10):
        """
        Download image from URL.

        Args:
            image_url: URL of the image
            timeout: Request timeout in seconds

        Returns:
            PIL Image object or None if failed
        """
        try:
            response = requests.get(image_url, timeout=timeout)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return img.convert('RGB')
        except Exception as e:
            print(f"Failed to download {image_url}: {e}")
            return None

    def _crop_by_clothing_type(self, img_array, clothing_type):
        """
        Crop image to focus on specific clothing type region.

        Args:
            img_array: Numpy array of image (RGB)
            clothing_type: Type of clothing (e.g., 'T-Shirt', 'Trousers', 'Dress')

        Returns:
            Cropped image array
        """
        height, width = img_array.shape[:2]
        clothing_type_lower = (clothing_type or '').lower()

        # Define crop regions based on clothing type
        if any(keyword in clothing_type_lower for keyword in ['shirt', 't-shirt', 'tshirt', 'top', 'blouse', 'jacket', 'coat', 'hoodie', 'sweater']):
            # Upper body: top 65% of image
            cropped = img_array[:int(height * 0.65), :]
            print(f"    Cropping for upper body ({clothing_type}): top 65%")

        elif any(keyword in clothing_type_lower for keyword in ['trouser', 'pant', 'jean', 'short', 'skirt', 'legging']):
            # Lower body: bottom 65% of image, starting from 35%
            cropped = img_array[int(height * 0.35):, :]
            print(f"    Cropping for lower body ({clothing_type}): bottom 65%")

        elif any(keyword in clothing_type_lower for keyword in ['dress', 'gown', 'saree', 'jumpsuit', 'overall']):
            # Full body: use entire image
            cropped = img_array
            print(f"    Using full image ({clothing_type})")

        elif any(keyword in clothing_type_lower for keyword in ['shoe', 'footwear', 'sandal', 'boot', 'sneaker']):
            # Footwear: bottom 25% of image
            cropped = img_array[int(height * 0.75):, :]
            print(f"    Cropping for footwear ({clothing_type}): bottom 25%")

        else:
            # Unknown type: use center 70% vertically (safe default)
            start_y = int(height * 0.15)
            end_y = int(height * 0.85)
            cropped = img_array[start_y:end_y, :]
            print(f"    Unknown clothing type ({clothing_type}): using center 70%")

        return cropped

    def _remove_background_grabcut(self, img_array, clothing_type=None):
        """
        Remove background from image using GrabCut algorithm.

        Args:
            img_array: Numpy array of image (RGB)
            clothing_type: Optional clothing type to focus on specific region

        Returns:
            Tuple of (masked_image, mask)
        """
        # Crop image based on clothing type first
        if clothing_type:
            img_array = self._crop_by_clothing_type(img_array, clothing_type)

        # Initialize mask
        mask = np.zeros(img_array.shape[:2], np.uint8)

        # Background and foreground models for GrabCut
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        # Define rectangle around the object (assume center region contains clothing)
        height, width = img_array.shape[:2]
        rect = (int(width * 0.05), int(height * 0.05),
                int(width * 0.90), int(height * 0.90))

        try:
            # Apply GrabCut
            cv2.grabCut(img_array, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

            # Create binary mask: probable foreground and definite foreground = 1
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        except Exception as e:
            print(f"    GrabCut failed: {e}, using full image")
            # If GrabCut fails, use the whole image
            mask2 = np.ones(img_array.shape[:2], dtype='uint8')

        # Apply mask to image
        masked_img = img_array * mask2[:, :, np.newaxis]

        return masked_img, mask2

    def _extract_valid_pixels(self, img_array, mask=None):
        """
        Extract valid pixels from image, filtering out background.

        Args:
            img_array: Numpy array of image
            mask: Optional mask (1 for valid pixels, 0 for background)

        Returns:
            Array of valid RGB pixels
        """
        if mask is not None:
            # Use provided mask
            valid_pixels = img_array[mask > 0]
        else:
            # Create mask based on pixel intensity
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            valid_mask = (gray > 20) & (gray < 235)
            valid_pixels = img_array[valid_mask]

        # Remove very dark pixels (likely shadows/background)
        valid_pixels = valid_pixels[np.sum(valid_pixels, axis=1) > 30]

        return valid_pixels

    def _rgb_to_hsv(self, rgb):
        """
        Convert RGB color to HSV color space.

        Args:
            rgb: RGB color array (0-255)

        Returns:
            HSV array (H: 0-360, S: 0-1, V: 0-1)
        """
        rgb_normalized = rgb / 255.0
        hsv = skcolor.rgb2hsv(rgb_normalized.reshape(1, 1, 3))
        hsv = hsv.reshape(3)
        hsv[0] *= 360  # Convert hue to degrees
        return hsv

    def _calculate_color_probabilities(self, labels):
        """
        Calculate probability of each color cluster.

        Args:
            labels: Cluster labels for each pixel

        Returns:
            Dictionary mapping cluster ID to probability
        """
        counter = Counter(labels)
        total = len(labels)
        probabilities = {cluster: count / total for cluster, count in counter.items()}
        return probabilities

    def _combine_similar_hues(self, colors, probabilities):
        """
        Combine colors with similar hues based on hue threshold.
        This implements the third stage of FashionColor-0 methodology.

        Args:
            colors: Array of RGB colors
            probabilities: Array of probabilities for each color

        Returns:
            Tuple of (combined_colors, combined_probabilities)
        """
        if len(colors) == 0:
            return [], []

        # Convert to HSV to analyze hue
        hsv_colors = np.array([self._rgb_to_hsv(c) for c in colors])

        # Group colors by similar hue
        groups = []
        used = set()

        for i in range(len(colors)):
            if i in used:
                continue

            group = [i]
            used.add(i)

            for j in range(i + 1, len(colors)):
                if j in used:
                    continue

                # Calculate hue difference (circular distance on color wheel)
                hue_diff = abs(hsv_colors[i][0] - hsv_colors[j][0])
                hue_diff = min(hue_diff, 360 - hue_diff)

                # Group if hues are similar
                if hue_diff < self.hue_threshold:
                    group.append(j)
                    used.add(j)

            groups.append(group)

        # Combine colors in each group using weighted average
        combined_colors = []
        combined_probs = []

        for group in groups:
            # Sum probabilities
            group_probs = [probabilities[idx] for idx in group]
            total_prob = sum(group_probs)

            # Filter out low-probability colors
            if total_prob < self.probability_threshold:
                continue

            # Weighted average of RGB values by probability
            weights = np.array(group_probs) / total_prob
            combined_color = np.average([colors[idx] for idx in group], axis=0, weights=weights)

            combined_colors.append(combined_color)
            combined_probs.append(total_prob)

        # Sort by probability (most dominant first)
        if combined_colors:
            sorted_indices = np.argsort(combined_probs)[::-1]
            combined_colors = [combined_colors[i] for i in sorted_indices]
            combined_probs = [combined_probs[i] for i in sorted_indices]

        return combined_colors, combined_probs

    def extract_dominant_colors(self, image, clothing_type=None):
        """
        Extract dominant colors from image using full FashionColor-0 pipeline:
        1. Crop image based on clothing type (optional)
        2. Remove background (optional)
        3. Cluster colors using k-means
        4. Combine similar hues based on probability

        Args:
            image: PIL Image object
            clothing_type: Type of clothing to focus extraction on (e.g., 'T-Shirt', 'Trousers')

        Returns:
            List of hex color strings
        """
        # Convert to numpy array
        img_array = np.array(image.convert('RGB'))

        # Stage 1: Background removal (if enabled)
        if self.remove_background:
            masked_img, mask = self._remove_background_grabcut(img_array, clothing_type)
            pixels = self._extract_valid_pixels(masked_img, mask)
        else:
            # Even without background removal, crop by clothing type
            if clothing_type:
                img_array = self._crop_by_clothing_type(img_array, clothing_type)
            pixels = self._extract_valid_pixels(img_array)

        # Check if we have enough pixels
        if len(pixels) < max(10, self.num_colors):
            print("    Not enough valid pixels after filtering")
            return []

        # Adjust number of clusters if needed
        n_clusters = min(self.num_colors, len(pixels))

        # Stage 2: Cluster colors using k-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
        labels = kmeans.fit_predict(pixels)
        cluster_colors = kmeans.cluster_centers_

        # Calculate probabilities
        prob_dict = self._calculate_color_probabilities(labels)
        probabilities = np.array([prob_dict[i] for i in range(len(cluster_colors))])

        # Stage 3: Combine similar hues
        final_colors, final_probs = self._combine_similar_hues(cluster_colors, probabilities)

        # Convert to hex
        hex_colors = []
        for color in final_colors:
            color = np.clip(color, 0, 255).astype(int)
            hex_color = '#{:02x}{:02x}{:02x}ff'.format(color[0], color[1], color[2])
            hex_colors.append(hex_color)

        return hex_colors

    def get_color_names(self, hex_colors):
        """
        Convert hex colors to human-readable color names.

        Args:
            hex_colors: List of hex color strings

        Returns:
            List of color names
        """
        color_names = []
        for hex_color in hex_colors:
            try:
                color_name = self.color_namer.get_color_name(hex_color)
                color_names.append(color_name)
            except Exception as e:
                print(f"Failed to get name for color {hex_color}: {e}")

        return color_names

    def extract_colors_from_url(self, image_url, clothing_type=None):
        """
        Extract color names from product image URL.

        Args:
            image_url: URL of the product image
            clothing_type: Type of clothing to focus extraction on (e.g., 'T-Shirt', 'Trousers')

        Returns:
            List of color names or empty list if failed
        """
        # Download image
        image = self.download_image(image_url)
        if image is None:
            return []

        # Extract dominant colors with clothing type awareness
        hex_colors = self.extract_dominant_colors(image, clothing_type)
        if not hex_colors:
            return []

        # Convert to color names
        color_names = self.get_color_names(hex_colors)

        # Remove duplicates while preserving order
        seen = set()
        unique_colors = []
        for color in color_names:
            if color not in seen:
                seen.add(color)
                unique_colors.append(color)

        return unique_colors


def process_product_file(input_file, output_file, num_colors=13, hue_threshold=15,
                        probability_threshold=0.05, remove_background=True, max_products=None):
    """
    Process a JSON file of products and extract colors.

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
        num_colors: Number of dominant colors to extract
        hue_threshold: Threshold for combining similar hues (degrees)
        probability_threshold: Minimum probability for a color to be included
        remove_background: Whether to use background removal
        max_products: Maximum number of products to process (None for all)
    """
    print(f"\nProcessing {input_file}...")

    # Load products
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('products', [])
    total_products = len(products)

    if max_products:
        products = products[:max_products]
        print(f"Processing first {len(products)} of {total_products} products")
    else:
        print(f"Processing all {total_products} products")

    # Initialize color extractor with all parameters
    extractor = FashionColorExtractor(
        num_colors=num_colors,
        hue_threshold=hue_threshold,
        probability_threshold=probability_threshold,
        remove_background=remove_background
    )

    # Process each product
    processed_count = 0
    success_count = 0

    for i, product in enumerate(products):
        image_url = product.get('image_url')
        product_name = product.get('name') or 'Unknown'
        clothing_type = product.get('clothing_type')

        if not image_url:
            print(f"[{i+1}/{len(products)}] Skipping product (no image URL): {product_name}")
            continue

        print(f"[{i+1}/{len(products)}] Processing: {product_name[:50]}... ({clothing_type})")

        # Extract colors with clothing type awareness
        colors = extractor.extract_colors_from_url(image_url, clothing_type)

        if colors:
            product['colors'] = colors
            success_count += 1
            print(f"  -> Found colors: {colors}")
        else:
            product['colors'] = []
            print(f"  -> No colors extracted")

        processed_count += 1

    # Update data
    data['products'] = products if max_products else products

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Processed {processed_count} products")
    print(f"[+] Successfully extracted colors for {success_count} products")
    print(f"[+] Saved to: {output_file}")


if __name__ == "__main__":
    # Configuration - Based on FashionColor-0 paper recommendations
    NUM_COLORS = 13  # Number of color clusters (as per paper)
    HUE_THRESHOLD = 15  # Degrees - for combining similar hues
    PROBABILITY_THRESHOLD = 0.05  # Minimum probability (5%)
    REMOVE_BACKGROUND = True  # Use GrabCut for background removal
    MAX_PRODUCTS = None  # Set to None to process all products, or a number for testing

    print("="*60)
    print("FashionColor-0 Color Extraction")
    print("="*60)
    print(f"Configuration:")
    print(f"  - Number of clusters: {NUM_COLORS}")
    print(f"  - Hue threshold: {HUE_THRESHOLD}°")
    print(f"  - Probability threshold: {PROBABILITY_THRESHOLD}")
    print(f"  - Background removal: {REMOVE_BACKGROUND}")
    print(f"  - Clothing-type aware cropping: ENABLED")
    print(f"  - Max products per file: {MAX_PRODUCTS if MAX_PRODUCTS else 'All'}")
    print("="*60)
    print("\nClothing-type aware cropping:")
    print("  - T-Shirts/Shirts/Tops: Extract from top 65% of image")
    print("  - Trousers/Jeans/Pants: Extract from bottom 65% of image")
    print("  - Dresses/Sarees: Use full image")
    print("  - Footwear: Extract from bottom 25% of image")
    print("="*60)

    # Process all fashion data files
    output_dir = Path("output")
    output_dir_with_colors = Path("output_with_colors")
    output_dir_with_colors.mkdir(exist_ok=True)

    json_files = list(output_dir.glob("*.json"))

    if not json_files:
        print("\nNo JSON files found in output/ directory")
        print("Please ensure your fashion data JSON files are in the 'output' folder")
    else:
        print(f"\nFound {len(json_files)} JSON files to process\n")

        for json_file in json_files:
            output_file = output_dir_with_colors / json_file.name
            process_product_file(
                input_file=json_file,
                output_file=output_file,
                num_colors=NUM_COLORS,
                hue_threshold=HUE_THRESHOLD,
                probability_threshold=PROBABILITY_THRESHOLD,
                remove_background=REMOVE_BACKGROUND,
                max_products=MAX_PRODUCTS
            )

        print(f"\n{'='*60}")
        print("All files processed successfully!")
        print(f"Results saved in: {output_dir_with_colors}")
        print("="*60)
