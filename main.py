import cv2
import pickle
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db
import threading
import time
import schedule

cred = credentials.Certificate("fastpark-13faf-firebase-adminsdk-jd384-0c75064bbb.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': "https://fastpark-13faf-default-rtdb.asia-southeast1.firebasedatabase.app"
})

from threading import Timer


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


width, height = 107, 48

vid = cv2.VideoCapture('carPark.mp4')

with open('CarParkPos', 'rb') as f:
    slotsList = pickle.load(f)

data = []
curr_id = 0
for slot in slotsList:
    a = [slot[0], slot[1], curr_id]
    data.append(a)
    curr_id += 1


def display_slots(img):
    for pos in slotsList:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)


def upload_to_firebase(temp):
    start = time.time()
    ref = db.reference('parking_lots/demo')
    users_ref = ref.child('slots')
    users_ref.set({
        'slots': temp
    }
    )
    end = time.time()
    print(end - start, 'secs')


def checkSlots(img, img1):
    spaceCounter = 0
    temp = []
    for pos in data:
        x, y, slot_id = pos
        croped = img[y:y + height, x:x + width]
        # cv2.imshow(str(x * y), croped)

        count = cv2.countNonZero(croped)
        status = -1
        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            status = 1

        else:
            color = (0, 0, 255)
            thickness = 2
            status = 0

        dic = {
            'slot_id': slot_id,
            'status': status
        }

        temp.append(dic)
        pos1 = [pos[0], pos[1]]
        cv2.rectangle(img1, pos1, (pos[0] + width, pos[1] + height), color, thickness)
    return temp

t1 = None
while True:
    if vid.get(cv2.CAP_PROP_POS_FRAMES) == vid.get(cv2.CAP_PROP_FRAME_COUNT):
        vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = vid.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)

    median = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(median, kernel, iterations=1)
    temp = checkSlots(dilated, img)
    if t1 == None or (t1 and t1.is_alive()==False):
        print('here',t1)

        t1 = threading.Thread(target=upload_to_firebase, args=(temp,))
        t1.start()

    cv2.imshow('fuk u', img)
    cv2.waitKey(5)
    # print(t1.is_alive())
    print('jello')
