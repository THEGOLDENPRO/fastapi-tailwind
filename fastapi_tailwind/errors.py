__all__ = (
    "OSNotSupported"
)

class OSNotSupported(Exception):
    """Exception thrown when compile() detects an OS that is not supported by the Tailwind binaries."""
    ...