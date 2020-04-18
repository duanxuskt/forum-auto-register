from utils import deserialize
import cv2
import numpy as np
from validcode_processor.splitter import split

if __name__ == '__main__':
    id_label_map = deserialize("dat\\id_label_map.data")
    # print(id_label_map)
    # model = cv2.ml.KNearest_create()
    # samples = np.loadtxt('dat\\samples.data', np.float32)
    # label_ids = np.loadtxt('dat\\label_ids.data', np.float32)
    # model.train(samples, cv2.ml.ROW_SAMPLE, label_ids)
    cv2.ml.KNearest_load("dat\\md.dat")
    img_path = 'F:\\temp\\validCode\\6JM6.png'
    im_res, boxes = split(img_path, None, False)
    # print(boxes)
    for box in boxes:
        roi = im_res[box[0][1]:box[3][1], box[0][0]:box[1][0]]
        roistd = cv2.resize(roi, (30, 30))
        # show(roistd)
        sample = roistd.reshape((1, 900)).astype(np.float32)
        ret, results, neighbours, distances = model.findNearest(sample, k=3)
        label_id = int(results[0, 0])
        label = id_label_map[label_id]
        print(label)
