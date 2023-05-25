"""
Omniverse Kit example extension that demonstrates how to stream video (such as RTSP) to a dynamic texture using [OpenCV VideoCapture](https://docs.opencv.org/3.4/dd/d43/tutorial_py_video_display.html)
and [omni.ui.DynamicTextureProvider](https://docs.omniverse.nvidia.com/kit/docs/omni.ui/latest/omni.ui/omni.ui.ByteImageProvider.html#byteimageprovider).

TODO:
- [x] Investigate how to perform the color space conversion and texture updates in a separate thread
- [ ] Investigate how to avoid the color space conversion and instead use the native format of the frame provided by OpenCV
"""
import asyncio
from pathlib import Path

import carb
import carb.profiler
import omni.ext
import omni.kit.app
from omni.kit.quicklayout import QuickLayout
import omni.ui
from omni.ui import MainWindow

from .video import VideoScrubber


async def _load_layout(layout_file: str, keep_windows_open=False):
    """this private methods just help loading layout, you can use it in the Layout Menu"""
    for _ in range(3):
        await omni.kit.app.get_app().next_update_async()
    QuickLayout.load_file(layout_file, keep_windows_open)


class OmniVideoExample(omni.ext.IExt):
    def on_startup(self, ext_id):
        # stream = omni.kit.app.get_app().get_update_event_stream()
        # self._sub = stream.create_subscription_to_pop(self._update_streams, name="update")
        self._window = omni.ui.Window("OpenCV Video Scrubbing Example", width=800, height=200)
        with self._window.frame:
            with omni.ui.VStack():
                VideoScrubber("{robotica.example.video.scrubbing}/data/oceans.mp4")
                # VideoScrubber("{omni.cv-video.example}/data/oceans.mp4", width=256, height=144)
                VideoScrubber("{robotica.example.video.scrubbing}/data/source-sm.mp4")

        self._window.deferred_dock_in(target_window="Commands", active_window=omni.ui.DockPolicy.CURRENT_WINDOW_IS_ACTIVE)

    def on_shutdown(self):
        # self._sub.unsubscribe()
        self._window = None
