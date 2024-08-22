```
pip install pyinstaller


pyi-makespec --onefile --windowed --add-data "icons/*;icons/" --add-data "screenshots/*;screenshots/" --icon=icons/your_icon.ico --name "screen" main.py


pyinstaller --clean screen.spec

```