#include <iostream>
#include "data_packet.h"

#define pop()   remove(0, 1)

DataPacket::DataPacket()
{
}

DataPacket::DataPacket(const QByteArray& byte_array)
{
    m_byte_array = byte_array;
}

DataPacket::DataPacket(const DataPacket& data_packet)
{
    m_byte_array = data_packet.m_byte_array;
}

DataPacket::~DataPacket()
{
}

bool DataPacket::is_empty() const
{
    return (m_byte_array.length() == 0);
}

bool DataPacket::is_control_seq() const
{
    if ((m_byte_array.length() > 2) && (m_byte_array[0] == CONTROL_CODE))
    {
        return (m_byte_array.indexOf(END_CONTROL_CODE) != -1);
    }
    return false;
}

char DataPacket::extract_control_data(QString& payload)
{
    if (is_control_seq())
    {
        m_byte_array.pop(); // Pop off the CONTROL_CODE
        char data_code = m_byte_array[0];
        m_byte_array.pop(); // Pop off the data code
        int index = m_byte_array.indexOf(END_CONTROL_CODE);
        payload = m_byte_array.left(index);
        m_byte_array.remove(0, index + 1); // Remove the payload bytes
        return data_code;
    }

    payload.clear();
    return UNKNOWN_CODE;
}

QString DataPacket::extract_plain_data()
{
    QString plain_data;
    int index = m_byte_array.indexOf(CONTROL_CODE);
    if (index == -1)
    {
        plain_data = m_byte_array;
        m_byte_array.clear();
    }
    else
    {
        plain_data = m_byte_array.left(index);
        m_byte_array.remove(0, index);
    }
    return plain_data;
}

DataPacket DataPacket::In(const QByteArray& byte_array)
{
    return DataPacket(byte_array);
}

QByteArray DataPacket::Out(char data_code, const char* payload)
{
    QByteArray byte_array;
    byte_array.append(CONTROL_CODE);
    byte_array.append(data_code);
    byte_array.append(payload);
    byte_array.append(END_CONTROL_CODE);
    return byte_array;
}

QByteArray DataPacket::Out(const QString& str)
{
    QByteArray byte_array;
    byte_array.append(str);
    return byte_array;
}

