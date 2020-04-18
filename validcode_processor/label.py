import os
import cv2
import sys
import glob

if __name__ == '__main__':
    input_dir = "F:\\temp\\validCode\\train_data"
    files = os.listdir(input_dir)
    output_dir = "F:\\temp\\validCode\\label_data"
    for filename in files:
        filename_ts = filename.split(".")[0]
        filepath = os.path.join(input_dir, filename)
        im = cv2.imread(filepath)
        cv2.imshow("image", im)
        # 等待输入
        key = cv2.waitKey(0)
        if key == 27:
            sys.exit()
        if key == 13:
            continue
        char = chr(key)
        print(char)
        outfile = "{}_{}.png".format(char, filename_ts)
        outpath = os.path.join(output_dir, outfile)
        cv2.imwrite(outpath, im)
