import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'

import time
import tensorflow as tf
import cv2
import numpy as np

from utils import label_map_util

# Only tested for tensorflow 2.4.1, opencv 4.5.1

# Model information
MODEL_NAME = 'efficientdet_d2'
PATH_TO_SAVED_MODEL = os.path.join(os.getcwd(), 'model_data_hagrid', MODEL_NAME, 'saved_model')
PATH_TO_LABELS = os.path.join(os.getcwd(), 'model_data_hagrid', MODEL_NAME, 'label_map.pbtxt')

# Load label map and obtain class names and ids
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
category_index = label_map_util.create_category_index(
    label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=19, use_display_name=True
    )
)


def visualise_on_image(image, bboxes, labels, scores, thresh):
    (h, w, d) = image.shape
    for bbox, label, score in zip(bboxes, labels, scores):
        if score > thresh:
            xmin, ymin = int(bbox[1] * w), int(bbox[0] * h)
            xmax, ymax = int(bbox[3] * w), int(bbox[2] * h)

            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(image, f"{label}: {int(score * 100)} %", (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 2)
    return image


def quantize_model(saved_model_dir):
    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,  # enable TensorFlow Lite ops.
        tf.lite.OpsSet.SELECT_TF_OPS  # enable TensorFlow ops.
    ]
    converter.allow_custom_ops = True
    tflite_quant_model = converter.convert()
    interpreter = tf.lite.Interpreter(model_content=tflite_quant_model)
    output_details = interpreter.get_output_details()
    input_details = interpreter.get_input_details()
    signature_details = interpreter.get_signature_list()
    print(input_details)
    print(output_details)
    print(signature_details)
    input_type = interpreter.get_input_details()[0]['dtype']
    print('input: ', input_type)
    output_type = interpreter.get_output_details()[0]['dtype']
    print('output: ', output_type)
    open(os.path.join(os.getcwd(), "quantize_model", "detector.tflite"), "wb").write(tflite_quant_model)


if __name__ == '__main__':

    # Load the model
    print("Loading saved model ...")
    detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
    print("Model Loaded!")

    # Open Video Capture (Camera)
    video_capture = cv2.VideoCapture(0)
    tic = time.time()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print('Error reading frame from camera. Exiting ...')
            break

        frame = cv2.flip(frame, 1)
        image_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
        # The model expects a batch of images, so also add an axis with `tf.newaxis`.
        input_tensor = tf.convert_to_tensor(image_np)[tf.newaxis, ...]

        # Pass frame through detector
        detections = detect_fn(input_tensor)
        # print(detections)
        # Detection parameters
        score_thresh = 0.4
        max_detections = 2

        # All outputs are batches tensors.
        # Convert to numpy arrays, and take index [0] to remove the batch dimension.
        # We're only interested in the first num_detections.
        scores = detections['detection_scores'][0, :max_detections].numpy()
        bboxes = detections['detection_boxes'][0, :max_detections].numpy()
        labels = detections['detection_classes'][0, :max_detections].numpy().astype(np.int64)
        labels = [category_index[n]['name'] for n in labels]
        # Display detections
        visualise_on_image(frame, bboxes, labels, scores, score_thresh)

        toc = time.time()
        fps = int(1 / (toc - tic))
        tic = toc
        cv2.putText(frame, f"FPS: {fps}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
        cv2.imshow("Hand theremin", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Exiting ...")
    video_capture.release()
    cv2.destroyAllWindows()

    #### model quantization ###
    # quantize_model(PATH_TO_SAVED_MODEL)