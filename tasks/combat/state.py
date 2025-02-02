import cv2
from scipy import signal

from module.base.timer import Timer
from module.base.utils import rgb2gray
from tasks.base.ui import UI
from tasks.combat.assets.assets_combat_state import COMBAT_AUTO, COMBAT_PAUSE, COMBAT_SPEED_2X


class CombatState(UI):
    _combat_click_interval = Timer(1, count=2)

    def is_combat_executing(self) -> bool:
        appear = self.appear(COMBAT_PAUSE)
        if appear:
            if COMBAT_PAUSE.button_offset[0] <= 5:
                return True

        return False

    def is_combat_auto(self) -> bool:
        image = rgb2gray(self.image_crop(COMBAT_AUTO))
        line = cv2.reduce(image, 1, cv2.REDUCE_AVG).flatten()
        # [122 122 122 182 141 127 139 135 130 135 136 141 147 149 149 150 147 145
        #  148 150 150 150 150 150 144 138 134 141 136 133 173 183 130 128 127 126]
        parameters = {
            # Border is about 188-190
            'height': 160,
            # Background is about 120-122
            'prominence': 35,
        }
        peaks, _ = signal.find_peaks(line, **parameters)
        return len(peaks) == 2

    def is_combat_speed_2x(self) -> bool:
        image = rgb2gray(self.image_crop(COMBAT_SPEED_2X))
        line = cv2.reduce(image, 1, cv2.REDUCE_AVG).flatten()
        # [122 122 122 182 141 127 139 135 130 135 136 141 147 149 149 150 147 145
        #  148 150 150 150 150 150 144 138 134 141 136 133 173 183 130 128 127 126]
        parameters = {
            # Border is about 188-190
            'height': 160,
            # Background is about 120-122
            'prominence': 35,
        }
        peaks, _ = signal.find_peaks(line, **parameters)
        return len(peaks) == 2

    def handle_combat_state(self, auto=True, speed_2x=True):
        """
        Set combat auto and 2X speed. Enable both by default.

        Returns:
            bool: If clicked
        """
        if not self.is_combat_executing():
            return False

        if speed_2x and not self.is_combat_speed_2x():
            if self._combat_click_interval.reached():
                self.device.click(COMBAT_SPEED_2X)
                self._combat_click_interval.reset()
                return True
        if not speed_2x and self.is_combat_speed_2x():
            if self._combat_click_interval.reached():
                self.device.click(COMBAT_SPEED_2X)
                self._combat_click_interval.reset()
                return True
        if auto and not self.is_combat_auto():
            if self._combat_click_interval.reached():
                self.device.click(COMBAT_AUTO)
                self._combat_click_interval.reset()
                return True
        if not auto and self.is_combat_auto():
            if self._combat_click_interval.reached():
                self.device.click(COMBAT_AUTO)
                self._combat_click_interval.reset()
                return True

        return False
