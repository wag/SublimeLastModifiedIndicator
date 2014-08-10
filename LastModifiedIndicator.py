import sublime_plugin
import sublime
import os

BASE_PATH = os.path.basename(os.path.abspath(os.path.dirname(__file__))).replace('.sublime-package', '')
if int(sublime.version()) < 3014:
    PATH = '..'
    EXT = ''
else:
    PATH = 'Packages'
    EXT = '.png'
ICONS_PATH = '{0}/{1}/{2}'.format(PATH, BASE_PATH, 'icons')

ALL_SETTINGS = [
    'last_modified_indicator',
    'last_modified_indicator_multiline',
]


def settings_changed():
    for window in sublime.windows():
        for view in window.views():
            reload_settings(view)
            erase_regions(view)


def reload_settings(view):
    settings = sublime.load_settings('LastModifiedIndicator.sublime-settings')
    settings.clear_on_change(__name__)
    settings.add_on_change(__name__, settings_changed)

    view_settings = view.settings()
    for setting in ALL_SETTINGS:
        if settings.get(setting) is not None:
            view_settings.set(setting, settings.get(setting))

    if view_settings.get('last_modified_indicator') is None:
        view_settings.set('last_modified_indicator', True)

    return view_settings


def plugin_loaded():
    settings_changed()


def erase_regions(view):
    for i in range(-3, 4):
        view.erase_regions('lmi-outline-{0}'.format(i))


class LastModifiedIndicator(object):
    def __init__(self, view):
        self.view = view
        self.sel = self.view.sel()
        self.has_sel = len(self.sel) == 1

    @property
    def _range(self):
        return range(-3, 4) if self.view.settings().get('last_modified_indicator_multiline', True) else range(0, 1)

    def run(self):
        if self.has_sel:
            line = self.view.rowcol(self.view.sel()[0].begin())[0]
            erase_regions(self.view)
            for i in self._range:
                _line = line + i
                if _line < 0:
                    continue
                point = self.view.full_line(self.view.text_point(_line, 0))
                self.view.add_regions(
                    'lmi-outline-{0}'.format(i), [point, ],
                    'lmi.outline.{0}'.format(i),
                    '{0}/{1}'.format(ICONS_PATH, format(abs(i)) + EXT),
                    sublime.HIDDEN)


class LastModifiedIndicatorEventHandler(sublime_plugin.EventListener):
    def on_load(self, view):
        reload_settings(view)

    def on_new(self, view):
        reload_settings(view)

    def on_clone(self, view):
        reload_settings(view)

    def on_modified(self, view):
        if view.settings().get('last_modified_indicator', True):
            LastModifiedIndicator(view).run()

    def on_post_save(self, view):
        erase_regions(view)
