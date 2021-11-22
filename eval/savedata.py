import pickle

class FrameSaver:

    def __init__(self, filename):
        self.frames = []
        self.filename = filename
        
    def saveFrame(self, img, speeds, errors):
        self.frames.append([img, speeds, errors])

        if len(self.frames) > 100:
            print("saving frames")
            frames = self.frames
            self.save(frames)
            self.frames = []

    def save(self, frames):
        f = open(self.filename, "wb")
        pickle.dump(frames, f)
        f.close()        