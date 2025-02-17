from fastapi_tailwind.binary import get_tailwind_binary_path

def test_get_tailwind_binary():
    assert get_tailwind_binary_path() is not None