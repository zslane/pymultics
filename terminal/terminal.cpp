#include "terminal.h"

int N_HORZ_CHARS = 80;
int N_VERT_LINES = 25;

const char* DEFAULT_SERVER_NAME = "localhost";
int DEFAULT_SERVER_PORT = 6800;
const char* DEFAULT_PHOSPHOR_COLOR = "green";

static char TEXT_EDIT_STYLE_SHEET[] = "QTextEdit { font-family: '%s'; font-size: %dpt; color: %s; background: black; border: 0px; }";
static char LINE_EDIT_STYLE_SHEET[] = "QLineEdit { font-family: '%s'; font-size: %dpt; color: %s; background: black; }";


KeyboardIO::KeyboardIO(QWidget* parent) : QLineEdit(parent)
{
}

void KeyboardIO::keyPressEvent(QKeyEvent* event)
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


TerminalIO::TerminalIO(const QString& phosphor_color, QWidget* parent) : QWidget(parent),
    ME("TerminalIO"),
    FONT_NAME("Glass TTY VT220"),
#ifdef Q_OS_MAC
    FONT_SIZE(20)
#else
    FONT_SIZE(15)
#endif
{
    char* color;
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

    //FONT_NAME = "Glass TTY VT220";
    //FONT_SIZE = 15;

    m_output = new QTextEdit();
    m_output->setReadOnly(true);
    m_output->setStyleSheet(fmtstr.sprintf(TEXT_EDIT_STYLE_SHEET, FONT_NAME, FONT_SIZE, color));
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
    output_frame->setStyleSheet(QString("QFrame { background: black; }"));
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
}

TerminalIO::~TerminalIO()
{
    delete m_socket;
    // delete m_output;
    // delete m_input;
}

int TerminalIO::_width(int nchars) const
{
    QFontMetrics fm(m_output->currentFont());
    return fm.width(QString(nchars, 'M'));
}

int TerminalIO::_height(int nlines) const
{
    QFontMetrics fm(m_output->currentFont());
    m_output->verticalScrollBar()->setSingleStep(fm.lineSpacing());
    return (fm.lineSpacing() * nlines);
}

void TerminalIO::startup()
{
//    std::cout << "connectToHost " << m_host.toStdString() << " " << m_port << std::endl;
    m_socket->connectToHost(m_host, m_port);
}

void TerminalIO::socket_error(QAbstractSocket::SocketError error)
{
    if (error == QAbstractSocket::ConnectionRefusedError)
    {
        emit setErrorStatus("Host Server not Active");
    }
    else
    {
        emit setErrorStatus(m_socket->errorString());
        std::cout << ME << " socket_error: " << error << std::endl;
    }
}

void TerminalIO::host_found()
{
    emit setNormalStatus("Waiting for Host Server");
}

void TerminalIO::connection_made()
{
    m_socket->setSocketOption(QAbstractSocket::LowDelayOption, 1);
    emit setConnectStatus(fmtstr.sprintf("Connected on port %d", m_socket->peerPort()));
    if (m_socket->peerPort() != m_port)
    {
        m_input->setEnabled(true);
        m_input->setFocus();
    }
}

void TerminalIO::connection_lost()
{
    m_input->setEnabled(false);
    emit setNormalStatus("Disconnected");
    // Original connection closed; this sets up the "permanent" connection
    if (m_com_port)
    {
        m_socket->connectToHost(m_host, m_com_port);
        connect(m_socket, SIGNAL(bytesWritten(qint64)), this, SLOT(written(qint64)));
        m_com_port = 0;
    }
    else
    {
        std::cout << ME << " connection closed by host " << std::endl;
    }
}

void TerminalIO::data_available()
{
    DataPacket& data_packet = DataPacket::In(m_socket->readAll());
    while (!data_packet.is_empty())
    {
        if (data_packet.is_control_seq())
        {
            QString payload;
            char data_code = data_packet.extract_control_data(payload);

            if (data_code == ASSIGN_PORT_CODE)
            {
                m_com_port = payload.toInt();
//                std::cout << ME << " disconnecting and reconnecting on port " << m_com_port << std::endl;
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
                throw fmtstr.sprintf("unknown control data code %d", int(data_code));
            }
        }
        else
        {
            display(data_packet.extract_plain_data());
        }
    }
}

void TerminalIO::send_string()
{
    QString s = m_input->text().trimmed();
    if (s.isEmpty()) s.append('\r');
    m_input->clear();
    if (m_socket->isValid() && (m_socket->state() == QAbstractSocket::ConnectedState))
    {
//        std::cout << ME << " sending: " << s.toStdString() << std::endl;
        int n = m_socket->write(DataPacket::Out(s));
//        std::cout << ME << " " << n << "bytes sent" << std::endl;
        m_socket->flush();
    }
}

void TerminalIO::send_linefeed()
{
    if (m_socket->isValid() && (m_socket->state() == QAbstractSocket::ConnectedState))
    {
//        std::cout << ME << " sending LINEFEED " << std::endl;
        int n = m_socket->write(DataPacket::Out(LINEFEED_CODE));
//        std::cout << ME << " " << n << " bytes sent " << std::endl;
        m_socket->flush();
    }
}

void TerminalIO::send_break_signal()
{
    if (m_socket->isValid() && (m_socket->state() == QAbstractSocket::ConnectedState))
    {
        // cout << ME << " sending BREAK signal " << endl;
        int n = m_socket->write(DataPacket::Out(BREAK_CODE));
        // cout << ME << " " << n << "bytes sent" << endl;
        m_socket->flush();
    }
}

void TerminalIO::written(qint64 nbytes)
{
    // cout << ME << " " << nbytes << " written " << endl;
}

void TerminalIO::shutdown()
{
    m_input->setEnabled(false);
    if (m_socket->state() == QAbstractSocket::ConnectedState)
        m_socket->disconnectFromHost();
}

void TerminalIO::reconnect()
{
    m_socket->connectToHost(m_host, m_port);
}

void TerminalIO::display(const QString& txt)
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

void TerminalIO::set_server_name(const QString& host)
{
    m_host = host;
}

void TerminalIO::set_server_port(int port)
{
    m_port = port;
}

void TerminalIO::set_phosphor_color(const QString& phosphor_color)
{
    char* color;
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


static QString MENUBAR_STYLE_SHEET (
"QMenuBar                { background: #252525; color: #c8c8c8; } "
"QMenuBar::item          { background: transparent; } "
"QMenuBar::item:selected { background: #444444; } "
);

static QString MENU_STYLE_SHEET (
"QMenu                { background: #444444; color: #c8c8c8; } "
"QMenu::item:selected { background: #656565; } "
);

TerminalWindow::TerminalWindow(QWidget* parent) : QMainWindow(parent),
    m_settings("pymultics", "Multics.Terminal")
{
    m_io = new TerminalIO(DEFAULT_PHOSPHOR_COLOR, this);
    connect(m_io, SIGNAL(setNormalStatus(const QString&)), this, SLOT(set_normal_status(const QString&)));
    connect(m_io, SIGNAL(setConnectStatus(const QString&)), this, SLOT(set_connect_status(const QString&)));
    connect(m_io, SIGNAL(setErrorStatus(const QString&)), this, SLOT(set_error_status(const QString&)));
    connect(this, SIGNAL(transmitString(const QString&)), m_io, SLOT(display(const QString&)));
    connect(this, SIGNAL(shutdown()), m_io, SLOT(shutdown()));

    setCentralWidget(m_io);
    setWindowTitle("pyMultics Virtual Terminal");
    setStyleSheet("QLineEdit, QMainWindow { background: #444444; border: 1px solid #252525; }");

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

void TerminalWindow::setup_menus()
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

    connect(m_set_phosphor_green, SIGNAL(triggered()), this, SLOT(set_phosphor_color_green()));
    connect(m_set_phosphor_amber, SIGNAL(triggered()), this, SLOT(set_phosphor_color_amber()));
    connect(m_set_phosphor_white, SIGNAL(triggered()), this, SLOT(set_phosphor_color_white()));

    connect(m_reconnect_action, SIGNAL(triggered()), m_io, SLOT(reconnect()));
    connect(m_io->m_socket, SIGNAL(connected()), this, SLOT(disable_reconnect()));
    connect(m_io->m_socket, SIGNAL(disconnected()), this, SLOT(enable_reconnect()));
    connect(m_io->m_socket, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(enable_reconnect()));
}

void TerminalWindow::set_phosphor_color(const QString& color)
{
    m_io->set_phosphor_color(color);
    m_settings.setValue("phosphor_color", color);
}

void TerminalWindow::set_status(const QString& txt)
{
    statusBar()->setPalette(m_palette);
    m_status_label->setPalette(m_palette);
    m_status_label->setText(txt);
}

void TerminalWindow::startup()
{
    setFixedSize(size());
    m_io->set_server_name(m_settings.value("host", DEFAULT_SERVER_NAME).toString());
    m_io->set_server_port(m_settings.value("port", DEFAULT_SERVER_PORT).toInt());
    m_io->set_phosphor_color(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR).toString());
    m_io->startup();
}

void TerminalWindow::set_phosphor_color_green()
{
    set_phosphor_color("green");
}

void TerminalWindow::set_phosphor_color_amber()
{
    set_phosphor_color("amber");
}

void TerminalWindow::set_phosphor_color_white()
{
    set_phosphor_color("white");
}

void TerminalWindow::enable_reconnect()
{
    m_reconnect_action->setEnabled(true);
}

void TerminalWindow::disable_reconnect()
{
    m_reconnect_action->setEnabled(false);
}

void TerminalWindow::set_normal_status(const QString& txt)
{
    m_palette.setColor(QPalette::Background, QColor(0x444444));
    set_status(txt);
}

void TerminalWindow::set_connect_status(const QString& txt)
{
    m_palette.setColor(QPalette::Background, QColor(0x445e44));
    set_status(txt);
}

void TerminalWindow::set_error_status(const QString& txt)
{
    m_palette.setColor(QPalette::Background, QColor(0x935353));
    set_status(txt);
}

void TerminalWindow::set_host_dialog()
{
    bool ok;
    QString host = QInputDialog::getText(0, "Set Host", "Enter host address:", QLineEdit::Normal, m_settings.value("host", DEFAULT_SERVER_NAME).toString(), &ok);
    if (ok)
    {
        m_io->set_server_name(host);
        m_settings.setValue("host", host);
    }
}

void TerminalWindow::set_port_dialog()
{
    bool ok;
    int port = QInputDialog::getInt(0, "Set Port", "Enter port number:", m_settings.value("port", DEFAULT_SERVER_PORT).toInt(), 1, 99999, 1, &ok);
    if (ok)
    {
        m_io->set_server_port(port);
        m_settings.setValue("port", port);
    }
}

void TerminalWindow::disconnect()
{
    QTimer::singleShot(0, this, SLOT(close()));
}

void TerminalWindow::closeEvent(QCloseEvent* event)
{
    emit closed();
    event->accept();
}