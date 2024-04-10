import subprocess  # nosec
import time

import cv2


class AutoLight:
    def __init__(self, max_value, edge_threshold):
        """
        Initializes the AutoLight class.

        Args:
            max_value (int): Maximum value for brightness detected between 0-255.
            edge_threshold (int): Threshold for triggering brightness adjust.
        """
        self.screen_threshold = [1067, 21333]
        self.cam_threshold = [0, (max_value if max_value <= 255 else 255)]
        self.last_value = 0
        self.edge_threshold = edge_threshold

    def convert_signal_to_brightness(self, signal):
        """
        Converts a signal value to a brightness value.

        Args:
            signal (int): Signal value.

        Returns:
            float: Brightness value.
        """
        # Calculate brightness level based on signal value
        step = (
            self.screen_threshold[1] - self.screen_threshold[0]
        ) / self.cam_threshold[1]
        brightness = ((signal if signal < self.cam_threshold[1] else self.cam_threshold[1]) * step) + self.screen_threshold[0]
        return int(brightness)

    def detect_light(self):
        """
        Detects the brightness level of the screen.

        Returns:
            float: Brightness level.
        """
        # Capture video from webcam (index 0 for default camera)
        cap = cv2.VideoCapture(0)

        # Check if webcam opened successfully
        if not cap.isOpened():
            print("Error opening webcam!")
            exit()

        # Capture a single frame
        ret, frame = cap.read()

        # Release the webcam capture
        cap.release()

        # Convert frame to grayscale for simpler analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate average pixel intensity
        avg_intensity = int(cv2.mean(gray)[0])

        # # Load the pre-trained Haar cascade for face detection
        # face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # # Detect faces
        # faces = face_cascade.detectMultiScale(
        #     gray,
        #     scaleFactor=1.1,
        #     minNeighbors=5,
        #     minSize=(30, 30),
        #     flags=cv2.CASCADE_SCALE_IMAGE
        # )

        # if len(faces) < 1:
        #     return 0

        # Return the average intensity (higher value indicates brighter image)
        return avg_intensity

    def set_brightness(self, brightness_level):
        """
        Attempts to set screen brightness using dbus command.

        Args:
            brightness_level (float): Brightness value between custom threshold.
        """
        # Convert brightness level to string representation for dbus
        brightness = self.convert_signal_to_brightness(brightness_level)
        if brightness in range(self.screen_threshold[0], self.screen_threshold[1]+1):
            brightness_string = str(self.convert_signal_to_brightness(brightness_level))
            subprocess.run(
                [
                    "/usr/bin/qdbus",
                    "org.kde.Solid.PowerManagement",
                    "/org/kde/Solid/PowerManagement/Actions/BrightnessControl",
                    "org.kde.Solid.PowerManagement.Actions.BrightnessControl.setBrightnessSilent",
                    brightness_string,
                ]
            )  # nosec
        else:
            print("Brightness value out of range!")
            print(brightness)
            return

    def run(self):
        """
        Runs the auto-brightness script.
        """
        # Continuously check for changes in brightness
        while True:
            time.sleep(3)
            current_value = self.detect_light()
            self.wake_threshold = [
                self.last_value - self.edge_threshold,
                self.last_value + self.edge_threshold,
            ]
            if current_value not in range(
                self.wake_threshold[0], self.wake_threshold[1]+1
            ):
                self.last_value = current_value
                self.set_brightness(current_value)


if __name__ == "__main__":
    # Example usage
    max_brightness_value = 255  # Maximum brightness value (0-255)
    edge_threshold = 10  # Threshold for triggering brightness adjust
    AutoLight(
        max_brightness_value, edge_threshold
    ).run()  # Run the auto-brightness script (continuously)
