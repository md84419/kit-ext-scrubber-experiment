# Based on code from: https://github.com/jshrake-nvidia/kit-cv-video-example
# License: Apache 2.0 (https://github.com/jshrake-nvidia/kit-cv-video-example/blob/main/LICENSE)

import time

import cv2 as cv
import numpy as np

import carb
import carb.profiler
import omni.ui


class OpenCvVideoStream:
    """
    A small abstraction around OpenCV VideoCapture and omni.ui.DynamicTextureProvider,
    making a one-to-one mapping between the two
    Resources:
    - https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html
    - https://docs.opencv.org/3.4/dd/d43/tutorial_py_video_display.html
    - https://docs.omniverse.nvidia.com/kit/docs/omni.ui/latest/omni.ui/omni.ui.ByteImageProvider.html#omni.ui.ByteImageProvider.set_bytes_data_from_gpu
    """

    def __init__(self, name: str, stream_uri: str, thumbnail_pos: int):
        self.name = name
        self.uri = stream_uri
        self.texture_array = None
        self._position = thumbnail_pos
        try:
            # Attempt to treat the uri as an int
            # https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html#a5d5f5dacb77bbebdcbfb341e3d4355c1
            stream_uri_as_int = int(stream_uri)
            self._video_capture = cv.VideoCapture(stream_uri_as_int)
        except Exception:
            # Otherwise treat the uri as a str
            self._video_capture = cv.VideoCapture(stream_uri)
        self.fps: float = self._video_capture.get(cv.CAP_PROP_FPS)
        self.width: int = self._video_capture.get(cv.CAP_PROP_FRAME_WIDTH)
        self.height: int = self._video_capture.get(cv.CAP_PROP_FRAME_HEIGHT)
        self._total_frames: int = self._video_capture.get(cv.CAP_PROP_FRAME_COUNT)
        self._dynamic_texture = omni.ui.DynamicTextureProvider(name)
        self._byte_image = omni.ui.ByteImageProvider()
        self._last_read = time.time()
        self.is_ok = self._video_capture.isOpened()
        # If this FPS is 0, set it to something sensible
        if self.fps == 0:
            self.fps = 24

    @carb.profiler.profile
    def update_texture(self):
        # Rate limit frame reads to the underlying FPS of the capture stream
        now = time.time()
        time_delta = now - self._last_read
        if time_delta < 1.0 / self.fps:
            return
        self._last_read = now

        # Read the frame
        carb.profiler.begin(0, "read")
        ret, frame = self._video_capture.read()
        cv.waitKey(0)
        carb.profiler.end(0)
        # The video may be at the end, loop by setting the frame position back to 0
        # if not ret:
        #     self._video_capture.set(cv.CAP_PROP_POS_FRAMES, 0)
        #     self._last_read = time.time()
        #     return

        frame_num = int(self._position * self._total_frames)
        frame_num = max(0, min(frame_num, self._total_frames-1))
        self._video_capture.set(cv.CAP_PROP_POS_FRAMES, frame_num)

        # By default, OpenCV converts the frame to BGR
        # We need to convert the frame to a texture format suitable for RTX
        # In this case, we convert to BGRA, but the full list of texture formats can be found at
        # # kit\source\extensions\omni.gpu_foundation\bindings\python\omni.gpu_foundation_factory\GpuFoundationFactoryBindingsPython.cpp
        frame: np.ndarray

        carb.profiler.begin(0, "color space conversion")
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        carb.profiler.end(0)
        height, width, channels = frame.shape

        carb.profiler.begin(0, "set_bytes_data")
        self._dynamic_texture.set_data_array(frame, [width, height, channels])
        self._byte_image.set_data_array(frame, [width, height, channels])
        carb.profiler.end(0)

    def update_position(self, position: float):
        self._position = position
