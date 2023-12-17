class Percepts:
    def __init__(self) -> None:
        self.percepts = [False, False, False, False, False]

    def __getitem__(self, name: str) -> bool:
        if name == "stench":
            return self.percepts[0]
        elif name == "breeze":
            return self.percepts[1]
        elif name == "glitter":
            return self.percepts[2]
        elif name == "bump":
            return self.percepts[3]
        elif name == "scream":
            return self.percepts[4]
        raise Exception(f"Unknown percept: {name}")

    def __setitem__(self, name: str, value: bool):
        if name == "stench":
            self.percepts[0] = value
        elif name == "breeze":
            self.percepts[1] = value
        elif name == "glitter":
            self.percepts[2] = value
        elif name == "bump":
            self.percepts[3] = value
        elif name == "scream":
            self.percepts[4] = value
        else:
            raise Exception(f"Unknown percept: {name}")

    def __repr__(self) -> str:
        names = ["none"] * 5
        if self.percepts[0]:
            names[0] = "stench"
        if self.percepts[1]:
            names[1] = "breeze"
        if self.percepts[2]:
            names[2] = "glitter"
        if self.percepts[3]:
            names[3] = "bump"
        if self.percepts[4]:
            names[4] = "scream"
        return f"Percepts({names})"


