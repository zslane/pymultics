#include "terminal.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    TerminalWindow win;
    win.show();
    
    return app.exec();
}
