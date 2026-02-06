import numpy as np
import time

class GestureRecognizer:
    def __init__(self):
        self.pinch_threshold = 0.04
        self.open_threshold = 0.17
        self.last_y = None
        self.last_x = None
        self.last_x_time = time.time()
        self.last_pinch_dist = None
        self.state_history = []
        self.history_limit = 3 

    def _get_distance(self, p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

    def detect_gesture(self, hand_landmarks):
        if not hand_landmarks: return "IDLE"
        
        lms = hand_landmarks.landmark
        thumb_tip, index_tip = lms[4], lms[8]
        palm_base, mid_base = lms[0], lms[9]

        pinch_dist = self._get_distance(index_tip, thumb_tip)
        f_up = [self._get_distance(lms[i], palm_base) > self.open_threshold for i in [8, 12, 16, 20]]
        up_cnt = sum(f_up)

        # 1. SWIPE (High Priority)
        curr_x, now = mid_base.x, time.time()
        if self.last_x is not None:
            dt = now - self.last_x_time
            if 0 < dt < 0.1:
                vel_x = (curr_x - self.last_x) / dt
                if vel_x > 2.2: return "ACTION_SWIPE_RIGHT"
                if vel_x < -2.2: return "ACTION_SWIPE_LEFT"
        self.last_x, self.last_x_time = curr_x, now

        # 2. ZOOM/ROTATE Logic (Tucked Fingers Only)
        # We only allow Zoom/Rotate if the other 3 fingers are definitely DOWN
        if up_cnt <= 1:
            # Check for Zoom Motion
            if self.last_pinch_dist is not None:
                diff = pinch_dist - self.last_pinch_dist
                self.last_pinch_dist = pinch_dist
                if diff > 0.01: return "ACTION_ZOOM_IN" # Increased threshold for stability
                if diff < -0.01: return "ACTION_ZOOM_OUT"
            
            self.last_pinch_dist = pinch_dist

            # If not zooming, check for static Rotate
            if pinch_dist < self.pinch_threshold:
                return "ACTION_ROTATE"

       # ... inside detect_gesture ...

        # 3. TRIGGER COMMANDS
        raw_cmd = "IDLE"
        
        if up_cnt >= 3: 
            raw_cmd = "ACTION_RESET"
        elif up_cnt == 1 and f_up[3]: 
            raw_cmd = "ACTION_CAPTURE"
            
        # TIGHTENED SELECT: Only if Index is up AND Thumb is very far away (> 0.1)
        elif up_cnt == 1 and f_up[0] and pinch_dist > 0.10: 
            raw_cmd = "ACTION_SELECT"

        # Apply stability filter to Triggers
        self.state_history.append(raw_cmd)
        if len(self.state_history) > self.history_limit: self.state_history.pop(0)
        
        stable_cmd = self.state_history[0] if len(set(self.state_history)) == 1 else "IDLE"

        # 4. FINAL ARBITRATION (The Fix)
        # If the HUD is seeing ZOOM/ROTATE/SCROLL, we should return THAT, not the stable_cmd
        
        # Check Scroll first
        if up_cnt == 2 and f_up[0] and f_up[1]:
            curr_y = index_tip.y
            if self.last_y is not None:
                dy = self.last_y - curr_y
                if dy > 0.05: return "ACTION_SCROLL_UP"
                elif dy < -0.05: return "ACTION_SCROLL_DOWN"
            self.last_y = curr_y

        # Check Zoom/Rotate (If tucked)
        if up_cnt <= 1:
            if self.last_pinch_dist is not None:
                diff = pinch_dist - self.last_pinch_dist
                self.last_pinch_dist = pinch_dist
                if diff > 0.008: return "ACTION_ZOOM_IN"
                if diff < -0.008: return "ACTION_ZOOM_OUT"
            self.last_pinch_dist = pinch_dist
            
            if pinch_dist < self.pinch_threshold:
                return "ACTION_ROTATE"

        # If no motion is found, return the stable trigger (Reset/Capture/Select)
        return stable_cmd