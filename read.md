```
pip install pyinstaller


pyi-makespec --onefile --windowed --add-data "icons/*;icons/" --add-data "screenshots/*;screenshots/" --icon=icons/link.png --name "screen" main.py


pyinstaller --clean screen.spec
pyinstaller screen.spec

```