import django


def register_signals(cls, signals_module=django.db.models.signals, **kwargs):
    for key, val in kwargs.items():
        signals_module.__getattribute__(key).connect(val, cls)


def temp_upload_to(instance, filename):
    """Specifies a temporary upload path to keep the filename."""
    now = datetime.now().isoformat()
    return 'tmp/%s/%s' % (now, filename)
