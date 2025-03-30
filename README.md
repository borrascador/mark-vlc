# Mark VLC

Allows creating and navigating annotated marks in a video playing in VLC. Marks are generated in a dokuwiki markup format and feature a table of contents, notes sections for each mark, and links to play from any marked timestamp.

Annotation files are automatically created in the same directory as the video file and are titled `annotations.dokuwiki`.

## Installation

**NOTE: Setup has only been tested on an M1 Mac using Python 3.11.5. If you experience any problems, please open an issue.**

  1. In the project folder, run `source venv/bin/activate` to activate the virtual environment.
  2. Run `pip install -e requirements.txt` to install dependencies.

## Instructions

  1. Run `vlc --extraintf http --http-port 8088 --http-password pass FILENAME` to start VLC first. `FILENAME` should be a full path, e.g. `/Users/foo/bar.mp4`
  2. If dependencies have been installed according to installation instructions, run `python -m main`.
  3. Start annotating! Output will be saved in dokuwiki format as a `.txt` file in the same directory as your video file by default. Custom output directory can be set with `-p` flag.

You can open the annotations file in a program such as VSCode to add notes as you mark, but remember to save before annotating again or all unsaved changes will be lost!

## Hotkeys

  * `<cmd>+<shift>+<space>`: creates mark in file and resets file organization.
  * `<cmd>+<shift>+p`: plays or pauses video.
  * `<cmd>+<shift>+.`: skips to next mark.
  * `<cmd>+<shift>+,`: skips to previous mark.
  * `<cmd>+<shift>+d`: quits program.

## Sample Outline

```
====== TITLE ======

[[LINK|START]]

Summary text

===== Scenes =====

==== Links to Scenes ====

  * [[#HH:MM:SS - SCENE SUMMARY 1]] > [[LINK|PLAY]]
  * [[#HH:MM:SS - SCENE SUMMARY 2]] > [[LINK|PLAY]]

==== Scene Listing ====

=== HH:MM:SS - SCENE SUMMARY 1 ===

  * [[LINK|PLAY SCENE]]
  * Description 1
    * More text

=== HH:MM:SS - SCENE SUMMARY 2 ===

  * [[LINK|PLAY SCENE]]
  * Description 2
    * More text and even more

```
