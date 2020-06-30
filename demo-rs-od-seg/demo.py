import cv2
import sys
import time
import datetime
import zmq
import numpy as np

from camera import Camera, RealSense, RGBDCamera
from config import *
from utils import *
from qt_widget import *

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5 import QtGui

from segmentation_service import SegmentationService
from tracking_service import TrackingService
from video import Video


if __name__ == '__main__':
    app = QApplication(sys.argv)

    if camera_mode == CameraMode.REALSENSE:
        camera = RealSense()
        camera.start()  
    elif camera_mode == CameraMode.WEBCAM:
        camera = Camera(video_index=0)
    elif camera_mode == CameraMode.KVS:
        camera = Camera(stream_name="beam-test-1")
    elif camera_mode == CameraMode.ZMQ:
        camera = RGBDCamera(ip="192.168.0.110")
    else:
        print("Camera Mode is not set")
        sys.exit(app.exec_())

    # Video thread
    video_thread = QtCore.QThread()
    video_thread.start()
    video = Video(camera)
    video.moveToThread(video_thread)

    # Segmentation service thread
    segmentation_thread = QtCore.QThread()
    segmentation_thread.start()
    segmentationService = SegmentationService(camera)
    segmentationService.moveToThread(segmentation_thread)
    
    # Tracking service thread
    tracking_thread = QtCore.QThread()
    tracking_thread.start()
    trackingService = TrackingService(camera)
    trackingService.moveToThread(tracking_thread)

    # Qt View
    rgb_viewer = ImageViewer()
    depth_viewer = ImageViewer()
    seg_viewer = ImageViewer()
    tracking_viewer = ImageViewer()
    table_viewer = TableViewer()

    grid_layout = QGridLayout()
    grid_layout.addWidget(rgb_viewer, 0, 0)
    grid_layout.addWidget(depth_viewer, 0, 1)
    grid_layout.addWidget(seg_viewer, 1, 0)
    grid_layout.addWidget(tracking_viewer, 1, 1)

    start_button = QPushButton('Start')
    seg_button = QPushButton('Segmentation')
    tracking_button = QPushButton('Tracking')
    clear_button = QPushButton('Clear')

    vertical_layout = QVBoxLayout()
    vertical_layout.addLayout(grid_layout)
    vertical_layout.addWidget(table_viewer.table)
    vertical_layout.addWidget(start_button)
    vertical_layout.addWidget(seg_button)
    vertical_layout.addWidget(tracking_button)
    
    layout_widget = QWidget()
    layout_widget.setLayout(vertical_layout)

    # Button Event
    start_button.clicked.connect(video.start)
    seg_button.clicked.connect(segmentationService.start)
    tracking_button.clicked.connect(trackingService.start)

    # Qt Event
    video.rgb_signal.connect(rgb_viewer.setImage)
    video.depth_signal.connect(depth_viewer.setImage)
    segmentationService.seg_signal.connect(seg_viewer.setImage)
    trackingService.tracking_signal.connect(tracking_viewer.setImage)

    main_window = QMainWindow()
    main_window.setCentralWidget(layout_widget)
    main_window.show()

    sys.exit(app.exec_())
