import numpy as np
import time

class GestureRecognizer:
    def __init__(self):
        self.pinch_threshold = 0.05
        self.last_y = None
        self.last_pinch_dist = None
        self.state_history = []
        self.history_limit = 3

    def _get_distance(self, p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def detect_gesture(self, hand_landmarks):
        if not hand_landmarks:
            return "IDLE"
        
        lms = hand_landmarks.landmark
        # Index(8), Middle(12), Ring(16), Pinky(20) tips vs knuckles (6,10,14,18)
        f_up = [lms[8].y < lms[6].y, lms[12].y < lms[10].y, 
                lms[16].y < lms[14].y, lms[20].y < lms[18].y]
        
        up_cnt = sum(f_up)
        pinch_dist = self._get_distance(lms[4], lms[8])

        # --- PRIORITY 1: SCROLL (Two fingers: Index & Middle) ---
        if up_cnt == 2 and f_up[0] and f_up[1]:
            curr_y = lms[8].y
            action = "IDLE"
            if self.last_y is not None:
                dy = self.last_y - curr_y
                if dy > 0.02: action = "ACTION_SCROLL_UP"
                elif dy < -0.02: action = "ACTION_SCROLL_DOWN"
            self.last_y = curr_y
            return action

        # --- PRIORITY 2: ZOOM & ROTATE (Thumb + Index only) ---
        if up_cnt <= 1:
            if self.last_pinch_dist is not None:
                diff = pinch_dist - self.last_pinch_dist
                if abs(diff) > 0.006:
                    self.last_pinch_dist = pinch_dist
                    return "ACTION_ZOOM_IN" if diff > 0 else "ACTION_ZOOM_OUT"
            
            self.last_pinch_dist = pinch_dist
            
            if pinch_dist < self.pinch_threshold:
                return "ACTION_ROTATE"

        # --- PRIORITY 3: STATIC TRIGGERS ---
        # --- PRIORITY 3: STATIC TRIGGERS ---
        raw_cmd = "IDLE"
        
        # RESET: Hand wide open
        if up_cnt >= 3:
            raw_cmd = "ACTION_RESET"
            
        # CAPTURE FIX: If Pinky is UP and Middle/Ring are DOWN
        elif f_up[3] and not f_up[1] and not f_up[2]:
            raw_cmd = "ACTION_CAPTURE"
            
        # SELECT: Only Index up and far from thumb
        elif f_up[0] and up_cnt == 1 and pinch_dist > 0.10:
            raw_cmd = "ACTION_SELECT"
        
        # ... rest of your smoothing logic ...  

        # Simple 3-frame smoothing
        self.state_history.append(raw_cmd)
        if len(self.state_history) > self.history_limit: self.state_history.pop(0)
        return max(set(self.state_history), key=self.state_history.count)