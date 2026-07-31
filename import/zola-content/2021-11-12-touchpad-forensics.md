+++
title = "Touchpad Forensics"
date = 2021-11-12
[extra]
banner="forensics"
+++

In this post we collect some notes on our experience debugging a faulty touchpad on Hyeyoung's Lenovo X1 (deepersea), which we suspect is a hardware issue.  Here are the steps we took to prove this conjecture before we ship the machine to Lenovo for repair.

<!-- more -->

1. Make sure a virtual terminal (vt) is available. Using a vt will suspend the X window system and thus prevent it from interfering with our analysis. As of Ubuntu 17.04 (maybe earlier), vts are not available by default.  To make a vt available, one must edit the file `/etc/systemd/logind.conf`, uncomment the line `NAutoVTs=6`, and restart the computer.
   
2. Determine the *input device handle* assigned to the touchpad using the command `cat /proc/bus/input/devices`. There will be a lot of output, but we just need to find the following block:
   
   ```sh
   I: Bus=0011 Vendor=0002 Product=0007 Version=01b1
   N: Name="SynPS/2 Synaptics TouchPad"
   P: Phys=isa0060/serio1/input0
   S: Sysfs=/devices/platform/i8042/serio1/input/input5
   U: Uniq=
   H: Handlers=mouse1 event5 
   B: PROP=5
   B: EV=b
   B: KEY=e520 10000 0 0 0 0
   B: ABS=660800011000003
   ```

   From the `H` field we determine that the device handle is `event5`.
   
3. Install the `evtest` diagnostic tool: `sudo apt install evtest`.

4. Switch to a virtual terminal using (e.g., `Ctrl`+`Alt`+`F2`, giving a mostly blank screen with a single `login:` prompt) and login using your username and password.

5. Run the `evtest` tool by entering the following command:

   ```
   sudo evtest /dev/input/event5 > ~/evtest.log
   ```
   
   This will start touchpad event logging, so immediately start a very brief test of just a single feature of the touchpad and then (quickly) stop event logging with `Ctrl`+`C`.
   
6. Inspect the resulting log file.

   Below is are excerpts from event log files collected from a normally functioning touchpad and a malfunctioning one.
   
   **Working Touchpad**

   ```
   Input driver version is 1.0.1
   Input device ID: bus 0x11 vendor 0x2 product 0x7 version 0x1b1
   Input device name: "SynPS/2 Synaptics TouchPad"
   Supported events:
     Event type 0 (EV_SYN)
     Event type 1 (EV_KEY)
       Event code 272 (BTN_LEFT)
       Event code 325 (BTN_TOOL_FINGER)
       Event code 328 (BTN_TOOL_QUINTTAP)
       Event code 330 (BTN_TOUCH)
       Event code 333 (BTN_TOOL_DOUBLETAP)
       Event code 334 (BTN_TOOL_TRIPLETAP)
       Event code 335 (BTN_TOOL_QUADTAP)
     Event type 3 (EV_ABS)
       Event code 0 (ABS_X)
         Value   5550
         Min     1264
         Max     5678
         Resolution      46
       Event code 1 (ABS_Y)
         Value   1754
         Min     1132
         Max     4720
         Resolution      60
       Event code 24 (ABS_PRESSURE)
         Value      0
         Min        0
         Max      255
       Event code 28 (ABS_TOOL_WIDTH)
         Value      0
         Min        0
         Max       15
       Event code 47 (ABS_MT_SLOT)
         Value      0
         Min        0
         Max        1
       Event code 53 (ABS_MT_POSITION_X)
         Value      0
         Min     1264
         Max     5678
         Resolution      46
       Event code 54 (ABS_MT_POSITION_Y)
         Value      0
         Min     1132
         Max     4720
         Resolution      60
       Event code 57 (ABS_MT_TRACKING_ID)
         Value      0
         Min        0
         Max    65535
       Event code 58 (ABS_MT_PRESSURE)
         Value      0
         Min        0
         Max      255
   Properties:
     Property type 0 (INPUT_PROP_POINTER)
     Property type 2 (INPUT_PROP_BUTTONPAD)
   Testing ... (interrupt to exit)
   Event: time 1636729221.197923, type 3 (EV_ABS), code 57 (ABS_MT_TRACKING_ID), value 125
   Event: time 1636729221.197923, type 3 (EV_ABS), code 53 (ABS_MT_POSITION_X), value 1597
   Event: time 1636729221.197923, type 3 (EV_ABS), code 54 (ABS_MT_POSITION_Y), value 4215
   Event: time 1636729221.197923, type 3 (EV_ABS), code 58 (ABS_MT_PRESSURE), value 22
   Event: time 1636729221.197923, type 1 (EV_KEY), code 330 (BTN_TOUCH), value 1
   Event: time 1636729221.197923, type 3 (EV_ABS), code 0 (ABS_X), value 1597
   Event: time 1636729221.197923, type 3 (EV_ABS), code 1 (ABS_Y), value 4215
   Event: time 1636729221.197923, type 3 (EV_ABS), code 24 (ABS_PRESSURE), value 22
   Event: time 1636729221.197923, type 1 (EV_KEY), code 325 (BTN_TOOL_FINGER), value 1
   Event: time 1636729221.197923, -------------- SYN_REPORT ------------
   Event: time 1636729221.222600, type 3 (EV_ABS), code 53 (ABS_MT_POSITION_X), value 1584
   Event: time 1636729221.222600, type 3 (EV_ABS), code 54 (ABS_MT_POSITION_Y), value 4265
   Event: time 1636729221.222600, type 3 (EV_ABS), code 58 (ABS_MT_PRESSURE), value 60
   Event: time 1636729221.222600, type 3 (EV_ABS), code 0 (ABS_X), value 1584
   Event: time 1636729221.222600, type 3 (EV_ABS), code 1 (ABS_Y), value 4265
   Event: time 1636729221.222600, type 3 (EV_ABS), code 24 (ABS_PRESSURE), value 60
   Event: time 1636729221.222600, -------------- SYN_REPORT ------------
   Event: time 1636729221.234486, type 3 (EV_ABS), code 54 (ABS_MT_POSITION_Y), value 4269
   Event: time 1636729221.234486, type 3 (EV_ABS), code 58 (ABS_MT_PRESSURE), value 64
   Event: time 1636729221.234486, type 3 (EV_ABS), code 1 (ABS_Y), value 4269
   Event: time 1636729221.234486, type 3 (EV_ABS), code 24 (ABS_PRESSURE), value 64
   Event: time 1636729221.234486, -------------- SYN_REPORT ------------
   Event: time 1636729221.246183, type 3 (EV_ABS), code 53 (ABS_MT_POSITION_X), value 1585
   Event: time 1636729221.246183, type 3 (EV_ABS), code 54 (ABS_MT_POSITION_Y), value 4271
   Event: time 1636729221.246183, type 3 (EV_ABS), code 58 (ABS_MT_PRESSURE), value 67
   Event: time 1636729221.246183, type 3 (EV_ABS), code 0 (ABS_X), value 1585
   Event: time 1636729221.246183, type 3 (EV_ABS), code 1 (ABS_Y), value 4271
   Event: time 1636729221.246183, type 3 (EV_ABS), code 24 (ABS_PRESSURE), value 67
   Event: time 1636729221.246183, -------------- SYN_REPORT ------------
   Event: time 1636729221.258146, type 3 (EV_ABS), code 54 (ABS_MT_POSITION_Y), value 4275
   Event: time 1636729221.258146, type 3 (EV_ABS), code 58 (ABS_MT_PRESSURE), value 69
   Event: time 1636729221.258146, type 3 (EV_ABS), code 1 (ABS_Y), value 4275
   Event: time 1636729221.258146, type 3 (EV_ABS), code 24 (ABS_PRESSURE), value 69
   ```
   
   **Broken Touchpad**





