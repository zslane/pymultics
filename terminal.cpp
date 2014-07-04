#include <stdlib>
#include "QApplication.h"
#include "QWidget.h"
#include "QString.h"
#include "QByteArray.h"
#include "QTcpSocket.h"
#include "QTextEdit.h"
#include "QTextCursor.h"
#include "QLineEdit.h"
#include "QLabel.h"
#include "QFrame.h"
#include "QMainWindow.h"
#include "QPalette.h"
#include "QTimer.h"
#include "QVBoxLayout.h"
#include "QMenu.h"
#include "QAction.h"
#include "QActionGroup.h"

int N_HORZ_CHARS = 80;
int N_VERT_LINES = 25;
            
const char* DEFAULT_SERVER_NAME = "localhost";
int DEFAULT_SERVER_PORT = 6800;
const char* DEFAULT_PHOSPHOR_COLOR = "green";

char CONTROL_CODE       = char(17); // Device Control 1
char UNKNOWN_CODE       = char(0);
char ECHO_NORMAL_CODE   = char(1);
char ECHO_PASSWORD_CODE = char(2);
char ASSIGN_PORT_CODE   = char(26); // Substitute
char END_CONTROL_CODE   = char(4);  // End of Transmission

char LINEFEED_CODE      = char(10); // Linefeed
char BREAK_CODE         = char(24); // Cancel

const char* TEXT_EDIT_STYLE_SHEET = "QTextEdit { font-family: '%s'; font-size: %dpt; color: %s; background: black; border: 0px; }";
const char* LINE_EDIT_STYLE_SHEET = "QLineEdit { font-family: '%s'; font-size: %dpt; color: %s; background: black; }";

class DataPacket: public
{
protected:

    char* m_data;
    long  m_size;
    
public:

    DataPacket::DataPacket() : m_data(0), m_size(0)
    {
    }
    
    DataPacket::DataPacket(const QByteArray& byte_array)
    {
        m_size = byte_array.size() + 1;
        m_data = new char [m_size];
        m_data[m_size - 1] = '\0';
        std::memcpy(m_data, byte_array.data(), m_size);
    }
    
    DataPacket::DataPacket(const DataPacket& data_packet)
    {
        m_size = data_packet.size();
        m_data = new char [m_size];
        std::memcpy(m_data, data_packet.data(), m_size);
    }
    
    DataPacket::~DataPacket()
    {
        delete [] m_data;
    }
    
    bool is_empty() const
    {
        return (m_size == 0);
    }
    
    bool is_control_seq() const
    {
        if ((m_size > 2) && (m_data[0] == CONTROL_CODE))
        {
            for (const char* c = m_data; *c; ++c)
                if (c == END_CONTROL_CODE)
                    return true;
        }
        return false;
    }
    
    char extract_control_data(QString& payload)
    {
        if is_control_seq()
        {
            ++m_data; --m_size; // Skip past the CONTROL_CODE byte
            char data_code = *m_data++; --m_size;
            while (*m_data != END_CONTROL_CODE)
            {
                payload.append(*m_data++); --m_size;
            }
            ++m_data; --m_size; // Skip past the END_CONTROL_CODE byte
            
            //*payload = '\0';
            return data_code;
        }
        
        payload.clear();
        return UNKNOWN_CODE;
    }
    
    QString extract_plain_data()
    {
        QString plain_data;
        while (*m_data && (*m_data != CONTROL_CODE))
        {
            plain_data.append(*m_data++); --m_size;
        }
        return plain_data;
    }
    
    static DataPacket In(const QByteArray& byte_array)
    {
        return DataPacket(byte_array);
    }
    
    static QByteArray Out(char data_code, const char* payload = 0)
    {
        QByteArray byte_array;
        byte_array.append(CONTROL_CODE);
        byte_array.append(data_code);
        byte_array.append(payload);
        byte_array.append(END_CONTROL_CODE);
        return byte_array;
    }
    
    static QByteArray Out(const QString& data)
    {
        return QByteArray(data);
    }
};


class KeyboardIO: public QLineEdit
{
signals:

    void breakSignal();
    void lineFeed();
    
public:

    KeyboardIO::KeyboardIO(QObject* parent = 0) : QLineEdit(parent)
    {
    }
    
protected:

    virtual void keyPressEvent(QKeyEvent* event)
    {
        if (event->key() == Qt::Key_Pause)
        {
            emit breakSignal();
            event->accept();
        }
        else if (event->key() == Qt::Key_Down)
        {
            emit lineFeed();
            event->accept();
        }
        else
            QLineEdit::keyPressEvent(event);
    }
};


class TerminalIO: public QWidget
{
signals:

    void setNormalStatus(const QString&);
    void setConnectStatus(const QString&);
    void setErrorStatus(const QString&);
    
protected:

    const char* FONT_NAME;
    const int   FONT_SIZE;
    
    QString     ME;
    QString     m_host;
    int         m_port;
    QTcpSocket* m_socket;
    int         m_com_port;
    QTextEdit*  m_output;
    KeyboardIO* m_input;
    
private:

    QString     fmtstr;
    QString     FONT_NAME;
    int         FONT_SIZE;
    
public:

    TerminalIO::TerminalIO(const QString& phosphor_color, QWidget* parent = 0) : QWidget(parent),
        ME("TerminalIO")
    {
        QString color;
        if (phosphor_color == "green") color = "lightgreen";
        if (phosphor_color == "amber") color = "gold";
        if (phosphor_color == "white") color = "white";
        
        m_host = DEFAULT_SERVER_NAME;
        m_port = DEFAULT_SERVER_PORT;
        
        m_socket = new QTcpSocket(this);
        connect(m_socket, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(socket_error(QAbstractSocket::SocketError)));
        connect(m_socket, SIGNAL(hostFound()), this, SLOT(host_found()));
        connect(m_socket, SIGNAL(connected()), this, SLOT(connection_made()));
        connect(m_socket, SIGNAL(disconnected()), this, SLOT(connection_lost()));
        connect(m_socket, SIGNAL(readyRead()), this, SLOT(data_available()));
        m_com_port = 0;
        
        FONT_NAME = "Glass TTY VT220";
        FONT_SIZE = 15;
        
        m_output = new QTextEdit();
        m_output->setReadOnly(true);
        m_output->setStyleSheet(fmtstr.sprintf(TEXT_EDIT_STYLE_SHEET, FONT_NAME, FONT_SIZE, color);
        m_output->setFontFamily(FONT_NAME);
        m_output->setFontPointSize(FONT_SIZE);
        m_output->setFocusPolicy(Qt::NoFocus);
        m_output->setWordWrapMode(QTextOption::WrapAnywhere);
        m_output->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
        m_output->setFixedSize(_width(N_HORZ_CHARS), _height(N_VERT_LINES));
        m_output->setEnabled(false);
        
        QVBoxLayout* output_layout = new QVBoxLayout();
        output_layout->addWidget(m_output);
        output_layout->setContentsMargins(3, 3, 0, 3);
        
        QFrame* output_frame = new QFrame();
        output_frame->setFrameStyle(QFrame::NoFrame);
        output_frame->setStyleSheet("QFrame { background: black; }");
        output_frame->setLayout(output_layout);
        
        m_input = new KeyboardIO();
        m_input->setStyleSheet(fmtstr.sprintf(LINE_EDIT_STYLE_SHEET, FONT_NAME, FONT_SIZE, color));
        m_input->setEnabled(false);
        connect(m_input, SIGNAL(returnPressed()), this, SLOT(send_string()));
        connect(m_input, SIGNAL(lineFeed()), this, SLOT(send_linefeed()));
        connect(m_input, SIGNAL(breakSignal()), this, SLOT(send_break_signal()));
        
        QVBoxLayout* layout = new QVBoxLayout();
        layout->addWidget(output_frame);
        layout->addWidget(m_input);
        
        setLayout(layout);
        
        QTimer::singleShot(0, this, SLOT(startup()));
    }
    
    TerminalIO::~TerminalIO()
    {
        delete m_socket;
        // delete m_output;
        // delete m_input;
    }
    
private slots:

    void startup()
    {
        m_socket->connectToHost(m_host, m_port);
    }
    
protected:
        
    int _width(int nchars) const
    {
        QFontMetrics fm(m_output->currentFont());
        return fm.width(QString(nchar, "M"));
    }
    
    int _height(int nlines) const
    {
        QFontMetrics fm(m_output->currentFont());
        m_output->verticalScrollBar()->setSingleStep(fm.lineSpacing());
        return (fm.lineSpacing() * nlines);
    }

public slots:

    void socket_error(QAbstractSocket::SocketError error)
    {
        if (error == QAbstractSocket::SocketError::ConnectionRefusedError)
        {
            emit setErrorStatus("Host Server not Active");
        }
        else
        {
            emit setErrorStatus(m_socket->errorString());
            cout << ME << " socket_error: " << error << endl;
        }
    }
    
    void host_found()
    {
        emit setNormalStatus("Waiting for Host Server");
    }
    
    void connection_made()
    {
        m_socket->setSocketOption(QAbstractSocket::LowDelayOption, 1);
        emit setConnectStatus(fmtstr.sprintf("Connected on port %d", m_socket->peerPort()));
        if (m_socket->peerPort() != SERVER_PORT)
        {
            m_input->setEnabled(true);
            m_input->setFocus();
        }
    }
    
    void connection_lost()
    {
        m_input->setEnabled(false);
        emit setNormalStatus("Disconnected");
        // Original connection closed; this sets up the "permanent" connection
        if (m_com_port)
        {
            m_socket->connectToHost(SERVER_NAME, m_com_port);
            connect(m_socket, SIGNAL(bytesWritten(qint64)), this, SLOT(written(qint64)));
            m_socket->bytesWritten.connect(m_written)
            m_com_port = 0;
        }
        else
        {
            cout << ME << " connection closed by host " << endl;
        }
    }
    
    void data_available()
    {
        data_packet = DataPacket::In(m_socket->readAll());
        while (data_packet.is_empty())
        {
            if (data_packet.is_control_seq())
            {
                QString payload;
                
                data_code = data_packet.extract_control_data(payload)
                
                if (data_code == ASSIGN_PORT_CODE)
                {
                    m_com_port = QString(payload).toInt();
                    // cout << ME << " disconnecting and reconnecting on port " << m_com_port << endl;
                    m_socket->close();
                }
                else if (data_code == ECHO_NORMAL_CODE)
                {
                    m_input->setEchoMode(QLineEdit::Normal);
                }
                else if (data_code == ECHO_PASSWORD_CODE)
                {
                    m_input->setEchoMode(QLineEdit::Password);
                }
                else
                {
                    throw fmtstr.sprintf("unknown control data code %d", ord(data_code));
                }
            }
            else
            {
                display(data_packet.extract_plain_data());
            }
        }
    }
    
    void send_string()
    {
        QString s = m_input->text().trimmed();
        if (s.isEmpty()) s.append('\r');
        m_input->clear();
        if (m_socket->isValid() && (m_socket->state() == QAbstractSocket::ConnectedState))
        {
            // cout << ME << " sending: " << repr(s) << endl;
            n = m_socket->write(DataPacket::Out(s));
            // cout << ME << " " << n << "bytes sent" << endl;
            m_socket->flush();
        }
    }
    
    void send_linefeed()
    {
        if (m_socket->isValid() && (m_socket->state() == QAbstractSocket::ConnectedState))
        {
            // cout << ME << " sending LINEFEED " << endl;
            n = m_socket->write(DataPacket::Out(LINEFEED_CODE));
            // cout << ME << " " << n << " bytes sent " << endl;
            m_socket->flush();
        }
    }
    
    void send_break_signal()
    {
        if (m_socket->isValid() && (m_socket->state() == QAbstractSocket::ConnectedState))
        {
            // cout << ME << " sending BREAK signal " << endl;
            n = m_socket->write(DataPacket::Out(BREAK_CODE));
            // cout << ME << " " << n << "bytes sent" << endl;
            m_socket->flush();
        }
    }
    
    void written(qint64 nbytes)
    {
        // cout << ME << " " << nbytes << " written " << endl;
    }
    
    void shutdown()
    {
        m_input->setEnabled(false);
        if (m_socket->state() == QAbstractSocket::ConnectedState)
            m_socket->disconnectFromHost();
    }
        
    void reconnect()
    {
        m_socket->connectToHost(m_host, m_port);
    }
    
    void display(const QString& txt)
    {
        m_output->insertPlainText(txt);
        // Remove characters that will never be seen again. This keeps the text edit
        // widget from filling up with useless characters.
        int max_chars = N_HORZ_CHARS * N_VERT_LINES + 1;
        int num_chars = m_output->toPlainText().length();
        if (num_chars > max_chars)
        {
            QTextCursor cursor = m_output->textCursor();
            cursor.setPosition(0, QTextCursor::MoveAnchor);
            cursor.setPosition(num_chars - max_chars, QTextCursor::KeepAnchor);
            cursor.removeSelectedText();
        }
        m_output->moveCursor(QTextCursor::End);
    }
    
pubic:
        
    void set_server_name(const QString& host)
    {
        m_host = host;
    }
    
    void set_server_port(int m_port)
    {
        m_port = port;
    }
        
    void set_phosphor_color(const QString& phosphor_color)
    {
        QString color;
        if (phosphor_color == "green") color = "lightgreen";
        if (phosphor_color == "amber") color = "gold";
        if (phosphor_color == "white") color = "white";
        
        m_output->setStyleSheet(fmtstr.sprintf(TEXT_EDIT_STYLE_SHEET, FONT_NAME, FONT_SIZE, color));
        m_output->style()->unpolish(this);
        m_output->style()->polish(this);
        m_output->update();
        
        m_input->setStyleSheet(fmtstr.sprintf(LINE_EDIT_STYLE_SHEET, FONT_NAME, FONT_SIZE, color));
        m_input->style()->unpolish(this);
        m_input->style()->polish(this);
        m_input->update();
    }
};

        
const char* MENUBAR_STYLE_SHEET = " \
    QMenuBar                { background: #252525; color: #c8c8c8; } \
    QMenuBar::item          { background: transparent; } \
    QMenuBar::item:selected { background: #444444; } \
";

const char* MENU_STYLE_SHEET = " \
    QMenu                { background: #444444; color: #c8c8c8; } \
    QMenu::item:selected { background: #656565; } \
";

class TerminalWindow: public QMainWindow
{

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
    QAction*    m_set_phosphor_green;
    QAction*    m_set_phosphor_amber;
    QAction*    m_set_phosphor_white;
    QAction*    m_reconnect_action;
    
public:

    TerminalWindow::TerminalWindow(QWidget* parent = 0) : QMainWindow(parent)
    {
        m_settings = QtCore.QSettings("pymultics", "Multics.Terminal");
        
        m_io = new TerminalIO(this);
        connect(m_io, SIGNAL(setNormalStatus(const QString&)), this, SLOT(set_normal_status(const QString&)));
        connect(m_io, SIGNAL(setConnectStatus(const QString&)), this, SLOT(set_connect_status(const QString&)));
        connect(m_io, SIGNAL(setErrorStatus(const QString&)), this, SLOT(set_error_status(const QString&)));
        connect(this, SIGNAL(transmitString(const QString&)), m_io, SLOT(display(const QString&)));
        connect(this, SIGNAL(shutdown()), m_io, SLOT(shutdown()));
        
        setCentralWidget(m_io);
        setWindowTitle("Virtual VT220 Terminal");
        setStyleSheet("QLineEdit, QMainWindow { background: #444444; border: 1px solid #252525; }");
        
        //m_palette = new QPalette()
        m_palette.setColor(QPalette::Background, QColor(0x444444));
        
        m_status_label = new QLabel();
        m_status_label->setAutoFillBackground(true);
        m_status_label->setPalette(m_palette);
        m_status_label->setText("Ready");
        
        QVBoxLayout* status_layout = new QVBoxLayout();
        status_layout->addWidget(m_status_label);
        status_layout->setContentsMargins(5, 5, 5, 5);
        
        QFrame* status_frame = new QFrame();
        status_frame->setLayout(status_layout);
        
        statusBar()->setSizeGripEnabled(false);
        statusBar()->setAutoFillBackground(true);
        statusBar()->setPalette(m_palette);
        statusBar()->addPermanentWidget(status_frame, 1);
        
        setup_menus();
        
        move(300, 50);
        
        QTimer::singleShot(0, this, SLOT(startup()));
    }
    
private:
        
    void setup_menus()
    {
        menuBar()->setStyleSheet(MENUBAR_STYLE_SHEET);
        
        m_options_menu = menuBar()->addMenu("Options");
        m_options_menu->setStyleSheet(MENU_STYLE_SHEET);
        
        m_set_host_action = m_options_menu->addAction("Set Host...");
        m_set_port_action = m_options_menu->addAction("Set Port...");
        m_options_menu->addSeparator();
        m_phosphor_color_menu = m_options_menu->addMenu("Phosphor Color");
        m_options_menu->addSeparator();
        m_reconnect_action = m_options_menu->addAction("Reconnect");
        
        m_set_phosphor_green = m_phosphor_color_menu->addAction("Green");
        m_set_phosphor_amber = m_phosphor_color_menu->addAction("Amber");
        m_set_phosphor_white = m_phosphor_color_menu->addAction("White");
        
        m_phosphor_color_group = new QActionGroup(this);
        m_phosphor_color_group->addAction(m_set_phosphor_green);
        m_phosphor_color_group->addAction(m_set_phosphor_amber);
        m_phosphor_color_group->addAction(m_set_phosphor_white);
        
        m_set_phosphor_green->setCheckable(true);
        m_set_phosphor_amber->setCheckable(true);
        m_set_phosphor_white->setCheckable(true);
        
        m_set_phosphor_green->setChecked(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "green");
        m_set_phosphor_amber->setChecked(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "amber");
        m_set_phosphor_white->setChecked(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "white");
        m_reconnect_action->setEnabled(false);
        
        connect(m_set_host_action, SIGNAL(triggered()), this, SLOT(set_host_dialog()));
        connect(m_set_port_action, SIGNAL(triggered()), this, SLOT(set_port_dialog()));

        connect(m_set_phosphor_green, SIGNAL(triggered()), this, SLOT(set_phosophor_color_green()));
        connect(m_set_phosphor_amber, SIGNAL(triggered()), this, SLOT(set_phosophor_color_amber()));
        connect(m_set_phosphor_white, SIGNAL(triggered()), this, SLOT(set_phosophor_color_white()));
        
        connect(m_reconnect_action, SIGNAL(triggered()), m_io, SLOT(reconnect()));
        connect(m_io->socket, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(enable_reconnect()));
        connect(m_io->socket, SIGNAL(connected()), this, SLOT(enable_reconnect()));
        connect(m_io->socket, SIGNAL(disconnected()), this, SLOT(disable_reconnect()));
    }

    void set_phosphor_color(const QString& color)
    {
        m_io->set_phosphor_color(color);
        m_settings.setValue("phosphor_color", color);
    }
    
    void set_status(const QString& txt)
    {
        statusBar()->setPalette(m_palette);
        m_status_label->setPalette(m_palette);
        m_status_label->setText(txt);
    }
    
private slots:

    void startup()
    {
        setFixedSize(size());
        m_io->set_server_name(m_settings.value("host", DEFAULT_SERVER_NAME));
        m_io->set_server_port(m_settings.value("port", DEFAULT_SERVER_PORT));
        m_io->set_phosphor_color(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR));
        m_io->startup();
    }
        
    void set_phosphor_color_green()
    {
        set_phosphor_color("green");
    }
        
    void set_phosphor_color_amber()
    {
        set_phosphor_color("amber");
    }
        
    void set_phosphor_color_white()
    {
        set_phosphor_color("white");
    }
    
    void set_normal_status(const QString& txt)
    {
        m_palette.setColor(QPalette::Background, QtGui.QColor(0x444444));
        set_status(txt);
    }
    
    void set_connect_status(const QString& txt)
    {
        m_palette.setColor(QPalette.Background, QtGui.QColor(0x445e44));
        set_status(txt);
    }
        
    void set_error_status(const QString& txt)
    {
        m_palette.setColor(QPalette::Background, QtGui.QColor(0x935353));
        set_status(txt);
    }
        
    void set_host_dialog()
    {
        bool ok;
        QString host = QInputDialog::getText(0, "Set Host", "Enter host address:", QLineEdit::Normal, m_settings.value("host", DEFAULT_SERVER_NAME), &ok);
        if (ok)
        {
            m_io->set_server_name(host);
            m_settings.setValue("host", host);
        }
    }
    
    void set_port_dialog()
    {
        bool ok;
        int port = QInputDialog::getInt(0, "Set Port", "Enter port number:", m_settings.value("port", DEFAULT_SERVER_PORT), 1, 99999, &ok);
        if (ok)
        {
            m_io->set_server_port(port);
            m_settings.setValue("port", port);
        }
    }
    
public slots:

    void disconnect()
    {
        QTimer::singleShot(0, this, SLOT(close()));
    }
    
protected:

    virtual void closeEvent(QCloseEvent* event)
    {
        emit closed();
        event->accept();
    }
};

void main()
{
    QApplication app;
    TerminalWindow win;
    win.show();
    app.exec();
}
