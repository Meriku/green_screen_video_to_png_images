import numpy
import math
from PIL import Image, ImageChops
from moviepy import *
import os


def colorclose(Cb_p, Cr_p, Cb_key, Cr_key, tola, tolb):
    """
    Calculate the alpha mask value based on color distance.
    
    Args:
        Cb_p (float): Cb value of the current pixel
        Cr_p (float): Cr value of the current pixel
        Cb_key (float): Cb value of the key color
        Cr_key (float): Cr value of the key color
        tola (float): Lower tolerance threshold
        tolb (float): Upper tolerance threshold
    
    Returns:
        float: Alpha mask value (0-255)
    """
    temp = math.sqrt((Cb_key - Cb_p)**2 + (Cr_key - Cr_p)**2)
    if temp < tola:
        z = 0.0
    elif temp < tolb:
        z = ((temp - tola) / (tolb - tola))
    else:
        z = 1.0
    return 255.0 * z

def remove_green_screen(frame, index, keyColor=None, tolerance=None):
    """
    Remove green screen from a single frame.
    
    Args:
        frame (numpy.ndarray): Input frame
        index (int): Frame index for output filename
        keyColor (tuple, optional): Key color to remove. Defaults to None.
        tolerance (list, optional): Color removal tolerance. Defaults to None.
    
    Returns:
        Image: Processed frame with green screen removed
    """
    # Convert frame to PIL Image in YCbCr color space
    inDataFG = Image.fromarray(frame).convert('YCbCr')

    # Set default key color and tolerance if not provided
    if keyColor is None:
        keyColor = inDataFG.getpixel((1, 1))
    if tolerance is None:
        tolerance = [30, 120]
    
    [Y_key, Cb_key, Cr_key] = keyColor
    [tola, tolb] = tolerance
    
    (x, y) = inDataFG.size  # get dimensions
    foreground = numpy.array(inDataFG.getdata())  # make array from image
    maskgen = numpy.vectorize(colorclose)  # vectorize masking function

    # Generate alpha mask
    alphaMask = maskgen(foreground[:, 1], foreground[:, 2], Cb_key, Cr_key, tola, tolb)
    alphaMask.shape = (y, x)  # make mask dimensions of original image
    imMask = Image.fromarray(numpy.uint8(alphaMask))
    
    # Create inverted mask
    invertMask = Image.fromarray(numpy.uint8(255 - 255 * (alphaMask / 255)))
    
    # Create images for color mask
    colorMask = Image.new('RGBA', (x, y), tuple([0, 0, 0, 0]))
    allgreen = Image.new('YCbCr', (x, y), tuple(keyColor))
    
    # Make color mask green in green values on image
    colorMask.paste(allgreen, invertMask)
    
    # Convert input image to RGBA
    inDataFG = inDataFG.convert('RGBA')
    
    # Subtract greens from input
    cleaned = ImageChops.subtract(inDataFG, colorMask)
    
    return cleaned

def remove_green_screen_from_video(input_video_path, save_to_directory, process_all_frames = True):
    """
    Remove green screen from an entire video.
    
    Args:
        input_video_path (str): Path to input video
        save_to_directory (str): Directory to save processed frames
    """
    # Ensure output directory exists
    os.makedirs(save_to_directory, exist_ok=True)

    # Load video
    input_video = VideoFileClip(input_video_path)

    # Process each frame
    for idx, frame in enumerate(input_video.iter_frames()):

        if process_all_frames or idx % 5 == 0:

            # Remove green screen from the frame
            cleaned_frame = remove_green_screen(frame, idx)
            
            # Save the processed frame
            outfile = os.path.join(save_to_directory, f'output_{idx}.png')
            cleaned_frame.save(outfile, "PNG")

            print(f'finished processing frame #: {idx}')

    # Close the video to release resources
    input_video.close()


input_video_path = r"path/input_video_name"     # C:/myfolder/myvideo.mp4
save_to_directory = r"path/output_folder_name"  # C:/myfolder/images    

remove_green_screen_from_video(input_video_path, save_to_directory)
print("done")