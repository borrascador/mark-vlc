# Mark VLC

Allows creating and navigating annotated marks in a video playing in VLC. Marks are generated in a dokuwiki markup format and feature a table of contents, notes sections for each mark, and links to play from any marked timestamp.

Annotation files are automatically created in the same directory as the video file and are titled `annotations.dokuwiki`.

## Instructions

  1. Run `vlc --extraintf http --http-port 8088 --http-password pass FILENAME` to start VLC first.
  2. Install dependencies and run `main.py`.
  3. Start annotating!
   
You can open the annotations file in a program such as VSCode to add notes as you mark, but remember to save before annotating again or all unsaved changes will be lost!

## Hotkeys

  * `<cmd>+<shift>+<space>`: creates mark in file and resets file organization.
  * `<cmd>+<shift>+p`: plays or pauses video.
  * `<cmd>+<shift>+.`: skips to next mark.
  * `<cmd>+<shift>+,`: skips to previous mark.
  * `<cmd>+<shift>+d`: quits program.

## Sample Outline

"""
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

"""