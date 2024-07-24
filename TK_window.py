#libraries
import tkinter as tk
from PIL import Image, ImageTk 
from label_generate import generate_labels
import time
import os
import glob


def read_png_names(directory): #function used to read the labels of images in given directory
    labels = []
    # Use glob to match the pattern '*.png'
    files = glob.glob(os.path.join(directory, '*.png'))
    for file in files:
        labels.append(os.path.basename(file).replace('.png',''))
    return labels


def display_image(images_path, label_generator, image_duration=4000, break_duration=1000, recorder=None, labels=['break', 'forward', 'backward', 'left', 'right']):
    # This function displays images in a Tkinter window. It alternates between displaying an image and a break image.
    # The images to be displayed are determined by the label_generator function.
    # The duration of each image and break is specified by image_duration and break_duration respectively.
    # The recorder is an opject used by the cortex app to record and export the EEG data during showing the image

    # Initialize some variables
    break_time = True  # Whether we are currently in a break
    curLabel = "break"  # The current label
    nextLabel = label_generator()  # The next label to be displayed
    record_dic = {i: 0 for i in labels}  # A dictionary to keep track of how many times each label has been displayed

    # Create a Tkinter window
    root = tk.Tk()

    # Define a function to be called when the window is closed
    def on_closing():
        # Print the record dictionary and the total number of images displayed
        print(record_dic)
        print(sum(record_dic.values()))
        # If a recorder was provided, print the total number of images it recorded
        if recorder is not None:
            print(recorder.exportedSum)
        # Destroy the window
        root.destroy()
        # If a recorder was provided, tell it to stop recording
        if recorder is not None:
            recorder.exit_fun()

    # Set the function to be called when the window is closed
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Create some labels to display information about the current image and remaining time
    remaining_time_label = tk.Label(root, text="Remaining Time: 0.0 ms")
    remaining_time_label.pack(side="top", pady=10)
    motion_label_label = tk.Label(root, text="Current label is: {}".format(curLabel))
    motion_label_label.pack(side="top", pady=10)

    # Load the images
    Images = {i: Image.open(images_path + (i + ".png")).convert("RGBA") for i in labels}

    # Create some layers for image transitions
    breakImg = Images['break']
    white_layer = Image.new('RGBA', breakImg.size, color=(255, 255, 255, 255))
    transparent_layer = Image.new('RGBA', breakImg.size, color=(255, 255, 255, 0))

    # Create a label to display the current image
    photo = ImageTk.PhotoImage(breakImg)
    panel = tk.Label(root, image=photo)

    # Initialize a variable to keep track of whether the images are currently being displayed
    is_playing = False

    # Define a function to start or pause the image display
    def toggle_playback():
        nonlocal is_playing
        nonlocal prev_time
        # Toggle the is_playing variable
        is_playing = not is_playing
        # Update the text of the play/pause button
        play_pause_button.config(text="pause" if is_playing else "play")
        # Update the image and remaining time label
        photo = ImageTk.PhotoImage(Images['break'])
        panel.configure(image=photo)
        panel.image = photo
        remaining_time_label.config(text="Remaining Time: 0.0 ms")
        # Record the current time
        prev_time = time.time()
        # If the images are now playing, start displaying the next image
        if is_playing:
            show_next_image(white_layer, break_duration)
        # If the images are now paused, update the motion label
        else:
            motion_label_label.config(text=record_dic)

    # Create a play/pause button
    play_pause_button = tk.Button(root, text="Play" if not is_playing else "Pause", command=toggle_playback)
    play_pause_button.pack(side="top")

    # Pack the image label
    panel.pack(side="bottom", fill="both", expand="yes")

    # Initialize some variables for the image display timing
    interval = 100
    prev_time = time.time()

    # Set the title of the window
    root.title("Image Display")

    # Define a function to display the next image
    def show_next_image(image, remaining_time):
        # This function is called repeatedly to update the displayed image and remaining time.
        # It uses the after method of the Tkinter window to schedule the next call to itself.

        # Access some non-local variables
        nonlocal break_time
        nonlocal curLabel
        nonlocal nextLabel
        nonlocal interval
        nonlocal prev_time
        nonlocal is_playing

        # If the images are not currently playing, reset some variables and update the window
        if not is_playing:
            curLabel = 'break'
            break_time = True
            if recorder is not None:
                recorder.stop_record()
                recorder.enableExport = False
            root.update()
            return

        # Update the remaining time label
        if not break_time:
            remaining_time_label.config(text="Remaining Time: {} ms".format(round(remaining_time / 1000, 1)))
        else:
            remaining_time_label.config(text="Remaining Time: 0.0 ms")

        # Update the motion label
        motion_label_label.config(text="Current label is: {}".format(curLabel.replace('_', ' ')))
        curImg = image
        # If there is still time remaining for the current image, update the image and schedule the next call to this function
        if remaining_time > 0:
            # Calculate some factors for the image transition
            duration = break_duration if break_time else image_duration
            transition_interval = 500
            startAlphaFactor = max(0, (duration - remaining_time - 100) / transition_interval)
            endAlphaFactor = float(remaining_time) / transition_interval
            betweenAlphaFactor = min(1, max(0, (duration - remaining_time - transition_interval - 200) / transition_interval))

            # Create a copy of the current image
            bgImg = image.copy()

            # If we are currently in a break, create a new image for the transition
            if break_time:
                if startAlphaFactor < 1:
                    bgImg = Image.blend(bgImg, white_layer, alpha=startAlphaFactor)
                    fgImg = Image.blend(transparent_layer, Images["break"], alpha=min(1, startAlphaFactor) * 0.5)
                    new_img = Image.alpha_composite(bgImg, fgImg)
                elif startAlphaFactor >= 1 and endAlphaFactor > 1:
                    curImg = Images[nextLabel]
                    bgImg = curImg.copy()
                    bgImg = Image.blend(bgImg, transparent_layer, alpha=1 - betweenAlphaFactor)
                    fgImg = Image.blend(Images["break"], transparent_layer, alpha=0.5)
                    new_img = Image.alpha_composite(bgImg, fgImg)
                elif endAlphaFactor <= 1 and recorder is not None and recorder.isDoneExport == False and recorder.enableExport == True:  # wait till export is done
                    remaining_time += 200
                    curImg = Images[nextLabel]
                    bgImg = curImg.copy()
                    bgImg = Image.blend(bgImg, transparent_layer, alpha=1 - betweenAlphaFactor)
                    fgImg = Image.blend(Images["break"], transparent_layer, alpha=0.5)
                    new_img = Image.alpha_composite(bgImg, fgImg)
                elif endAlphaFactor <= 1:
                    curImg = Images[nextLabel]
                    bgImg = curImg.copy()
                    fgImg = Image.blend(transparent_layer, Images['break'], alpha=endAlphaFactor * 0.5)
                    new_img = Image.alpha_composite(bgImg, fgImg)
                new_img = Image.alpha_composite(bgImg, fgImg)
            else:
                new_img = Images[nextLabel]

            # Update the image label
            photo = ImageTk.PhotoImage(new_img)
            panel.configure(image=photo)
            panel.image = photo

            # Update the window
            root.update()

            # Calculate the actual interval since the last call to this function
            real_interval = round((time.time() - prev_time) * 1000, 3)

            # Record the current time
            prev_time = time.time()

            # Calculate the remaining time for the current image
            remaining_time = max(remaining_time - real_interval, 0)

            # Schedule the next call to this function
            root.after(interval, lambda: show_next_image(curImg, remaining_time))
        else:
            # If there is no time remaining for the current image, switch to the next image or break
            break_time = not break_time
            if break_time:
                # If we are switching to a break, stop the recorder if one was provided
                if recorder is not None:
                    recorder.stop_record()
                    recorder.enableExport = True
                # Update the record dictionary
                record_dic[curLabel] += 1
                # Reset the current label
                curLabel = "break"
                # Get the next label to be displayed
                nextLabel = label_generator()
            else:
                # If we are switching to an image, update the current label
                curLabel = nextLabel
                # Start the recorder if one was provided
                if recorder is not None:
                    cwd = os.getcwd()
                    recorder.record_export_folder = cwd + recorder.output_dir + curLabel
                    recorder.record_title = curLabel[0:2] + recorder.record_title[2:]
                    recorder.create_record(recorder.record_title)
            
            # Determine the duration and interval for the next image or break
            duration = break_duration if break_time else image_duration
            interval = 10 if break_time else 100

            # Schedule the next call to this function
            root.after(interval, lambda: show_next_image(curImg, duration))

    # Set the size and position of the window
    root.geometry('%dx%d+%d+%d' % (400, 500, 500, 150))
    # Start the Tkinter event loop
    root.mainloop()

def main(img_path, duration ,break_duration = 3000,recorder = None): #That is the main funtion of the code file where used to run the UI
    # Path to the images folder >> all images in png format >> one image has to be named `break.png`
    images_path = img_path
    # Duration for which each image is displayed
    image_duration = duration 
    # Duration for which the break is displayed
    break_duration = break_duration
    # Read the names of the PNG images in the specified path
    imgs_labels = read_png_names(images_path)
    # Create a list of labels for the images
    labels_to_gen = [i for i in imgs_labels]
    print(labels_to_gen)
    #Start a label generator object which used to create the next labels with balanced random generator 
    label_generator = generate_labels(1500, labels_to_gen)
    #Initialize the TK window and start data recording
    display_image(images_path, label_generator ,image_duration = image_duration, break_duration = break_duration,labels = imgs_labels,recorder = recorder)


# Example usage:
if __name__ == "__main__":

    images_path = "./_images/"
    image_duration = 4000  # Display each image for 4000 milliseconds (4 seconds)
    break_duration = 3000
    main(images_path, duration=image_duration, break_duration=break_duration)
