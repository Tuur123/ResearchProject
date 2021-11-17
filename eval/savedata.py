import cv2
import pickle

class FrameSaver:

    def __init__(self, fileName):
        self.frames = []
        self.f = open(fileName, "w")

    def saveFrame(self, img, speeds, errors):
        self.frames.append([img, speeds, errors])

    def save(self):
        pickle.dump(self.frames, self.f)
        self.f.close()