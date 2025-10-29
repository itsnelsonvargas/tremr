"""
Creates a bright, eye-catching earthquake warning icon
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_earthquake_icon(filename='earthquake_warning.png', size=256):
    """Create a bright earthquake warning icon"""

    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Color scheme - bright and attention-grabbing
    red = (255, 0, 0, 255)
    orange = (255, 140, 0, 255)
    yellow = (255, 215, 0, 255)
    white = (255, 255, 255, 255)
    dark_red = (180, 0, 0, 255)

    # Draw outer glow effect (multiple circles)
    center = size // 2
    for i in range(5, 0, -1):
        alpha = 40 * i
        glow_color = (255, 0, 0, alpha)
        radius = center - (10 * (5 - i))
        draw.ellipse([center - radius, center - radius,
                     center + radius, center + radius],
                    fill=glow_color)

    # Draw main circle (gradient effect with multiple circles)
    for i in range(20, 0, -1):
        radius = center - 20 - i
        # Color transition from red to orange
        r = 255
        g = int(140 * (20 - i) / 20)
        b = 0
        color = (r, g, b, 255)
        draw.ellipse([center - radius, center - radius,
                     center + radius, center + radius],
                    fill=color)

    # Draw warning triangle in the center
    triangle_size = size // 3
    triangle_top = center - triangle_size // 2
    triangle_bottom = center + triangle_size // 2
    triangle_left = center - triangle_size // 2
    triangle_right = center + triangle_size // 2

    # Draw yellow warning triangle with border
    triangle_points = [
        (center, triangle_top),
        (triangle_left, triangle_bottom),
        (triangle_right, triangle_bottom)
    ]

    # Black outline for triangle
    outline_offset = 3
    outline_points = [
        (center, triangle_top - outline_offset),
        (triangle_left - outline_offset, triangle_bottom + outline_offset),
        (triangle_right + outline_offset, triangle_bottom + outline_offset)
    ]
    draw.polygon(outline_points, fill=(0, 0, 0, 255))
    draw.polygon(triangle_points, fill=yellow)

    # Draw exclamation mark
    exclaim_width = size // 20
    exclaim_top = center - triangle_size // 3
    exclaim_middle = center + triangle_size // 6

    # Exclamation line
    draw.rectangle([
        center - exclaim_width, exclaim_top,
        center + exclaim_width, exclaim_middle
    ], fill=dark_red)

    # Exclamation dot
    dot_size = exclaim_width * 2
    dot_top = exclaim_middle + exclaim_width * 2
    draw.ellipse([
        center - dot_size, dot_top,
        center + dot_size, dot_top + dot_size * 2
    ], fill=dark_red)

    # Draw earthquake waves at bottom
    wave_y_start = center + triangle_size // 2 + 10
    wave_width = 4
    wave_color = white

    # Multiple wave lines
    for wave_num in range(3):
        y_pos = wave_y_start + (wave_num * 8)
        # Zigzag wave pattern
        points = []
        num_points = 8
        for i in range(num_points):
            x = (size // 8) + (i * (3 * size // 4) // (num_points - 1))
            y_offset = 5 if i % 2 == 0 else -5
            points.append((x, y_pos + y_offset))

        # Draw the wave
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=wave_color, width=wave_width)

    # Add inner shine effect
    shine_radius = size // 6
    shine_offset = size // 4
    for i in range(3, 0, -1):
        alpha = 60 * i
        shine_color = (255, 255, 255, alpha)
        r = shine_radius - (i * 5)
        draw.ellipse([
            center - shine_offset - r, center - shine_offset - r,
            center - shine_offset + r, center - shine_offset + r
        ], fill=shine_color)

    # Save the image
    img.save(filename, 'PNG')
    print(f"✓ Created earthquake warning icon: {filename}")
    print(f"  Size: {size}x{size} pixels")
    print(f"  Format: PNG with transparency")

    return filename

if __name__ == '__main__':
    # Create the icon
    icon_file = create_earthquake_icon()

    # Open the image to show it
    try:
        img = Image.open(icon_file)
        img.show()
        print("\n✓ Icon created and opened for preview!")
    except Exception as e:
        print(f"Icon created but couldn't preview: {e}")
