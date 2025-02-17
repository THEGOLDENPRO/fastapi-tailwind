__all__ = (
    "BinaryNotFoundError",
)

class BinaryNotFoundError(Exception):
    """
    Exception thrown when a tailwindcss binary could NOT be found.

    tailwind.compile() has a chance of throwing this if your variation of fastapi-tailwind ships 
    with no binary which is very very unusual and only occurs if we've made a mistake packaging 
    or you are using some custom variation of the library, so there's no need to catch this.
    """
    ...