import cv2
import pickle

width, height = 107, 48

try:
    with open('CarParkPos', 'rb') as f:
        slotsList = pickle.load(f)
except:
    slotsList = list()


def delete_slot(x, y):
    for i, slots in enumerate(slotsList):
        x_, y_ = slots
        if x_ < x < x_ + width and y_ < y < y_ + height:
            slotsList.pop(i)


def mouse_click_handler(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        slotsList.append((x, y))

    if events == cv2.EVENT_RBUTTONDOWN:
        delete_slot(x, y)

    with open('SlotsPos', 'wb') as file:
        pickle.dump(slotsList, file)


while True:

    img = cv2.imread('carParkImg.png')
    for pos in slotsList:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)
    cv2.imshow('image', img)
    cv2.setMouseCallback('image', mouse_click_handler)
    cv2.waitKey(1)
