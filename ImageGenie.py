import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PIL import Image, ImageDraw, ImageTk, ImageOps

# -------------------------------
# TRANSFORMATION FUNCTIONS
# -------------------------------

def pixelate_image(image, pixel_size=10):
    """
    Create a pixelated version of an image.
    Divides the image into blocks, computes each block's average color,
    and then draws a colored rectangle on that block.
    """
    image = image.convert("RGB")
    width, height = image.size
    pixelated_image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(pixelated_image)
    
    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            box = (x, y, x + pixel_size, y + pixel_size)
            block = image.crop(box)
            pixels = list(block.getdata())
            num_pixels = len(pixels)
            avg_color = tuple(sum(channel) // num_pixels for channel in zip(*pixels))
            draw.rectangle(box, fill=avg_color)
    return pixelated_image

def dot_mosaic_image(image, pixel_size=10):
    """
    Create a dot mosaic version of an image.
    Divides the image into blocks, calculates the average color,
    and draws a filled circle (dot) in the center of each block.
    """
    image = image.convert("RGB")
    width, height = image.size
    mosaic_image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(mosaic_image)
    
    for y in range(0, height, pixel_size):
        for x in range(0, width, pixel_size):
            box = (x, y, x + pixel_size, y + pixel_size)
            block = image.crop(box)
            pixels = list(block.getdata())
            num_pixels = len(pixels)
            avg_color = tuple(sum(channel) // num_pixels for channel in zip(*pixels))
            center_x = x + pixel_size // 2
            center_y = y + pixel_size // 2
            radius = pixel_size // 2
            ellipse_box = (center_x - radius, center_y - radius,
                           center_x + radius, center_y + radius)
            draw.ellipse(ellipse_box, fill=avg_color)
    return mosaic_image

def grayscale_image(image):
    """
    Convert the image to grayscale.
    The image is processed and returned in RGB mode.
    """
    return ImageOps.grayscale(image).convert("RGB")

def invert_image(image):
    """
    Invert the colors of the image.
    """
    image = image.convert("RGB")
    return ImageOps.invert(image)

# -------------------------------
# GUI APPLICATION CLASS
# -------------------------------

class ImageTransformerApp:
    def __init__(self, root):
        """
        Initialize the GUI with a modern, visually appealing layout.
        Applies custom styling to frames, labels, and buttons.
        """
        self.root = root
        self.root.title("Advanced Image Transformer")
        self.root.configure(background="#ffffff")
        self.image = None           # Holds the loaded image.
        self.image_path = None      # Path to the loaded image.
        self.save_directory = None  # Output directory for processed images.

        # Create and configure a ttk Style for a modern look.
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Using 'clam' for flexibility in styling.
        self.style.configure("TFrame", background="#ffffff")
        self.style.configure("TLabel", background="#ffffff", foreground="#333333", font=("Helvetica", 10))
        self.style.configure("TLabelFrame", background="#ffffff", foreground="#333333", font=("Helvetica", 11, "bold"))
        self.style.configure("TLabelFrame.Label", background="#ffffff")
        self.style.configure("TButton", background="#4CAF50", foreground="white", font=("Helvetica", 10, "bold"), padding=6)
        self.style.map("TButton", background=[("active", "#45a049")])
        
        # Configure the root window to have three columns: left margin, center content, right margin.
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)  # Center column gets most of the space.
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create the central container frame.
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        
        # ----- FILE SELECTION FRAME -----
        file_frame = ttk.LabelFrame(self.main_frame, text="1. Select an Image")
        file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        file_frame.columnconfigure(1, weight=1)
        self.select_btn = ttk.Button(file_frame, text="Select Image", command=self.select_image)
        self.select_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # ----- IMAGE INFORMATION FRAME -----
        info_frame = ttk.LabelFrame(self.main_frame, text="Image Information")
        info_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        info_frame.columnconfigure(0, weight=1)
        self.info_label = ttk.Label(info_frame, text="No image loaded", wraplength=400)
        self.info_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # ----- OUTPUT DIRECTORY FRAME -----
        output_frame = ttk.LabelFrame(self.main_frame, text="2. Select Output Directory")
        output_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        output_frame.columnconfigure(1, weight=1)
        self.save_dir_btn = ttk.Button(output_frame, text="Choose Save Directory", command=self.select_save_directory)
        self.save_dir_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.save_dir_label = ttk.Label(output_frame, text="No directory selected")
        self.save_dir_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # ----- TRANSFORMATION OPTIONS FRAME -----
        options_frame = ttk.LabelFrame(self.main_frame, text="3. Choose Transformations")
        options_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        options_frame.columnconfigure(1, weight=1)
        ttk.Label(options_frame, text="Pixel Size:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.pixel_size_entry = ttk.Entry(options_frame, width=5)
        self.pixel_size_entry.insert(0, "10")
        self.pixel_size_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.transform_vars = {
            "Pixelate": tk.BooleanVar(),
            "Dot Mosaic": tk.BooleanVar(),
            "Grayscale": tk.BooleanVar(),
            "Invert": tk.BooleanVar()
        }
        row = 1
        for transform, var in self.transform_vars.items():
            cb = ttk.Checkbutton(options_frame, text=transform, variable=var)
            cb.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="w")
            row += 1

        # ----- PROCESS BUTTON FRAME -----
        process_frame = ttk.Frame(self.main_frame)
        process_frame.grid(row=4, column=0, padx=5, pady=15, sticky="ew")
        process_frame.columnconfigure(0, weight=1)
        self.process_btn = ttk.Button(process_frame, text="Process Image", command=self.process_image)
        self.process_btn.grid(row=0, column=0, padx=10, pady=10)

        # ----- TRANSFORMATION SUMMARY FRAME -----
        summary_frame = ttk.LabelFrame(self.main_frame, text="Transformation Summary")
        summary_frame.grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        summary_frame.columnconfigure(0, weight=1)
        self.summary_label = ttk.Label(summary_frame, text="No transformations applied yet", justify="left", wraplength=400)
        self.summary_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    
    def select_image(self):
        """
        Opens a file dialog to choose an image. Loads the image and updates labels
        with the file name and image information (dimensions and pixel count).
        """
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
        )
        if file_path:
            try:
                self.image = Image.open(file_path)
                self.image_path = file_path
                self.file_label.config(text=os.path.basename(file_path))
                width, height = self.image.size
                total_pixels = width * height
                info_text = f"Dimensions: {width} x {height}  |  Total Pixels: {total_pixels}"
                self.info_label.config(text=info_text)
            except Exception as e:
                messagebox.showerror("Error", f"Unable to open image:\n{e}")
        else:
            messagebox.showwarning("File Selection", "No file was selected.")

    def select_save_directory(self):
        """
        Opens a directory dialog for selecting an output folder for processed images.
        """
        directory = filedialog.askdirectory(title="Select Save Directory")
        if directory:
            self.save_directory = directory
            self.save_dir_label.config(text=directory)
        else:
            messagebox.showwarning("Directory Selection", "No directory was selected.")

    def process_image(self):
        """
        Processes the loaded image using selected transformations.
        Saves processed images to the chosen output directory (or default directory)
        and updates the Transformation Summary with details about the manipulation.
        """
        if self.image is None or self.image_path is None:
            messagebox.showerror("No Image", "Please select an image first.")
            return

        try:
            pixel_size = int(self.pixel_size_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Pixel Size must be an integer.")
            return

        transformations = {
            "Pixelate": lambda img: pixelate_image(img, pixel_size=pixel_size),
            "Dot Mosaic": lambda img: dot_mosaic_image(img, pixel_size=pixel_size),
            "Grayscale": grayscale_image,
            "Invert": invert_image
        }

        if self.save_directory:
            directory = self.save_directory
        else:
            directory, _ = os.path.split(self.image_path)

        width, height = self.image.size
        total_pixels = width * height
        summary_str = f"Original Image: {width} x {height} ({total_pixels} pixels)\n"
        
        for transform_name, func in transformations.items():
            if self.transform_vars[transform_name].get():
                try:
                    transformed_image = func(self.image)
                except Exception as e:
                    messagebox.showerror("Transformation Error",
                                         f"Error applying {transform_name} transformation:\n{e}")
                    continue

                base, ext = os.path.splitext(os.path.basename(self.image_path))
                new_filename = f"{base}_{transform_name.replace(' ', '').lower()}{ext}"
                save_path = os.path.join(directory, new_filename)
                try:
                    transformed_image.save(save_path)
                    print(f"{transform_name} image saved to: {save_path}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Error saving {transform_name} image:\n{e}")
                    continue
                
                # Update summary with specifics for each transformation.
                if transform_name in ("Pixelate", "Dot Mosaic"):
                    blocks_x = width // pixel_size
                    blocks_y = height // pixel_size
                    total_blocks = blocks_x * blocks_y
                    summary_str += (f"\n{transform_name}:\n  Divided into {blocks_x} columns x {blocks_y} rows = {total_blocks} blocks "
                                    f"(~{pixel_size**2} pixels per block).\n")
                elif transform_name == "Grayscale":
                    summary_str += f"\nGrayscale:\n  All {total_pixels} pixels converted to grayscale.\n"
                elif transform_name == "Invert":
                    summary_str += f"\nInvert:\n  All {total_pixels} pixels had their colors inverted.\n"

                self.display_image(transformed_image, f"{transform_name} Image")

        self.summary_label.config(text=summary_str)

    def display_image(self, pil_image, window_title):
        """
        Display a transformed image in a new top-level window.
        """
        top = tk.Toplevel(self.root)
        top.title(window_title)
        tk_image = ImageTk.PhotoImage(pil_image)
        label = ttk.Label(top, image=tk_image)
        label.image = tk_image  # Maintain a reference.
        label.pack(padx=10, pady=10)

# -------------------------------
# MAIN EXECUTION BLOCK
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageTransformerApp(root)
    root.mainloop()
