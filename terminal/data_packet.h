#ifndef DATA_PACKET_H
#define DATA_PACKET_H

#include <QByteArray>
#include <QString>
#include <QRegExp>

const char UNKNOWN_CODE       = char(0);
const char CONTROL_CODE       = char(128);
const char ECHO_NORMAL_CODE   = char(129);
const char ECHO_PASSWORD_CODE = char(130);
const char ASSIGN_PORT_CODE   = char(131);
const char WHO_CODE           = char(132);
const char BREAK_CODE         = char(133);
const char LINEFEED_CODE      = char(134);
const char END_CONTROL_CODE   = char(254);

class DataPacket
{
protected:

    QByteArray m_byte_array;

public:

    DataPacket::DataPacket();
    DataPacket::DataPacket(const QByteArray& byte_array);
    DataPacket::DataPacket(const DataPacket& data_packet);

    DataPacket::~DataPacket();

    bool is_empty() const;
    bool is_control_seq() const;
    const QByteArray& data() const { return m_byte_array; }
    const std::string toStdString() const { return std::string(m_byte_array.data()); }

    char extract_control_data(QString& payload);
    QString extract_plain_data();

    static DataPacket In(const QByteArray& byte_array);
    static QByteArray Out(char data_code, const char* payload = 0);
    static QByteArray Out(const QString& str);
};

#endif // DATA_PACKET_H
