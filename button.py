import cv2

class Button:
    def __init__(self, pos, width, height, text):
        self.pos = pos
        self.width = width
        self.height = height
        self.text = text

    def draw(self, img):
        x, y = self.pos
        cv2.rectangle(img, (x, y), (x + self.width, y + self.height), (255, 255, 255), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + self.width, y + self.height), (0, 0, 0), 2)
        cv2.putText(img, self.text, (x + 30, y + 65), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 0, 0), 2)

    def is_clicked(self, x, y):
        return self.pos[0] < x < self.pos[0] + self.width and self.pos[1] < y < self.pos[1] + self.height
