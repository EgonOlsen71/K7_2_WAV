"""# K7 to 1200 Baud WAV Converter

A simple Python utility to convert `.k7` tape image files (used by the **Philips VG5000** home computer and similar systems) into 1200 Baud `.wav` audio files for reliable loading on real hardware.

---

## Overview

This tool was created using **Google's Antigravity** to solve a common hardware reliability issue: standard tape conversion utilities included with MAME default to 2400 Baud. On physical VG5000 hardware, 2400 Baud is often too fast and prone to read errors.

By converting `.k7` tape images into 1200 Baud `.wav` audio files, the playback becomes far more tolerant and reliable when fed into original vintage hardware via audio jacks, cassette adapters, or physical tapes.

---

## Features

- **Reliable Signal Rate:** Converts `.k7` tape images specifically into 1200 Baud `.wav` audio format.
- **Batch Conversion:** Automatically processes all `.k7` files in a target directory.
- **Minimal Dependencies:** Standard Python script requiring no extra complex setup.

---

## Prerequisites

- **Python 3.x**

---

## Usage Instructions

1. **Configure Directory Path:**  
   Open the Python script in a text editor and update the folder path inside the `main()` function to point to your folder containing `.k7` files:
   ```python
   def main():
       # Set your folder path here
       workspace_dir = "./k7_files"
       # ...
