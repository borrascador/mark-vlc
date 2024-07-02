import os, sys, re
from python_vlc_http import HttpVLC
from pynput import keyboard
from urllib.parse import unquote
from itertools import chain

"""
SAMPLE OUTLINE:

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

# VLC CONNECTION CONFIG + SECRETS
LOCAL_HOST = 'http://127.0.0.1:8088'
LOCAL_USER = ''
LOCAL_PASS = 'pass'
LOCAL_ROOT = 'http://:pass@127.0.0.1:8088'

# HEADING CONSTANTS
H1 = '======'
H2 = '====='
H3 = '===='
H4 = '==='
H5 = '=='

#
## Hotkey functions
#

def on_activate_annotate():
    setup_annotation_file()
    seconds = get_current_seconds()
    clean_file(seconds)

def on_activate_play():
    vlc_client.play()

def on_activate_next():
    path = get_path()
    with open(path + "/annotations.dokuwiki", "r") as f:
        lines = f.readlines()
        sorted_times = get_sorted_times(lines, reverse=True)
        current_pos = get_current_seconds()
        next_closest = None
        for t in sorted_times:
            if t > current_pos:
                next_closest = t
        if next_closest:
            vlc_client.seek(next_closest)
            hhmmss = seconds_to_hhmmss(next_closest)
            print(f'Jumped to next mark: {hhmmss}')
        else:
            print('Jump failed: no next mark')

def on_activate_prev():
    path = get_path()
    with open(path + "/annotations.dokuwiki", "r") as f:
        lines = f.readlines()
        sorted_times = get_sorted_times(lines)
        current_pos = get_current_seconds()
        prev_closest = None
        for t in sorted_times:
            if t < current_pos:
                prev_closest = t
        if prev_closest:
            vlc_client.seek(prev_closest)
            hhmmss = seconds_to_hhmmss(prev_closest)
            print(f'Jumped to previous mark: {hhmmss}')
        else:
            print('Jump failed: no previous mark')

def on_activate_exit():
    sys.exit()

#
## Time helper functions
#

def get_current_seconds():
    return round(vlc_client.position() * vlc_client.media_length())

def seconds_to_hhmmss(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"

def hhmmss_to_seconds(hhmmss):
    match = re.search(r"\d{2}:\d{2}:\d{2}", hhmmss)
    if match:
        hhmmss = match[0]
    else:
        return -1
    hours, minutes, seconds = map(int, hhmmss.split(':'))
    return hours * 3600 + minutes * 60 + seconds

#
## Sorting helper functions
#

def get_sorted_times(lines, reverse=False):
    time_list = []
    for line in lines:
        seconds = hhmmss_to_seconds(line)
        if seconds > -1:
            time_list.append(seconds)
    return sorted(time_list, reverse=reverse)

def get_sorted_lines(lines, reverse=False):
    return sorted(lines, key=hhmmss_to_seconds, reverse=reverse)

#
## Main File Generating Function
#

def clean_file(seconds):
    path = get_path()
    new_lines = []
    with open(path + "/annotations.dokuwiki", "r") as rf:
        lines = rf.readlines()       # read

        open_section = None
        lines_by_section = {}
        section_list = []
        for line in lines:
            if line.startswith('='):
                open_section = line
                lines_by_section[line] = [line]
                if line not in section_list:
                    section_list.append(line)
            elif open_section:
                lines_by_section[open_section].append(line)
            # matches = re.findall(r"\[\[(.*?)\]\]", line)
            # if len(matches) == 2:
            #     print(matches)

        ## TITLE
        indices = [position for position, section_heading in enumerate(section_list) if section_heading.startswith(f'{H1} ')]
        if len(indices) == 0:
            movie_title_section = create_movie_title_section()
            TITLE = movie_title_section[0]
            lines_by_section[TITLE] = movie_title_section
        else:
            TITLE = section_list[indices[0]]

        ## SECTION ORDER
        SCENES = '===== Scenes =====\n'
        LINKS_TO_SCENES = '==== Links to Scenes ====\n'
        SCENE_LISTING = '==== Scene Listing ====\n'
        SECTION_ORDER = [TITLE, SCENES, LINKS_TO_SCENES, SCENE_LISTING]

        ## SCENES
        indices = [position for position, section_heading in enumerate(section_list) if SCENES in section_heading]
        if len(indices) == 0:
            section = SCENES
            lines_by_section[section] = [section, '\n']

        ## LINKS TO SCENES
        indices = [position for position, section_heading in enumerate(section_list) if LINKS_TO_SCENES in section_heading]
        if len(indices) == 0:
            section = LINKS_TO_SCENES
            lines_by_section[section] = [section, '\n']

        ## SCENE LISTING
        indices = [position for position, section_heading in enumerate(section_list) if SCENE_LISTING in section_heading]
        if len(indices) == 0:
            section = SCENE_LISTING
            lines_by_section[section] = [section, '\n']

        ## HANDLE SCENE LINKS + LISTINGS TOGETHER
        new_scene_link = create_scene_link(seconds)
        scene_links = [parse_scene_link(link) for link in (lines_by_section[LINKS_TO_SCENES] + new_scene_link) if link.startswith('  * [[#')]

        new_scene_section = create_scene_section(seconds)
        scene_headings = [parse_scene_heading(heading) for heading in (section_list + [new_scene_section[0]]) if heading.startswith(f'{H4} ')]

        # Depending on list concat order, prioritizes link or heading name in scene_dict
        # Currently prioritizes link name and performs sorting on combined dict
        scene_dict = dict(sorted(dict(scene_headings + scene_links).items()))

        scene_link_strings = [''.join(create_scene_link(seconds, name)) for (seconds, name) in scene_dict.items()]
        scene_heading_strings = list(chain(*[
            create_scene_section(seconds, name, lines_by_section, section_list)
            for (seconds, name) in scene_dict.items()
        ]))

        lines_by_section[LINKS_TO_SCENES] = lines_by_section[LINKS_TO_SCENES][0:2] + scene_link_strings + ['\n']

        for section_heading in SECTION_ORDER:
            new_lines = new_lines + lines_by_section[section_heading]
        new_lines = new_lines + scene_heading_strings

    with open(path + "/annotations.dokuwiki", "w") as wf:
        wf.write(''.join(new_lines)) # write
        print(f'Added new mark: {seconds_to_hhmmss(seconds)}')

#
## Text Read/Write Helper Functions
#

def create_play_link(seconds):
    return f'[[{LOCAL_ROOT}/requests/status.xml?command=seek&val={seconds}|PLAY SCENE]]'

def extract_movie_title():
    filename = get_path(get_filename=True)
    return filename.split(' - ')[0]

def create_movie_title_section():
    movie_title = extract_movie_title()
    return [f'{H1} {movie_title} {H1}\n', '\n']

def create_scene_link(seconds, name=''):
    hhmmss = seconds_to_hhmmss(seconds)
    play_link = create_play_link(seconds)
    if name:
        name = f' - {name}'
    return [f'  * [[#{hhmmss}{name}]] > {play_link}\n']

def create_scene_section(seconds, name='', lines_by_section=None, section_list=None):
    hhmmss = seconds_to_hhmmss(seconds)
    play_link = create_play_link(seconds)
    if name:
        name = f' - {name}'

    lines = []
    lines.append(f'{H4} {hhmmss}{name} {H4}\n')
    lines.append(f'\n')

    section_body = []
    if lines_by_section and section_list:
        indices = [position for position, section_heading in enumerate(section_list)
                   if hhmmss in section_heading and section_heading.startswith(f'{H4} ')]
        if len(indices) == 1:
            section_body = lines_by_section[section_list[indices[0]]][2:]
            return lines + section_body
    lines.append(f'  * {play_link}\n')
    lines.append(f'\n')
    return lines + section_body

def parse_scene_link(line):
    seconds = None
    name = ''
    seconds = hhmmss_to_seconds(line)
    matches = re.findall(r"- (.*?)\]\]", line)
    if matches:
        name = matches[0]
    return seconds, name

def parse_scene_heading(line):
    seconds = None
    name = ''
    seconds = hhmmss_to_seconds(line)
    matches = re.findall(r"- (.*?) =", line)
    if matches:
        name = matches[0]
    return seconds, name

#
## Filepath helper functions
#

def setup_annotation_file():
    path = get_path()
    # Check for annotation file in same location as video file
    # If it doesn't exist, create it.
    filename = path + "/annotations.dokuwiki"
    if not os.path.exists(filename):
        open(filename, 'w').close()

def get_path(get_filename=False):
    playlist_data = vlc_client.fetch_playlist()
    current_uri = dfs(playlist_data)
    # Returns video path in the following format (example):
    # file:///Users/jan/Movies/Yakuza%20Graveyard%20-%20RAW/title_t00.mkv
    # So we strip filename and fix the string format
    path = current_uri.replace('file://', '')
    path = unquote(path)
    if get_filename:
        return path.split('/')[-1]
    else:
        return '/'.join(path.split('/')[:-1])

def dfs(root_node):
    # Depth-first search
    stack = [root_node]
    while len(stack) > 0:
        current_node = stack.pop(0)
        if 'current' in current_node.keys():
            return current_node['uri']
        if 'children' in current_node.keys():
            for child in current_node['children']:
                stack.insert(0, child)

#
## Main program entry point
#

if __name__ == '__main__':
    try:
        # First run:
        # vlc --extraintf http --http-port 8088 --http-password pass FILENAME
        vlc_client = HttpVLC(LOCAL_HOST, LOCAL_USER, LOCAL_PASS)
    except:
        print('VLC connection failed!')
        print('Run `vlc --extraintf http --http-port 8088 --http-password pass FILENAME` to start VLC first.')
        print('Exiting.')
        sys.exit()

    setup_annotation_file()

    with keyboard.GlobalHotKeys({
        '<cmd>+<shift>+<space>': on_activate_annotate,
        '<cmd>+<shift>+p': on_activate_play,
        '<cmd>+<shift>+.': on_activate_next,
        '<cmd>+<shift>+,': on_activate_prev,
        '<cmd>+<shift>+d': on_activate_exit
    }) as h: h.join()
