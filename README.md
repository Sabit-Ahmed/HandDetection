# Hand Detection using Coco Hand, Ego Hand and TV-Hand Datasets

This is a hands detector that uses different models (i.e. SSD_mobilenet_v2_fpn_320, centernet_mobilenet_v2_fpn_512, centernet_resnet_v2_fpn_512, etc.) 
trained on different datasets (i.e. coco hand, ego hand, tv hand datasets etc.).

Acknowledgements:
- https://github.com/molyswu/hand_detection/blob/temp/hand_detection/egohands_dataset_clean.py
- https://github.com/datitran/raccoon_dataset/blob/master/generate_tfrecord.py
- https://github.com/aalpatya/detect_hands
- https://aalpatya.medium.com/train-an-object-detector-using-tensorflow-2-object-detection-api-in-2021-a4fed450d1b9

Requires tensorflow 2, (tested on tensorflow 2.4.1)
and OpenCV 4 (tested on OpenCV 4.2.1)

# Live Hand Detection only
**python3 webcam_detect_hands.py**
    
![out1](https://github.com/Sabit-Ahmed/HandDetection/blob/master/HandDetection.gif)


TODO: Put camera frame reading and processing into multi-threading
