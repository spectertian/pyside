```
pip install pyinstaller


pyi-makespec --onefile --windowed --add-data "icons/*;icons/" --add-data "screenshots/*;screenshots/" --icon=icons/link.png main.py



pyinstaller --clean main.spec

```