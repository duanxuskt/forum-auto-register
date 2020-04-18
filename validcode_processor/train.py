import os
import numpy as np
import cv2
from utils import serialize, deserialize


def save_data():
    label_dir = "F:\\temp\\validCode\\label_data"
    filenames = os.listdir(label_dir)
    samples = np.empty((0, 900))
    labels = []
    for filename in filenames:
        filepath = os.path.join(label_dir, filename)
        label = filename.split(".")[0].split("_")[0]
        labels.append(label)
        im = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        sample = im.reshape((1, 900)).astype(np.float32)
        samples = np.append(samples, sample, 0)
        samples = samples.astype(np.float32)
        unique_labels = list(set(labels))
        unique_ids = list(range(len(unique_labels)))
        label_id_map = dict(zip(unique_labels, unique_ids))
        id_label_map = dict(zip(unique_ids, unique_labels))
        label_ids = list(map(lambda x: label_id_map[x], labels))
        label_ids = np.array(label_ids).reshape((-1, 1)).astype(np.float32)

    # responses = np.array(labels, np.float32)
    # responses = responses.reshape((responses.size, 1))

    np.savetxt('dat\\samples.data', samples)
    np.savetxt('dat\\label_ids.data', label_ids)
    serialize("dat\\id_label_map.data", id_label_map)
    id_label_map = deserialize("dat\\id_label_map.data")
    print(id_label_map)


def create_ANN(hidden=20):
    ann = cv2.ml.ANN_MLP_create()  # 建立模型
    ann.setTrainMethod(cv2.ml.ANN_MLP_RPROP | cv2.ml.ANN_MLP_UPDATE_WEIGHTS)  # 设置训练方式为反向传播
    ann.setActivationFunction(
        cv2.ml.ANN_MLP_SIGMOID_SYM)  # 设置激活函数为SIGMOID，还有cv2.ml.ANN_MLP_IDENTITY,cv2.ml.ANNMLP_GAUSSIAN
    ann.setLayerSizes(np.array([784, hidden, 10]))  # 设置层数，输入784层，输出层10
    ann.setTermCriteria((cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 0.1))  # 设置终止条件
    return ann


def train(ann, samples=10000, epochs=1):
    # tr:训练数据集; val:校验数据集; test:测试数据集;
    tr, val, test = wrap_data()

    for x in range(epochs):
        counter = 0
        for img in tr:
            if (counter > samples):
                break
            if (counter % 1000 == 0):
                print("Epoch %d: Trained %d/%d" % (x, counter, samples))
            counter += 1
            data, digit = img
            ann.train(np.array([data.ravel()], dtype=np.float32), cv2.ml.ROW_SAMPLE,
                      np.array([digit.ravel()], dtype=np.float32))
        print("Epoch %d complete" % x)
    return ann, test


def vectorized_result(j):
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e


def wrap_data():
    # tr_d数组长度为50000，va_d数组长度为10000，te_d数组长度为10000
    tr_d, va_d, te_d = load_data()

    # 训练数据集
    training_inputs = [np.reshape(x, (900, 1)) for x in tr_d[0]]
    training_results = [vectorized_result(y) for y in tr_d[1]]
    training_data = list(zip(training_inputs, training_results))

    # 校验数据集
    validation_inputs = [np.reshape(x, (900, 1)) for x in va_d[0]]
    validation_data = list(zip(validation_inputs, va_d[1]))

    # 测试数据集
    test_inputs = [np.reshape(x, (900, 1)) for x in te_d[0]]
    test_data = list(zip(test_inputs, te_d[1]))
    return (training_data, validation_data, test_data)


if __name__ == '__main__':
    id_label_map = deserialize("dat\\id_label_map.data")
    samples = np.loadtxt('dat\\samples.data', np.float32)
    label_ids = np.loadtxt('dat\\label_ids.data', np.float32)
    model = cv2.ml.KNearest_create()
    # model = cv2.ml.Boost_create()
    model.train(samples, cv2.ml.ROW_SAMPLE, label_ids)
    model.save("dat\\md.dat")
    cv2.ml.SVM_load()
