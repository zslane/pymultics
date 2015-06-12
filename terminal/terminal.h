#ifndef TERMINAL_H
#define TERMINAL_H

#include <cstdlib>
#include <iostream>
#include "qglobal.h"
#include <QApplication>
#include <QWidget>
#include <QString>
#include <QByteArray>
#include <QTcpSocket>
#include <QHostInfo>
#include <QTextEdit>
#include <QTextCursor>
#include <QLineEdit>
#include <QLabel>
#include <QFrame>
#include <QStyle>
#include <QMainWindow>
#include <QScrollBar>
#include <QPalette>
#include <QPainter>
#include <QTimer>
#include <QEvent>
#include <QBoxLayout>
#include <QInputDialog>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QActionGroup>
#include <QSettings>
#include <QStatusBar>
#include <QKeyEvent>
#include "data_packet.h"

inline double round(double x) { return double(int(x + 0.5)); }

class KeyboardIO: public QLineEdit
{
    Q_OBJECT

signals:

    void breakSignal();
    void lineFeed();

public:

    KeyboardIO(const QFont& font, const QString& color = "white", const QString& bkgdcolor = "black", QWidget* parent = 0);

protected:

    virtual void keyPressEvent(QKeyEvent* event);
};


class ScreenIO: public QTextEdit
{
    Q_OBJECT

private:

    bool m_connected;

public:

    ScreenIO(const QFont& font, const QString& color = "white", const QString& bkgdcolor = "black", QWidget* parent = 0);

    void setConnected(bool flag);

protected:

    virtual void paintEvent(QPaintEvent* event);

};


class TerminalIO: public QWidget
{
    Q_OBJECT

signals:

    void setNormalStatus(const QString&);
    void setConnectStatus(const QString&);
    void setErrorStatus(const QString&);

public:
    QTcpSocket* m_socket;
    QString     m_name;

protected:

    const char* ME;
    QString     m_host;
    int         m_port;
    int         m_com_port;
    ScreenIO*   m_output;
    KeyboardIO* m_input;

public:

    TerminalIO(const QString& phosphor_color, QWidget* parent = 0);

    ~TerminalIO();

protected:

    int _width(int nchars) const;
    int _height(int nlines) const;
    void get_text_colors(const QString& phosphor_color, QString& color, QString& bkgdcolor) const;

public slots:

    void startup();

    void socket_error(QAbstractSocket::SocketError error);

    void host_found();
    void connection_made();
    void connection_lost();

    void data_available();

    void send_string();
    void send_linefeed();
    void send_break_signal();
    void send_who_code();

    void written(qint64 nbytes);

    void shutdown();
    void reconnect();

    void display(const QString& txt);

public:

    void set_server_name(const QString& host);
    void set_server_port(int port);
    void reset();
    void set_phosphor_color(const QString& phosphor_color);
};


class TerminalWindow: public QMainWindow
{
    Q_OBJECT

signals:

    void transmitString(const QString&);
    void shutdown();
    void closed();

protected:

    QSettings   m_settings;
    TerminalIO* m_io;
    QPalette    m_palette;
    QLabel*     m_status_label;
    QMenu*      m_options_menu;
    QAction*    m_set_host_action;
    QAction*    m_set_port_action;
    QMenu*      m_phosphor_color_menu;
    QActionGroup* m_phosphor_color_group;
    QAction*    m_set_phosphor_vintg;
    QAction*    m_set_phosphor_green;
    QAction*    m_set_phosphor_amber;
    QAction*    m_set_phosphor_white;
    QAction*    m_reconnect_action;

public:

    TerminalWindow(QWidget* parent = 0);

private:

    void setup_menus();
    void set_phosphor_color(const QString& color);
    void set_status(const QString& txt);

private slots:

    void startup();

    void set_phosphor_color_vintg();
    void set_phosphor_color_green();
    void set_phosphor_color_amber();
    void set_phosphor_color_white();

    void enable_reconnect();
    void disable_reconnect();

    void set_normal_status(const QString& txt);
    void set_connect_status(const QString& txt);
    void set_error_status(const QString& txt);

    void set_host_dialog();
    void set_port_dialog();

public slots:

    void disconnect();

protected:

    virtual void closeEvent(QCloseEvent* event);
};

#endif // TERMINAL_H
