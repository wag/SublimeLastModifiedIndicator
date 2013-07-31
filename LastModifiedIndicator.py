import sublime_plugin
import sublime
import os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
IMG_PATH = os.path.join('..', os.path.basename(BASE_PATH), 'img')
settings = sublime.load_settings('LastModifiedIndicator.sublime-settings')

class LastModifiedIndicator(object):
    def __init__(self, view):
        self.view = view
        self.sel = self.view.sel()
        self.has_sel = len(self.sel) == 1

    @property
    def _range(self):
        return range(-3, 4) if settings.get('last_modified_indicator_multiline', True) else range(0, 1)

    def run(self):
        if self.has_sel:
            self.erase_regions()
            line = self.view.rowcol(self.view.sel()[0].begin())[0]
            for i in self._range:
                _line = line + i
                if _line < 0:
                    continue
                point = self.view.full_line(self.view.text_point(_line, 0))
                if os.path.exists(os.path.join(BASE_PATH, 'img', '%d%s' % (abs(i), '.png'))):
                    self.view.add_regions('lmi-outline-%d' % i, [point, ], 'lmi.outline.%d' % i,
                        os.path.join(IMG_PATH, str(abs(i))), sublime.HIDDEN)

    def erase_regions(self):
        if self.has_sel:
            for i in range(-3, 4):
                self.view.erase_regions('lmi-outline-%d' % i)


class LastModifiedIndicatorEventHandler(sublime_plugin.EventListener):
    def on_modified(self, view):
        if settings.get('last_modified_indicator', True):
            LastModifiedIndicator(view).run()
