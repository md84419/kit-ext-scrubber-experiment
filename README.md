# Omniverse kit-scrubber-experiment [robotica.example.video.scrubbing]

A scratch space for exploring and experimenting with a simple video scrubbing UI widget.

![](./exts/robotica.example.video.scrubbing/data/preview.gif)


# Getting Started
## Requirements
- NVIDIA Omniverse Launcher
- An Omniverse App (Create, Code, etc)
- Kit 104.1 or later
- Tested with Code 2022.3.3

```
> .\link_app.bat
> .\runbuild.bat
```

# Background
See https://discord.com/channels/827959428476174346/1090676075887067146 for more info.

The code is based in part on [JShrake's example code](https://github.com/jshrake-nvidia/kit-cv-video-example) for [OpenCV](https://docs.opencv.org/3.4/dd/d43/tutorial_py_video_display.html) and [DynamicTextureProvider](https://docs.omniverse.nvidia.com/kit/docs/omni.ui/latest/omni.ui/omni.ui.ByteImageProvider.html#byteimageprovider).  His code created a Prim plane in the viewport.
Mine creates a VideoScrubber widget in a dockable window.

This is example code. It is not ready for production use and has not been optimised. It is unlikley to scale well.


# Optimising thumbnail videos
For a video that will be displayed as 256x256 pixels, you want to create a thumbnail version of the video which is
256x256 resolution and exactly 256 frames long. The framerate of the thumbnail version doesn't matter other than you
ideally want every frame to be different (no duplicate frames). The video should be progressive rather than interfaced
for best results.


# Contributing
The source code for this repository is provided as-is. We only accept outside contributions from individuals who have
signed an Individual Contributor License Agreement.
