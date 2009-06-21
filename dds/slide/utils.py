import django

def register_signals(cls, signals_module=django.db.models.signals, **kwargs):
    for key, val in kwargs.items():
        signals_module.__getattribute__(key).connect(val, cls)
