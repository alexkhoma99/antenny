# Priting
import sys
import serial
import shutil

import colorama

class TerminalPrinter(object):

    YES_DISPLAY_STRING = colorama.Fore.GREEN + "YES" + colorama.Fore.RESET
    NO_DISPLAY_STRING = colorama.Fore.RED + "NO" + colorama.Fore.RESET
    GYRO_CALIBRATION_MESSAGE = "To calibrate the gyroscope, let the sensor rest on a level surface for a few seconds."
    ACCEL_CALIBRATION_MESSAGE = "To calibrate the accelerometer, slowly move the sensor into >=6 distinct " \
                                "orientations,\nsome perpendicular to the xyz axes. "
    MAGNET_CALIBRATION_MESSAGE = "To calibrate the magnetometer, move the sensor in figure-8 shapes through the air a " \
                                 "few times. "

    def print_error(self, string):
        print("\n" + string + "\n")

    def parse_error(self, e):
        error_list = str(e).strip('()').split(", b'")
        error_list[0] = error_list[0][1:]
        ret = []
        for err in error_list:
            ret.append(bytes(err[0:-1], 'utf-8').decode('unicode-escape'))
        return ret

    def print_error_and_exception(self, error, exception):
        self.print_error(error)
        error_list = self.parse_error(exception)
        try:
            print(error_list[2])
        except:
            pass

    def calibration_wait_message(self, gyro_calibrated, accel_calibrated, magnet_calibrated, use_ellipsis=True):
        """
        generate a human-readable message that indicates which components remain
        to be calibrated, e.g. if all the arguments are true, then it should
        return the string "waiting for gyroscope, accelerometer and magnetometer
        to be calibrated...".
        """
        components = ((['gyroscope'] if not gyro_calibrated else []) +
                      (['accelerometer'] if not accel_calibrated else []) +
                      (['magnetometer'] if not magnet_calibrated else []))
        components_list_string = ', '.join(components[:-2] + [" and ".join(components[-2:])])
        if components:
            return ("waiting for " + components_list_string +
                    " to be calibrated" + ("..." if use_ellipsis else ""))
        else:
            return "all components calibrated!"

    def _display_initial_calibration_status(
        self,
        calibration_status
    ):
        """
        Display the initial calibration message, with status and calibration instructions.

        calibration_status: A tuple of booleans representing previous calibration T/F
                            status for the system, gyroscope, accelerometer, and magnetometer
        """
        system_calibrated, gyro_calibrated, accel_calibrated, magnet_calibrated = calibration_status
        print("System calibrated?", f"{self.YES_DISPLAY_STRING}" if system_calibrated else self.NO_DISPLAY_STRING)
        print("\n")
        if gyro_calibrated:
            print(" - Gyroscope is calibrated.")
        else:
            print(f" - {self.GYRO_CALIBRATION_MESSAGE}")

        if accel_calibrated:
            print(" - Accelerometer is calibrated.")
        else:
            print(f" - {self.ACCEL_CALIBRATION_MESSAGE}")

        if magnet_calibrated:
            print(" - Magnetometer is calibrated.")
        else:
            print(f" - {self.MAGNET_CALIBRATION_MESSAGE}")
        print("\n")

    def _display_loop_calibration_status(
        self,
        calibration_data,
        old_calibration_status,
        waiting_dot_count,
        dot_counter
    ):
        """
        Display calibration status, to be updated periodically.

        calibration_data: A tuple of integers representing calibration status for the
                          system, gyroscope, accelerometer, and magnetometer
        old_calibration_status: A tuple of booleans representing previous calibration T/F
                                status for the system, gyroscope, accelerometer, and magnetometer
        waiting_dot_count: The number of ellipsis dots to cycle through
        dot_counter: The index of the current ellipsis dot, in range [0, waiting_dot_count)
        """

        system_level, gyro_level, accel_level, magnet_level = calibration_data
        system_calibrated, gyro_calibrated, accel_calibrated, magnet_calibrated = old_calibration_status

        print(" \n" * 8, end='')
        self._display_initial_calibration_status(old_calibration_status)
        print(" ")

        gyro_calibrated = gyro_calibrated or gyro_level > 0
        accel_calibrated = accel_calibrated or accel_level > 0
        magnet_calibrated = magnet_calibrated or magnet_level > 0
        system_calibrated = system_calibrated or system_level > 0

        # Print the calibration status panel: this is the section that automatically refereshes.
        waiting_dots = ('.' * dot_counter) + '/' + ('.' * (waiting_dot_count - dot_counter - 1))
        print("┌ CALIBRATION STATUS")
        print("│")
        print("│ * Gyroscope calibrated?",
                f"{self.YES_DISPLAY_STRING} (level {gyro_level}/3)" if gyro_calibrated else self.NO_DISPLAY_STRING)
        print("│ * Accelerometer calibrated?",
                f"{self.YES_DISPLAY_STRING} (level {accel_level}/3)" if accel_calibrated else self.NO_DISPLAY_STRING)
        print("│ * Magnetometer calibrated?",
                f"{self.YES_DISPLAY_STRING} (level {magnet_level}/3)" if magnet_calibrated else self.NO_DISPLAY_STRING)
        print("│")
        wait_message = self.calibration_wait_message(gyro_calibrated, accel_calibrated, magnet_calibrated, use_ellipsis=False)
        wait_message += (" " + waiting_dots if wait_message else "")

        # Write the wait message with an appropriate amount of trailing whitespace in order
        # to clear the line from previous longer writes
        terminal_width, _ = shutil.get_terminal_size()
        spacing_length = max(min(terminal_width - 3 - len(wait_message), 20), 0)
        print(f"└ {wait_message}", " " * spacing_length)

        return (system_calibrated, gyro_calibrated, accel_calibrated, magnet_calibrated)


    pass
