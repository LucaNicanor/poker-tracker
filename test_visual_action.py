import numpy as np
from PIL import Image

im = Image.open("hands/raw/clubwpt/clubwpt_hand_20261023_221827.png")
w, h = im.size

# In this screenshot, Ainsley1 has the timer circle active
# Let's crop Ainsley1's timer circle: X around 820-900, Y around 640-740
crop_ainsley = im.crop((int(w * 0.70), int(h * 0.76), int(w * 0.77), int(h * 0.88)))
crop_ainsley.save("hands/raw/clubwpt/test_timer_circle.png")

arr = np.array(crop_ainsley)
# Check for cyan / electric blue pixels: R < 80, G > 140, B > 180
cyan_mask = (arr[:, :, 0] < 80) & (arr[:, :, 1] > 140) & (arr[:, :, 2] > 180)
cyan_count = np.sum(cyan_mask)

print(f"Image size: {w}x{h}")
print(f"Cyan timer pixels in active player circle: {cyan_count}")

# Check Hero avatar circle area (when NOT active): X around 47% to 54%, Y around 85% to 98%
crop_hero = im.crop((int(w * 0.47), int(h * 0.85), int(w * 0.54), int(h * 0.98)))
arr_hero = np.array(crop_hero)
cyan_hero_mask = (
    (arr_hero[:, :, 0] < 80) & (arr_hero[:, :, 1] > 140) & (arr_hero[:, :, 2] > 180)
)
cyan_hero_count = np.sum(cyan_hero_mask)
print(f"Cyan timer pixels in Hero area (when folded/inactive): {cyan_hero_count}")
