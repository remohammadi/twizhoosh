import importlib

from core.smart_handlers.base.base_handler import JustRepliedException
from core.utils.logging import debug
from core.utils import farsi_tools
from core.settings import INSTALLED_HANDLERS


def load_handlers():
    handlers = []
    for handler in INSTALLED_HANDLERS:
        (package_name, dot, class_name) = handler.rpartition('.')
        module = importlib.import_module(package_name)
        handlers.append(getattr(module, class_name))
    return handlers


class SmartHandlersManager:
    '''
    A timeline update dispatcher between Smart Handlers
    '''

    def __init__(self, twitter, *args, **kwargs):
        short_term_memory = {}
        handler_classes = load_handlers()
        self.smart_handlers = [
            handler(twitter, short_term_memory) for handler in handler_classes]

    def on_timeline_update(self, data):
        try:
            data['text'] = farsi_tools.normalize(data['text'])
            for smart_handler in self.smart_handlers:
                smart_handler.timeline_update(data)
        except JustRepliedException as e:
            debug(u'Just replied with:\n {0}'.format(e.tweet))
