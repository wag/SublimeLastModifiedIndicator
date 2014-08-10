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
    'last_modified_indicator_file_save_clear',
]

user_settings = None
lmi_settings = None
settings = {}


def init_settings():
    globals()['user_settings'] = sublime.load_settings('Preferences.sublime-settings')
    globals()['lmi_settings'] = sublime.load_settings('LastModifiedIndicator.sublime-settings')
    lmi_settings.clear_on_change(__name__)
    lmi_settings.add_on_change(__name__, settings_changed)
    user_settings.clear_on_change(__name__)
    user_settings.add_on_change(__name__, settings_changed)
    settings_changed()


def settings_changed():
    for value in ALL_SETTINGS:
        user_value = user_settings.get(value)
        settings[value] = user_value if user_value is not None else lmi_settings.get(value)

    for window in sublime.windows():
        for view in window.views():
            reload_settings(view)
            erase_regions(view)


def reload_settings(view):
    view_settings = view.settings()
    for value in ALL_SETTINGS:
        if settings.get(value) is not None:
            view_settings.set(value, settings.get(value))

    if view_settings.get('last_modified_indicator') is None:
        view_settings.set('last_modified_indicator', True)


def plugin_loaded():
    init_settings()


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
        return range(-3, 4) if settings.get('last_modified_indicator_multiline', True) else range(0, 1)

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
        if settings.get('last_modified_indicator', True):
            LastModifiedIndicator(view).run()

    def on_post_save(self, view):
        if settings.get('last_modified_indicator_file_save_clear', False):
            erase_regions(view)
