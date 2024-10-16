import tkinter as tk
from tkinter import ttk

import platform

if platform.system() == "Windows":
    HOST_OS = "Windows"
else:
    HOST_OS = "Linux"

if HOST_OS == "Windows":
    import vgamepad as vg


def normalize_value(value: int) -> int:
    if not (0 <= value <= 100):
        print("Input must be between 0 and 100")

    # Scale from 0-100 to 0-65535 (65536 total values in 16-bit range)
    scaled_value = (value / 100) * 65535

    # Shift the scaled value to the range -32768 to 32767
    normalized_value = int(scaled_value - 32768)

    return normalized_value


class ArmDisarmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arm/Disarm Controller")
        self.root.geometry("400x300")

        # Range of the slider (0 to 100)
        self.range = 65_536  # 2^16 need to be normalized +32767 to -32768
        # Initialize the virtual gamepad
        if HOST_OS == "Windows":
            self.gamepad = vg.VX360Gamepad()

        # State for the button (armed or disarmed)
        self.armed = tk.BooleanVar(value=False)

        # Create a frame for the layout (button on the left, slider on the right)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left side - Toggle switch and Circular button
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(side="left", padx=20)

        # Toggle switch for arming/disarming
        self.arm_toggle = ttk.Checkbutton(
            self.control_frame,
            text="Armed",
            variable=self.armed,
            command=self.toggle_arm_disarm,
            style="Switch.TCheckbutton",
        )
        self.arm_toggle.pack(pady=10)

        # Smaller circular button (not clickable now, just to display the status)
        self.button = tk.Canvas(self.control_frame, width=150, height=150)
        self.circle = self.button.create_oval(10, 10, 140, 140, fill="red")
        self.text = self.button.create_text(
            75, 75, text="DISARM", font=("Arial", 14), fill="white"
        )
        self.button.pack()

        # Right side - Slider and percentage display
        self.slider_frame = tk.Frame(self.main_frame)
        self.slider_frame.pack(side="right", padx=20)
        self.slider_value_label = tk.Label(
            self.slider_frame, text="0%", font=("Arial", 14)
        )
        self.slider_value_label.pack(side="left", padx=10)

        self.slider = ttk.Scale(
            self.slider_frame,
            value=100,
            from_=0,
            to=100,
            orient="vertical",
            command=self.update_slider_label,
        )
        self.slider.pack(side="left")

    def toggle_arm_disarm(self):
        """Toggle between armed and disarmed states using the switch."""
        if self.armed.get():
            # Armed
            self.button.itemconfig(self.circle, fill="green")
            self.button.itemconfig(self.text, text="ARM")
            if HOST_OS == "Windows":
                self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                self.gamepad.update()
        else:
            # Disarmed
            self.button.itemconfig(self.circle, fill="red")
            self.button.itemconfig(self.text, text="DISARM")
            if HOST_OS == "Windows":
                self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
                self.gamepad.update()

    def update_slider_label(self, value):
        """Update the percentage label next to the slider."""
        percentage = 100 - int(float(value))
        val = normalize_value(percentage)
        print(f"Value: {val}")
        if HOST_OS == "Windows":
            self.gamepad.left_joystick(
                x_value=val, y_value=0
            )  # values between -32768 and 32767
            self.gamepad.update()
        self.slider_value_label.config(text=f"{percentage}%")


if __name__ == "__main__":
    root = tk.Tk()

    # Add style for the toggle switch (this is optional and can be modified)
    style = ttk.Style(root)
    style.configure("Switch.TCheckbutton", font=("Arial", 12))

    app = ArmDisarmApp(root)
    root.mainloop()
