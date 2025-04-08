# Import necessary libraries for GUI and image processing.
# tkinter: For creating the graphical user interface.
# filedialog and messagebox: For file selection and displaying messages.
# ttk: Provides themed widget set for more modern-looking GUI elements.
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Pillow modules for image manipulation:
# Image: Opens and manipulates images.
# ImageDraw: Draws shapes on images.
# ImageTk: Converts PIL images for display in Tkinter.
# ImageOps: Provides common image operations (grayscale, invert, etc.).
from PIL import Image, ImageDraw, ImageTk, ImageOps
import os  # os module for file path manipulations.

# -------------------------------
# TRANSFORMATION FUNCTIONS
# -------------------------------

def pixelate_image(image, pixel_size=10):
    """
    Converts the image into a pixelated version.
    It divides the image into blocks of size (pixel_size x pixel_size), computes the average color,
    and draws a rectangle filled with that color over each block.
    """
    # Ensure the image is in RGB mode.
    image = image.convert("RGB")
    width, height = image.size

    # Create a new blank image with the same size to draw the pixelated effect.
    pixelated_image = Image.new("RGB", (width, height))
    # Create a drawing object.
    draw = ImageDraw.Draw(pixelated_image)

    # Loop through the image in steps of pixel_size.
    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            # Define the coordinates for the current block.
            box = (x, y, x + pixel_size, y + pixel_size)
            # Crop the section of the image corresponding to the block.
            block = image.crop(box)
            # Convert the block into a list of its pixel data.
            pixels = list(block.getdata())
            # Calculate the average color by summing values per channel and dividing by number of pixels.
            num_pixels = len(pixels)
            avg_color = tuple(sum(channel) // num_pixels for channel in zip(*pixels))
            # Draw a rectangle filled with the average color onto the new image.
            draw.rectangle(box, fill=avg_color)
    return pixelated_image

def dot_mosaic_image(image, pixel_size=10):
    """
    Creates a dot mosaic version of the image.
    Similar to pixelate_image, it divides the image into blocks but instead draws a filled circle (dot)
    for each block using the average color.
    """
    # Ensure image is in RGB mode.
    image = image.convert("RGB")
    width, height = image.size

    # Create a new blank image with a white background.
    mosaic_image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(mosaic_image)

    # Process the image block by block.
    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            box = (x, y, x + pixel_size, y + pixel_size)
            block = image.crop(box)
            pixels = list(block.getdata())
            num_pixels = len(pixels)
            avg_color = tuple(sum(channel) // num_pixels for channel in zip(*pixels))
            # Calculate the center of the block.
            center_x = x + pixel_size // 2
            center_y = y + pixel_size // 2
            # Radius for the dot (circle).
            radius = pixel_size // 2
            # Define the bounding box for the ellipse (circle) to be drawn.
            ellipse_box = (center_x - radius, center_y - radius,
                           center_x + radius, center_y + radius)
            # Draw the circle (dot) with the average color.
            draw.ellipse(ellipse_box, fill=avg_color)
    return mosaic_image

def grayscale_image(image):
    """
    Converts the image to grayscale.
    The image is first converted to "L" mode (grayscale) and then back to RGB,
    ensuring consistency with other processing functions.
    """
    return ImageOps.grayscale(image).convert("RGB")

def invert_image(image):
    """
    Inverts the colors of the image.
    Converts the image to RGB and then applies the inversion.
    """
    image = image.convert("RGB")
    return ImageOps.invert(image)

# -------------------------------
# GUI APPLICATION CLASS
# -------------------------------

class ImageTransformerApp:
    def __init__(self, root):
        """
        Initializes the GUI window and its widgets.
        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.root.title("Advanced Image Transformer")
        self.image = None       # This will hold the original PIL image.
        self.image_path = None  # This stores the full path of the loaded image.

        # Frame for file selection.
        file_frame = ttk.LabelFrame(root, text="1. Select an Image")
        file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        # Button to trigger image selection.
        self.select_btn = ttk.Button(file_frame, text="Select Image", command=self.select_image)
        self.select_btn.grid(row=0, column=0, padx=5, pady=5)
        # Label to display the name of the selected file.
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.grid(row=0, column=1, padx=5, pady=5)

        # Frame for transformation options.
        options_frame = ttk.LabelFrame(root, text="2. Choose Transformations")
        options_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Label and entry for setting pixel size (used in pixelate and dot mosaic transformations).
        ttk.Label(options_frame, text="Pixel Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pixel_size_entry = ttk.Entry(options_frame, width=5)
        self.pixel_size_entry.insert(0, "10")  # Default value.
        self.pixel_size_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Create checkboxes for each transformation option.
        # The BooleanVar() holds the state (True or False) for the checkbox.
        self.transform_vars = {
            "Pixelate": tk.BooleanVar(),
            "Dot Mosaic": tk.BooleanVar(),
            "Grayscale": tk.BooleanVar(),
            "Invert": tk.BooleanVar()
        }
        row = 1
        # Loop through each transformation option and add a checkbox.
        for transform, var in self.transform_vars.items():
            cb = ttk.Checkbutton(options_frame, text=transform, variable=var)
            cb.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2)
            row += 1

        # Frame for the process button.
        process_frame = ttk.Frame(root)
        process_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        # Button that triggers the image processing based on the selected options.
        self.process_btn = ttk.Button(process_frame, text="Process Image", command=self.process_image)
        self.process_btn.grid(row=0, column=0, padx=5, pady=5)
    
    def select_image(self):
        """
        Opens a file dialog to let the user select an image file.
        After selection, the image is loaded and stored.
        """
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
        )
        # If a file is selected, load it.
        if file_path:
            try:
                self.image = Image.open(file_path)
                self.image_path = file_path
                # Update the label with the file name.
                self.file_label.config(text=os.path.basename(file_path))
            except Exception as e:
                messagebox.showerror("Error", f"Unable to open image:\n{e}")
        else:
            messagebox.showwarning("File Selection", "No file was selected.")

    def process_image(self):
        """
        Processes the loaded image based on the selected transformation options.
        For each selected transformation:
         - Applies the transformation.
         - Saves the resulting image in the same directory with a modified name.
         - Displays the image in a new window.
        """
        # Check if an image has been loaded.
        if self.image is None or self.image_path is None:
            messagebox.showerror("No Image", "Please select an image first.")
            return

        # Retrieve and validate the pixel size from the entry field.
        try:
            pixel_size = int(self.pixel_size_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Pixel Size must be an integer.")
            return

        # Map each transformation option to its corresponding function.
        transformations = {
            "Pixelate": lambda img: pixelate_image(img, pixel_size=pixel_size),
            "Dot Mosaic": lambda img: dot_mosaic_image(img, pixel_size=pixel_size),
            "Grayscale": grayscale_image,
            "Invert": invert_image
        }

        # Determine where to save transformed images by splitting the original file path.
        directory, filename = os.path.split(self.image_path)

        # Apply each selected transformation.
        for transform_name, func in transformations.items():
            if self.transform_vars[transform_name].get():
                try:
                    transformed_image = func(self.image)
                except Exception as e:
                    messagebox.showerror("Transformation Error",
                                         f"Error applying {transform_name} transformation:\n{e}")
                    continue

                # Create a new filename indicating the type of transformation.
                base, ext = os.path.splitext(filename)
                new_filename = f"{base}_{transform_name.replace(' ', '').lower()}{ext}"
                save_path = os.path.join(directory, new_filename)
                try:
                    # Save the transformed image.
                    transformed_image.save(save_path)
                    print(f"{transform_name} image saved to: {save_path}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Error saving {transform_name} image:\n{e}")
                    continue
                
                # Display the transformed image.
                self.display_image(transformed_image, f"{transform_name} Image")
    
    def display_image(self, pil_image, window_title):
        """
        Displays a given PIL image in a new Tkinter window (Toplevel widget).
        Args:
            pil_image: The PIL image object to display.
            window_title: Title for the new window.
        """
        # Create a new top-level window.
        top = tk.Toplevel(self.root)
        top.title(window_title)
        
        # Convert the PIL image to a Tkinter PhotoImage.
        tk_image = ImageTk.PhotoImage(pil_image)
        # Create and place a label widget with the image.
        label = ttk.Label(top, image=tk_image)
        label.image = tk_image  # Keep a reference so that the image is not garbage-collected.
        label.pack(padx=10, pady=10)
        

# -------------------------------
# MAIN EXECUTION BLOCK
# -------------------------------
if __name__ == "__main__":
    # Create the main Tkinter window.
    root = tk.Tk()
    # Instantiate the ImageTransformerApp with the root window.
    app = ImageTransformerApp(root)
    # Start the Tkinter event loop.
    root.mainloop()
