#-------------------------------------------------
#
# Project created by QtCreator 2014-07-04T23:19:09
#
#-------------------------------------------------

QT       += core gui network

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = terminal
TEMPLATE = app


SOURCES +=\
        terminal.cpp \
    main.cpp \
    data_packet.cpp

HEADERS  += terminal.h \
    data_packet.h
