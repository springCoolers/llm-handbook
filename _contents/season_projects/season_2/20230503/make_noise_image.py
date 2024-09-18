import numpy as np
from PIL import Image

# Load the image
image_path = "data/original_text/text_image0.png"  # Replace with the path to your image
image = Image.open(image_path)

# Convert the image to a NumPy array
image_array = np.array(image)

print('333333333333')
print(image_array.shape)
print(type(image_array.shape))

k = 10
x = int(image_array.shape[0] / k)
y = int(image_array.shape[1] / k)
z = int(image_array.shape[2])
image_shape = (x, y, z)

print(image_shape)
print(type(image_shape))

# Generate random noise
noise = np.random.normal(loc=0, scale=50, size=image_shape).astype(np.uint8)

# Add the noise to the image
noisy_image_array = np.clip(image_array + noise, 0, 255).astype(np.uint8)

# Convert the NumPy array back to an image
noisy_image = Image.fromarray(noisy_image_array)

# Save the noisy image
noisy_image.save("noisy_image.png")