import sys
from forms import StatGen
from PyQt5.QtWidgets import QApplication

import asyncio
from qasync import QEventLoop

if __name__ == '__main__':
    app = QApplication(sys.argv)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    ex = StatGen(loop)
    ex.show()

    while loop:
        loop.run_forever()
        if app.activeWindow() is None:
            sys.exit()
