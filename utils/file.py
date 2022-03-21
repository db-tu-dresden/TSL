from pathlib import Path
from typing import Generator


class BadSuffixError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.message = message
        self.error = errors

    def __str__(self):
        errors = ", ".join(f"{x}: {self.error[x]}" for x in self.error)
        return f"{self.message} ({errors})"


class BadFormatError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.message = message
        self.error = errors

    def __str__(self):
        errors = ", ".join(f"{x}: {self.error[x]}" for x in self.error)
        return f"{self.message} ({errors})"


class RequiredFileNotFoundError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.message = message
        self.error = errors

    def __str__(self):
        errors = ", ".join(f"{x}: {self.error[x]}" for x in self.error)
        return f"{self.message} ({errors})"
