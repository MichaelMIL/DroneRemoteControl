import cv2
import numpy as np
import tkinter as tk
from tkinter import Button, Scale, HORIZONTAL
from PIL import Image, ImageTk


class VideoPlayer:
    def __init__(self, root, video_source=0, width=640, height=480):
        self.root = root
        self.root.title("Frequency & Channel Game")

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        # Set width and height for video feed
        self.width = width
        self.height = height
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Canvas for video display
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.pack()

        self.is_paused = False
        self.noise_intensity = 0

        # Buttons for play, pause, and set
        self.btn_play = Button(root, text="Play", width=10, command=self.play_video)
        self.btn_play.pack(side=tk.LEFT)

        self.btn_pause = Button(root, text="Pause", width=10, command=self.pause_video)
        self.btn_pause.pack(side=tk.LEFT)

        self.btn_set = Button(root, text="Set", width=10, command=self.check_values)
        self.btn_set.pack(side=tk.LEFT)

        # Sliders for channel and frequency
        self.channel_slider = Scale(
            root, from_=0, to=16, orient=HORIZONTAL, label="Channel"
        )
        self.channel_slider.pack(side=tk.TOP, fill=tk.X, padx=10)

        self.frequency_slider = Scale(
            root,
            from_=5.0,
            to=6.0,
            resolution=0.01,
            orient=HORIZONTAL,
            label="Frequency (GHz)",
        )
        self.frequency_slider.pack(side=tk.TOP, fill=tk.X, padx=10)

        # Correct frequency and channel (game goal)
        self.correct_channel = 15
        self.correct_frequency = 5.0

        self.update()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def play_video(self):
        self.is_paused = False

    def pause_video(self):
        self.is_paused = True

    def check_values(self):
        selected_channel = self.channel_slider.get()
        selected_frequency = self.frequency_slider.get()

        # Calculate "distance" from correct settings
        ch_distance = (
            abs(selected_channel - self.correct_channel) / 16.0
        )  # Normalize channel distance (0-16)
        freq_distance = (
            abs(selected_frequency - self.correct_frequency) / 1.0
        )  # Normalize frequency distance (5.0-6.0)

        # Combine distances and adjust noise intensity (0 means no noise, 1 means full noise)
        self.noise_intensity = ch_distance + freq_distance  # Average the two distances

        print(f"Channel: {selected_channel}, Frequency: {selected_frequency} GHz")
        print(f"Noise Intensity: {self.noise_intensity:.2f}")

    def add_video_noise(self, frame):
        noise_level = int(self.noise_intensity * 100) + 20  # Scale noise by intensity
        if noise_level > 0:
            noise = np.random.normal(0, noise_level, frame.shape).astype(np.uint8)
            noisy_frame = cv2.add(frame, noise)
            noisy_frame = cv2.add(noisy_frame, noise)
            noisy_frame = cv2.add(noisy_frame, noise)
            noisy_frame = cv2.add(noisy_frame, noise)
            noisy_frame = cv2.add(noisy_frame, noise)
            noisy_frame = cv2.add(noisy_frame, noise)
            noisy_frame = cv2.add(noisy_frame, noise)

            return noisy_frame
        return frame

    def update(self):
        if not self.is_paused:
            ret, frame = self.vid.read()
            if ret:
                frame = cv2.resize(frame, (self.width, self.height))

                if self.noise_intensity > 0:
                    frame = self.add_video_noise(frame)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.image = imgtk

        self.root.after(10, self.update)

    def on_closing(self):
        self.vid.release()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()

    # Set desired width and height for the video feed
    video_width = 800
    video_height = 600

    video_player = VideoPlayer(
        root, video_source=0, width=video_width, height=video_height
    )
    root.mainloop()
