import sublime_plugin
import sublime
import os

IMG_PATH = os.path.join('..', 'LastModifiedIndicator', 'img')


class LastModifiedIndicator(object):
    def __init__(self, view):
        self.view = view

    def run(self):
        sel = self.view.sel()
        if len(sel) == 1 and self.view.settings().get('last_modified_indicator'):
            line = self.view.rowcol(self.view.sel()[0].begin())[0]
            for i in range(-3, 4):
                point = self.view.full_line(self.view.text_point(line + i, 0))
                self.view.add_regions('lmi-outline-%d' % i, [point, ], 'lmi.outline.%d' % i, os.path.join(IMG_PATH, str(abs(i))), sublime.HIDDEN)


class LastModifiedIndicatorEventHandler(sublime_plugin.EventListener):
    def on_modified(self, view):
        LastModifiedIndicator(view).run()
