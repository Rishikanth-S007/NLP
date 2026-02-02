import re

class CommandLogic:
    def __init__(self):
        """
        A professional, expanded vocabulary for a medical environment.
        Uses Regex patterns to ensure commands are caught even within full sentences.
        """
        self.vocabulary = {
            "ACTION_ZOOM_IN": [r"zoom in", r"magnify", r"closer", r"enlarge", r"increase scale"],
            "ACTION_ZOOM_OUT": [r"zoom out", r"back up", r"smaller", r"wide view", r"decrease scale"],
            "ACTION_ROTATE": [r"rotate", r"turn", r"spin", r"revolve", r"pivot", r"angle"],
            "ACTION_FREEZE": [r"freeze", r"stop", r"lock", r"hold", r"pause", r"done", r"finish"],
            "ACTION_RESET": [r"reset", r"original", r"home", r"center", r"recenter", r"default"],
            "ACTION_CAPTURE": [r"capture", r"snapshot", r"save", r"record", r"take photo"]
        }

    def get_action(self, text):
        """
        Matches raw speech against surgical command patterns.
        Returns the Action Key (e.g., ACTION_ZOOM_IN) or ACTION_UNKNOWN.
        """
        # Clean the text: lowercase and remove extra whitespace
        text = text.lower().strip()
        
        # Iterate through our dictionary to find a match
        for action, patterns in self.vocabulary.items():
            for pattern in patterns:
                # re.search allows the keyword to be anywhere in the user's sentence
                if re.search(pattern, text):
                    return action
        
        return "ACTION_UNKNOWN"