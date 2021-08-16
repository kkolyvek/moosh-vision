# IMPORT PACKAGES
import cv2
import time
import threading
from queue import Queue
from imutils import resize

# IMPORT LOCAL FILES
from processImage import brightnessContrast

"""
Video stream from drone stream seems to be choppy and unstable - could be due ot OpenCV playback or drone connection or whatever. To fix:
1) Place recieved footage into a Queue to edit - delay x seconds to allow Queue to fill
2) After delay, edit frames and put into a separate Queue
3) After another delay, display frames at correct FPS from edited Queue
"""

# CLASS DEFINITION


class VideoStream:
    """ An instance of a video stream """
    # CLASS VARIABLES
    inputStack = Queue(0)
    editStack = Queue(0)

    def __init__(self, src, fps) -> None:
        # INSTANCE VARIABLES
        self.source = cv2.VideoCapture(src)
        self.baseFps = fps
        self.fps = fps
        # self.fpsOpenCV = self.source.get(cv2.CAP_PROP_FPS)
        # print(self.fpsOpenCV)
        self.ms = round(1 / self.fps * 1000)

        # brightness/contrast values [alpha = 1, beta = 0]
        self.bc = [float(1), float(0)]

        # PLAYBACK SPEED AUTOMATION
        self.playbackSpeedEditable = True
        self.framesSinceLastChange = 0

        # THREADS AND MISC.
        self.inputThread = None
        self.editThread = None

        self.is_streaming = False
        self.windowName = "Test Window"

    # METHODS
    def readFrame(self, inputStack):
        print('reading frames')
        while self.is_streaming == True:
            ret, frame = self.source.read()
            if not ret:
                self.stop()
            inputStack.put(frame)

    def editFrame(self, inputStack, editStack, bc):
        print('editing frames')
        while self.is_streaming == True:
            frame = inputStack.get()

            # Do some frame edits here
            frame = resize(frame, width=1920)
            frame = brightnessContrast(frame, bc[0], bc[1])

            editStack.put(frame)

    def displayFrame(self, bc):
        if self.editStack.empty() or self.is_streaming == False:
            self.stop()
        else:
            # method to automate playback speed
            '''
            This is a little bit hacky -- :
            IF 10 frames pass (to give the program a second to catch up),
            THEN add to the fps based on the difference between the baseline queue size and the current queue size
            Note: This seems to work best if you have an initial GOOD ESTIMATE that is not TOO FAR OFF so that the swing isn't too great
            '''
            if abs(self.baseline - self.editStack.qsize()) > (self.baseline / 100 * 10):
                self.playbackSpeedEditable = True

            if self.framesSinceLastChange >= self.baseline / 2:
                # self.fps = self.fps - \
                #     ((self.baseline - self.editStack.qsize()) * 0.25)
                diff = self.baseline - self.editStack.qsize()
                if diff != 0:
                    # keep sign but only change fps by one
                    self.fps = self.fps - (diff / abs(diff))
                    # cap fps:
                    if self.fps > self.baseFps + 5:
                        self.fps = self.baseFps + 5
                    elif self.fps < self.baseFps - 5:
                        self.fps = self.baseFps - 5
                    self.ms = round(1 / self.fps * 1000)
                    self.framesSinceLastChange = 0
                    self.playbackSpeedEditable = False

            if self.playbackSpeedEditable == True:
                self.framesSinceLastChange += 1

            # Take frame from the edited stack to display at specified rate
            frame = self.editStack.get()

            cv2.putText(frame, "InputStack Size: {}".format(self.inputStack.qsize()),
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            cv2.putText(frame, "EditStack Size: {}".format(self.editStack.qsize()),
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            cv2.putText(frame, "Playback FPS: {}".format(
                self.fps), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

            cv2.putText(frame, "Alpha: {:.2f}".format(
                bc[0]), (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            cv2.putText(frame, "Beta: {}".format(
                bc[1]), (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

            cv2.imshow(self.windowName, frame)

            # Display window to FPS of video (in whole integer ms)
            key = cv2.waitKey(self.ms)

            # QUIT PROGRAM
            if key == ord("q"):
                self.stop()

            # CHANGE BRIGHTNESS CONTRAST
            if key == ord("o"):
                bc[0] -= 0.2
                # print(self.alpha)
            if key == ord("p"):
                bc[0] += 0.2
                # print(self.alpha)
            if key == ord("k"):
                bc[1] -= 10
                # print(self.beta)
            if key == ord("l"):
                bc[1] += 10
                # print(self.beta)

            # CHANGE PLAYBACK SPEED
            if key == ord("m"):
                self.fps += 1
                self.ms = round(1 / self.fps * 1000)
            if key == ord("n"):
                self.fps -= 1
                self.ms = round(1 / self.fps * 1000)

    def start(self):
        self.is_streaming = True

        # start separate threads for reading and editing (outputThread is on main thread)
        self.inputThread = threading.Thread(
            target=self.readFrame, args=(self.inputStack,))
        self.editThread = threading.Thread(
            target=self.editFrame, args=(self.inputStack, self.editStack, self.bc))

        # set up window
        cv2.namedWindow(self.windowName, cv2.WINDOW_AUTOSIZE)
        # cv2.namedWindow(self.windowName, cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty(
        #     self.windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # give each worker thread a headstart to fill stacks
        self.inputThread.start()
        time.sleep(1)
        self.editThread.start()
        time.sleep(1)

        # run display on main thread
        self.baseline = self.editStack.qsize()
        print(self.baseline)
        while self.is_streaming == True:
            self.displayFrame(self.bc)

    def stop(self):
        self.is_streaming = False
        self.inputThread.join()
        self.editThread.join()
        cv2.destroyAllWindows
