import cv2
import numpy as np
import time
import os
import uuid
import traceback


def show(img):
    cv2.imshow('img', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def contours_sort(contours, method=0):
    """
        按照从左到右或从右到左的顺序将识别的轮廓排序
    :param contours:
    :param method:
    :return:
    """
    if method == 0:
        contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[0])
    else:
        contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[0], reverse=True)
    return contours


def prepare(img, thresh=100):
    origin_img = img
    im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # show(im_gray)
    ret, im_inv = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY_INV)
    # im_inv = cv2.adaptiveThreshold(im_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 21, 2)
    kernel = 1 / 16 * np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]])
    im_blur = cv2.filter2D(im_inv, -1, kernel)
    # show(im_blur)
    ret, im_res = cv2.threshold(im_blur, 127, 255, cv2.THRESH_BINARY)
    # show(im_res)
    im2, contours, hierarchy = cv2.findContours(im_res, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # show(im2)
    # print("%s = %d" % (img_path, len(contours)))
    contours = contours_sort(contours)
    return im_res, contours


def split(img_path, output_path, is_save):
    img = cv2.imread(img_path)
    im_res, contours = prepare(img, 100)
    if len(contours) != 4:
        im_res, contours = prepare(img, 127)

    # cv2.imwrite(os.path.join("F:\\temp\\validCode\\captcha", '%s.png' % str(uuid.uuid4()).replace('-', '')), im_res)

    result = []
    if len(contours) == 4:
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            box = np.int0([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])
            result.append(box)

        # print(result)
        # show(im_res)
        if is_save:
            for box in result:
                cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
                roi = im_res[box[0][1]:box[3][1], box[0][0]:box[1][0]]
                roistd = cv2.resize(roi, (30, 30))  # 将字符图片统一调整为30x30的图片大小
                # show(roistd)
                timestamp = int(time.time() * 1e6)  # 为防止文件重名，使用时间戳命名文件名
                filename = "{}.png".format(timestamp)
                filepath = os.path.join(output_path, filename)
                cv2.imwrite(filepath, roistd)
        return im_res, result


if __name__ == '__main__':
    input_path = "F:\\temp\\validCode\\pre"
    output_path = "F:\\temp\\validCode\\train_data"
    imgs = os.listdir(input_path)
    for img in imgs:
        img_path = os.path.join(input_path, img)
        try:
            split(img_path, output_path, True)
        except Exception as e:
            traceback.print_exc()

    # im = cv2.imread(os.path.join(input_path, '03fac90f8cdc4b5e959a1c428e60f70e.png'))
    # split(im, output_path)
