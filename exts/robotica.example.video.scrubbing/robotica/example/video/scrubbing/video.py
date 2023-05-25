import asyncio
import re
import threading
from typing import List

import carb
import carb.profiler
import omni.ext             # provides omni.*
import omni.ui as ui
import omni.kit.app

from .opencv_model import OpenCvVideoStream
from .style import STYLE, PADDING


THUMBNAIL_POS = 0.2
FUDGE_X = 2.5
FUDGE_Y = 2.35


class _Video(ui.Widget):
    def __init__(self,  *args, **kwargs):
        """
        Create a Video widget without chrome.

        Args:
            url (str): Path to the file on the local file system. This path is passed to OpenCV
        """
        url = kwargs.get('url', args[0])
        url = self.__parse_url(url)
        self._video = url
        self._streams: List[OpenCvVideoStream] = []
        self._stream_threads: List[threading.Thread] = []

    def __parse_url(self, string: str):
        pattern = r"\{(.*?)\}"
        
        match = re.search(pattern, string)
        if match:
            manager = omni.kit.app.get_app().get_extension_manager()
            extension = manager.get_extension_path_by_module(match.group(1))
            remainder = string.replace('{'+match.group(1)+'}', "")
            return extension+remainder
        return string
        
    def create_image_provider_stream(self, stream_uri):
        image_name = f"Video{len(self._streams)}"
        video_stream = self.create_stream(stream_uri, image_name)

        if video_stream is not None:
            carb.log_info(f"Creating video stream {stream_uri} {video_stream.width}x{video_stream.height}")
            if self._zstack is not None:
                self._zstack.width = ui.Length(video_stream.width/FUDGE_X + PADDING*2)
                self._zstack.height = ui.Length(video_stream.height/FUDGE_X + PADDING*2)
            self._running = True
            i = len(self._streams) - 1
            thread = threading.Thread(target=self._update_stream, args=(i, ))
            thread.daemon = True
            thread.start()
            self._stream_threads.append(thread)
        return image_name

    def create_stream(self, stream_uri, image_name) -> OpenCvVideoStream:
        video_stream = OpenCvVideoStream(image_name, stream_uri, THUMBNAIL_POS)
        if not video_stream.is_ok:
            carb.log_error(f"Error opening stream: {stream_uri}")
            return
        self._streams.append(video_stream)
        return video_stream

    @carb.profiler.profile
    def _update_stream(self, i, callback=None):
        async def loop():
            while self._running:
                await asyncio.sleep(0.001)
                self._streams[i].update_texture()
        asyncio.run(loop())

    def destroy(self):
        # self._sub.unsubscribe()
        self._running = False
        for thread in self._stream_threads:
            thread.join()
        self._stream_threads = []
        for i in range(len(self._streams)):
            self._streams[i] = None
        self._streams = []


class VideoScrubber(_Video):
    def __init__(self, *args, **kwargs):
        """
        Create a Video scrubber widget with chrome styling.
        Mousing left and right over the the video allows one to scrub through the video

        Args:
            url (str): Path to the file on the local file system. This path is passed to OpenCV
        """
        super().__init__(*args, **kwargs)
        self._mouse_in: ui.Rectangle = None
        self._rect_initial_computed_width: float = None
        self._mouse_thread: threading.Thread = None
        self._build_ui()

    def _build_ui(self):
        with ui.VStack(style=STYLE):
            self._zstack = ui.ZStack()
            with self._zstack:
                self._rect = ui.Rectangle()
                self.create_image_provider_stream(self._video)
                if len(self._streams) == 0:
                    carb.log_error("OpenCv Failed.  No stream.")
                    self._image = ui.ImageWithProvider(alignment=ui.Alignment.CENTER_TOP)
                else:
                    self._rect.set_mouse_hovered_fn(lambda e, w=self._rect: self.mouse_hovered_fn(e, w))
                    self._image = ui.ImageWithProvider(self._streams[0]._byte_image, alignment=ui.Alignment.CENTER_TOP)
                self._placer = ui.Placer()
                with self._placer:
                    self._playhead = ui.Line(name="playhead", alignment=ui.Alignment.LEFT, width=1)
                    self._playhead.visible = False
        self._create_mouse_read_thread()

    def _create_mouse_read_thread(self):
        thread = threading.Thread(target=self._update_mouse)
        thread.daemon = True
        thread.start()
        self._mouse_thread = thread

    def mouse_hovered_fn(self, hovered: bool, widget: ui.Widget=None):
        """
        Callback to handle mouse entry to/exit from the VideoScrubber widget

        Args:
            hovered (bool): True if the mouse is over the widget, False if it has moved away
            widget (ui.Widget, optional): the widget instance handling the mouse events
        """
        if not hovered:
            self._mouse_in = None
            self._playhead.visible = False
            i = len(self._streams) - 1
            self._streams[i].update_position(THUMBNAIL_POS)  # On exit, display the thumbnail image
            return
        self._mouse_in = widget
        self._playhead.visible = True

    def _update_mouse(self):
        async def loop():
            while self._running:
                await asyncio.sleep(0.001)
                if self._mouse_in:
                    self.input = carb.input.acquire_input_interface()
                    self.mouse = omni.appwindow.get_default_app_window().get_mouse()

                    (x, _) = self.input.get_mouse_coords_pixel(self.mouse)

                    if hasattr(self._mouse_in, 'screen_position_x'):
                        rect = self._mouse_in
                        x = x - rect.screen_position_x - PADDING

                        if self._rect_initial_computed_width is None:
                            self._rect_initial_computed_width = rect.computed_width - PADDING*2

                        width2 = self._rect_initial_computed_width
                        x = max(0, min(x, width2))
                        normal_x = x/width2
                        self._placer.offset_x = x
                        try:
                            i = len(self._streams) - 1
                            self._streams[i].update_position(normal_x)
                        except Exception as e:
                            carb.log_error(f"OpenCv raised an exception: {e, e.with_traceback()}")

        asyncio.run(loop())

    def destroy(self):
        super().destroy()
        self._mouse_in = None

        if self._mouse_thread is not None:
            self._mouse_thread.join()
            self._mouse_thread = None
        self._image = None
