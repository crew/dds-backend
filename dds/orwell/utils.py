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


def acquire_pk(self):
    """Pre-allocate the primary key by creating an empty object and saving
    it, but only if needed.
    """
    if not self.pk:
        temp = self.__class__()
        super(temp.__class__, temp).save()
        self.pk = temp.pk
    return self.pk


def scaffolded_save(self, func, *args, **kwargs):
    """Adds a scaffold option. When scaffold is True, the file field
    is not renamed."""
    # Create the object first
    acquire_pk(self)
    # Load the file onto the file system
    super(self.__class__, self).save(*args, **kwargs)
    # Do things with the file
    func(self)
    # Final save.
    super(self.__class__, self).save(*args, **kwargs)
