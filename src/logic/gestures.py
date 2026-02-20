import numpy as np
import time

class GestureRecognizer:
    def __init__(self):
        self.pinch_threshold = 0.04  # Slightly tighter for rotate
        self.last_y = None
        self.last_pinch_dist = None
        self.state_history = []
        self.history_limit = 8 # Increased for better smoothing
        self.zoom_sensitivity = 0.02
        self.pinch_active_threshold = 0.22

    def _get_distance(self, p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def detect_gesture(self, hand_landmarks):
        if not hand_landmarks:
            self.last_pinch_dist = None
            self.last_y = None
            return "IDLE"
        
        lms = hand_landmarks.landmark
        f_up = [lms[8].y < lms[6].y, lms[12].y < lms[10].y, 
                lms[16].y < lms[14].y, lms[20].y < lms[18].y]
        
        up_cnt = sum(f_up)
        wrist = lms[0]
        
        if wrist.y < 0.2 or wrist.x < 0.1 or wrist.x > 0.9:
            self.last_pinch_dist = None
            self.last_y = None
            return "IDLE"

        pinch_dist = self._get_distance(lms[4], lms[8])

        # --- PRIORITY 1: SCROLL ---
        if up_cnt == 2 and f_up[0] and f_up[1]:
            curr_y = lms[8].y
            action = "IDLE"
            if self.last_y is not None:
                dy = self.last_y - curr_y
                if abs(dy) > 0.03: # Deadzone for scroll
                    action = "ACTION_SCROLL_UP" if dy > 0 else "ACTION_SCROLL_DOWN"
            self.last_y = curr_y
            return action # Bypassing smoothing for continuous movement

        # --- PRIORITY 2: ZOOM & ROTATE ---
        if up_cnt <= 1:
            # Only process Zoom/Rotate if Index is the active finger (or both down for pinch)
            if up_cnt == 0 or f_up[0]:
                raw_cmd = "IDLE"
                # Logic: If thumb and index are active
                if self.last_pinch_dist is not None:
                    diff = pinch_dist - self.last_pinch_dist
                    # Improved Zoom logic: must exceed sensitivity AND stay within active threshold
                    if abs(diff) > self.zoom_sensitivity and pinch_dist < self.pinch_active_threshold:
                        self.last_pinch_dist = pinch_dist
                        return "ACTION_ZOOM_IN" if diff > 0 else "ACTION_ZOOM_OUT"
                
                self.last_pinch_dist = pinch_dist
                
                # Rotation triggered by pinch-and-hold (tighter threshold)
                if pinch_dist < self.pinch_threshold:
                    raw_cmd = "ACTION_ROTATE"
                
                if raw_cmd != "IDLE":
                    self.state_history.append(raw_cmd)
                    if len(self.state_history) > self.history_limit: self.state_history.pop(0)
                    return max(set(self.state_history), key=self.state_history.count)
                
                return "IDLE" # EARLY RETURN: Only if it was clearly meant for Thumb/Index

        # --- PRIORITY 3: STATIC TRIGGERS ---
        # Reachable if up_cnt >= 2 (but failed P1) or if up_cnt == 1 (and not index)
        raw_cmd = "IDLE"
        if up_cnt >= 3:
            # Palm extension for Reset
            raw_cmd = "ACTION_RESET"
        elif f_up[3] and not f_up[0] and not f_up[1] and not f_up[2]:
            # ONLY Pinky up for Capture (Snappier detection)
            raw_cmd = "ACTION_CAPTURE"
        
        self.state_history.append(raw_cmd)
        if len(self.state_history) > self.history_limit: self.state_history.pop(0)
        return max(set(self.state_history), key=self.state_history.count)
