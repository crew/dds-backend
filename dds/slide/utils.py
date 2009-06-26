import django
from datetime import datetime


def register_signals(cls, signals_module=django.db.models.signals, **kwargs):
    """Registers signals by their dictionary arguments.
    For example,
        register_signals(SomeModel, pre_save=pre_save_handler)
    will translate into
        signals.pre_save.connect(pre_save_handler, SomeModel)
    """
    for key, val in kwargs.items():
        signals_module.__getattribute__(key).connect(val, cls)


def temp_upload_to(instance, filename):
    """Specifies a temporary upload path to keep the filename."""
    now = datetime.now().isoformat()
    return 'tmp/%s/%s' % (now, filename)
