#include "terminal.h"

int N_HORZ_CHARS = 80;
int N_VERT_LINES = 25;

const char* DEFAULT_SERVER_NAME = "localhost";
const int   DEFAULT_SERVER_PORT = 6800;
const char* DEFAULT_PHOSPHOR_COLOR = "green";

QString TEXTIO_STYLE_SHEET = "QTextEdit, QLineEdit { color: %1; background: %2; border: 0px; }";


KeyboardIO::KeyboardIO(const QFont& font, const QString& color, const QString& bkgdcolor, QWidget* parent) : QLineEdit(parent)
{
    setStyleSheet(TEXTIO_STYLE_SHEET.arg(color, bkgdcolor));
    setFont(font);
}

void KeyboardIO::keyPressEvent(QKeyEvent* event)
{
    if (event->key() == Qt::Key_Pause)
    {
        emit breakSignal();
        event->accept();
    }
    else if (event->key() == Qt::Key_Enter)
    {
        emit lineFeed();
        event->accept();
    }
    else
        QLineEdit::keyPressEvent(event);
}


ScreenIO::ScreenIO(const QFont& font, const QString& color, const QString& bkgdcolor, QWidget* parent) : QTextEdit(parent)
{
    QFontMetrics fm(font);

    setReadOnly(true);
    setStyleSheet(TEXTIO_STYLE_SHEET.arg(color, bkgdcolor));
    setFont(font);
    setFocusPolicy(Qt::NoFocus);
    setWordWrapMode(QTextOption::WrapAnywhere);
    setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    setCursorWidth(fm.width("M"));
    setEnabled(false);
    setConnected(false);
}

void ScreenIO::setConnected(bool flag)
{
    m_connected = flag;
    update();
}

void ScreenIO::paintEvent(QPaintEvent* event)
{
    QTextEdit::paintEvent(event);
    if (m_connected)
    {
        QPainter painter(viewport());
        painter.fillRect(cursorRect(), QBrush(palette().text().color()));
    }
}


TerminalIO::TerminalIO(const QString& phosphor_color, QWidget* parent) : QWidget(parent),
    ME("TerminalIO")
{
    QString color, bkgdcolor;
    get_text_colors(phosphor_color, color, bkgdcolor);

    m_name = QHostInfo::localHostName();
    m_host = DEFAULT_SERVER_NAME;
    m_port = DEFAULT_SERVER_PORT;

    m_socket = new QTcpSocket(this);
    connect(m_socket, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(socket_error(QAbstractSocket::SocketError)));
    connect(m_socket, SIGNAL(hostFound()), this, SLOT(host_found()));
    connect(m_socket, SIGNAL(connected()), this, SLOT(connection_made()));
    connect(m_socket, SIGNAL(disconnected()), this, SLOT(connection_lost()));
    connect(m_socket, SIGNAL(readyRead()), this, SLOT(data_available()));
    m_com_port = 0;

    const char* FONT_NAME = "Glass TTY VT220";
#ifdef Q_OS_MAC
    const int   FONT_SIZE = 20;
#else
    const int   FONT_SIZE = 15;
#endif

    QFont font(FONT_NAME, FONT_SIZE);
    font.setStyleHint(QFont::TypeWriter);

    m_output = new ScreenIO(font, color, bkgdcolor);
    m_output->setFixedSize(_width(N_HORZ_CHARS), _height(N_VERT_LINES));

    QVBoxLayout* output_layout = new QVBoxLayout();
    output_layout->addWidget(m_output);
    output_layout->setContentsMargins(0, 3, 0, 3);

    QFrame* output_frame = new QFrame();
    output_frame->setFrameStyle(QFrame::NoFrame);
    output_frame->setStyleSheet(QString("QFrame { background: %1; }").arg(bkgdcolor));
    output_frame->setLayout(output_layout);

    m_input = new KeyboardIO(font, color, bkgdcolor);
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
}

int TerminalIO::_width(int nchars) const
{
    QFontMetricsF fm(m_output->currentFont());
    return int(round(fm.width('M') * nchars + 0.5) + m_output->document()->documentMargin() * 2);
}

int TerminalIO::_height(int nlines) const
{
    QFontMetrics fm(m_output->currentFont());
    m_output->verticalScrollBar()->setSingleStep(fm.lineSpacing());
    return (fm.lineSpacing() * nlines);
}

void TerminalIO::get_text_colors(const QString& phosphor_color, QString& color, QString& bkgdcolor) const
{
    if (phosphor_color == "vintage") color = "#32dd97";
    if (phosphor_color == "green") color = "lightgreen";
    if (phosphor_color == "amber") color = "gold";
    if (phosphor_color == "white") color = "white";

    bkgdcolor = QColor(color).darker(1500).name();
}

void TerminalIO::startup()
{
    // std::cout << "connectToHost " << m_host.toStdString() << " " << m_port << std::endl;
    m_socket->connectToHost(m_host, m_port);
}

void TerminalIO::socket_error(QAbstractSocket::SocketError error)
{
    if (error == QAbstractSocket::ConnectionRefusedError)
    {
        emit setErrorStatus(QString("Host Server %1 not Active").arg(m_host));
    }
    else if (error != QAbstractSocket::RemoteHostClosedError)
    {
        emit setErrorStatus(m_socket->errorString());
        std::cout << ME << " socket_error: " << error << std::endl;
    }
}

void TerminalIO::host_found()
{
    emit setNormalStatus(QString("Waiting for Host Server %1").arg(m_host));
}

void TerminalIO::connection_made()
{
    m_socket->setSocketOption(QAbstractSocket::LowDelayOption, 1);
    QString connected_msg = QString("Connected to %1 on port %2").arg(m_socket->peerName(), QString::number(m_socket->peerPort()));
    if (m_socket->peerPort() != m_port)
    {
        send_who_code();
        m_output->setConnected(true);
        m_input->setEnabled(true);
        m_input->setFocus();
        emit setConnectStatus(connected_msg);
    }
    else
    {
        emit setNormalStatus(connected_msg);
    }
}

void TerminalIO::connection_lost()
{
    m_input->setEnabled(false);
    m_output->setConnected(false);
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
        std::cout << ME << " connection closed by host " << m_host.toStdString() << std::endl;
    }
}

void TerminalIO::data_available()
{
    DataPacket data_packet = DataPacket::In(m_socket->readAll());
    while (!data_packet.is_empty())
    {
        if (data_packet.is_control_seq())
        {
            QString payload;
            char data_code = data_packet.extract_control_data(payload);

            if (data_code == ASSIGN_PORT_CODE)
            {
                m_com_port = payload.toInt();
                // std::cout << ME << " disconnecting and reconnecting on port " << m_com_port << std::endl;
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
                throw QString("Unknown control data code char(%1)").arg(int(data_code));
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
    QString s = m_input->text().trimmed(); s.append(CR);
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
        // If there are other characters in the input buffer, treat the LF as a CR
        // and send the whole string out.
        if (!m_input->text().isEmpty())
        {
            send_string();
        }
        // Otherwise send the LF out alone as a string.
        else
        {
//            std::cout << ME << " sending LINEFEED " << std::endl;
            int n = m_socket->write(DataPacket::Out(QString(LF)));
//            std::cout << ME << " " << n << " bytes sent " << std::endl;
            m_socket->flush();
        }
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

void TerminalIO::send_who_code()
{
    if (m_socket->isValid() && (m_socket->state() == QAbstractSocket::ConnectedState))
    {
        // std::cout << ME << " sending WHO CODE " << std::endl;
        int n = m_socket->write(DataPacket::Out(WHO_CODE, m_name.toStdString().c_str()));
        // std::cout << ME << " " << n << " bytes sent " << std::endl;
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
    m_output->setConnected(false);
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

void TerminalIO::reset()
{
    m_socket->abort();
    QTimer::singleShot(0, this, SLOT(reconnect()));
}

void TerminalIO::set_phosphor_color(const QString& phosphor_color)
{
    QString color, bkgdcolor;
    get_text_colors(phosphor_color, color, bkgdcolor);

    m_output->setStyleSheet(TEXTIO_STYLE_SHEET.arg(color, bkgdcolor));
    m_output->style()->unpolish(this);
    m_output->style()->polish(this);
    m_output->update();

    m_input->setStyleSheet(TEXTIO_STYLE_SHEET.arg(color, bkgdcolor));
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
    connect(m_io->m_socket, SIGNAL(connected()), this, SLOT(disable_reconnect()));
    connect(m_io->m_socket, SIGNAL(disconnected()), this, SLOT(enable_reconnect()));
    connect(m_io->m_socket, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(enable_reconnect()));
    connect(this, SIGNAL(transmitString(const QString&)), m_io, SLOT(display(const QString&)));
    connect(this, SIGNAL(shutdown()), m_io, SLOT(shutdown()));

    setCentralWidget(m_io);
    setWindowTitle(QString("pyMultics Virtual Terminal - %1").arg(m_io->m_name));
    setStyleSheet("QLineEdit, QMainWindow { background: #444444; border: 1px solid #252525; }");

    m_palette.setColor(QPalette::Background, QColor(0x444444));
    m_palette.setColor(QPalette::WindowText, QColor("black"));

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
    statusBar()->setStyleSheet("QStatusBar::item { border: 0px; }");
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

    m_set_host_action = m_options_menu->addAction("Set Host...", this, SLOT(set_host_dialog()));
    m_set_port_action = m_options_menu->addAction("Set Port...", this, SLOT(set_port_dialog()));
    m_options_menu->addSeparator();
    m_phosphor_color_menu = m_options_menu->addMenu("Phosphor Color");
    m_options_menu->addSeparator();
    m_reconnect_action = m_options_menu->addAction("Reconnect", m_io, SLOT(reconnect()));

    m_set_phosphor_vintg = m_phosphor_color_menu->addAction("Vintage Green", this, SLOT(set_phosphor_color_vintg()));
    m_set_phosphor_green = m_phosphor_color_menu->addAction("Green", this, SLOT(set_phosphor_color_green()));
    m_set_phosphor_amber = m_phosphor_color_menu->addAction("Amber", this, SLOT(set_phosphor_color_amber()));
    m_set_phosphor_white = m_phosphor_color_menu->addAction("White", this, SLOT(set_phosphor_color_white()));

    m_phosphor_color_group = new QActionGroup(this);
    m_phosphor_color_group->addAction(m_set_phosphor_vintg);
    m_phosphor_color_group->addAction(m_set_phosphor_green);
    m_phosphor_color_group->addAction(m_set_phosphor_amber);
    m_phosphor_color_group->addAction(m_set_phosphor_white);

    m_set_phosphor_vintg->setCheckable(true);
    m_set_phosphor_green->setCheckable(true);
    m_set_phosphor_amber->setCheckable(true);
    m_set_phosphor_white->setCheckable(true);

    m_set_phosphor_vintg->setChecked(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "vintage");
    m_set_phosphor_green->setChecked(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "green");
    m_set_phosphor_amber->setChecked(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "amber");
    m_set_phosphor_white->setChecked(m_settings.value("phosphor_color", DEFAULT_PHOSPHOR_COLOR) == "white");
    m_reconnect_action->setEnabled(false);
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

void TerminalWindow::set_phosphor_color_vintg()
{
    set_phosphor_color("vintage");
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
        m_settings.setValue("host", host);
        m_io->set_server_name(host);
        m_io->reset();
    }
}

void TerminalWindow::set_port_dialog()
{
    bool ok;
    int port = QInputDialog::getInt(0, "Set Port", "Enter port number:", m_settings.value("port", DEFAULT_SERVER_PORT).toInt(), 1, 99999, 1, &ok);
    if (ok)
    {
        m_settings.setValue("port", port);
        m_io->set_server_port(port);
        m_io->reset();
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
