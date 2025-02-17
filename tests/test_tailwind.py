import os
from fastapi_tailwind import tailwind

def test_tailwind_compile():
    os.chdir("./examples/hello-world-app")

    popen = tailwind.compile("./static/output.css")

    assert popen.wait() == 0