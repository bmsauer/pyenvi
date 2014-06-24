from pydoc import writedoc
import shutil

modules = [
    "pyenvi.pyenvi",
    "pyenvi.exceptions",
    "pyenvi.pyenvi_run"
]

for module in modules:
    writedoc(module)
    shutil.move(module+".html","docs/"+module+".html")
