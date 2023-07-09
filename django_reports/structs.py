"""Re-usable collections and structures."""
import enum


class OptionMeta(enum.EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False

        return True


class Option(enum.Enum, metaclass=OptionMeta):
    def __str__(self):
        return str(self.value)
