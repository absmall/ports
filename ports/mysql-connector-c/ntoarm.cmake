SET(CMAKE_SYSTEM_NAME QNX)
SET(CMAKE_SYSTEM_VERSION 1)

# specify the cross compiler
SET(CMAKE_C_COMPILER   $ENV{QNX_HOST}/usr/bin/ntoarmv7-gcc)
SET(CMAKE_CXX_COMPILER $ENV{QNX_HOST}/usr/bin/ntoarmv7-g++)


# where is the target environment 
SET(CMAKE_FIND_ROOT_PATH $ENV{QNX_HOST} $ENV{QTDIR} $ENV{QNX_TARGET} $ENV{QNX_TARGET}/armle-v7)

SET(CMAKE_STATIC_LIBRARY_PREFIX "")
SET(CMAKE_SHARED_LIBRARY_PREFIX "lib")
SET(CMAKE_STATIC_LIBRARY_SUFFIX ".a")
SET(CMAKE_SHARED_LIBRARY_SUFFIX ".so")
SET(CMAKE_FIND_LIBRARY_PREFIXES "lib")
SET(CMAKE_FIND_LIBRARY_SUFFIXES ".so" ".a")

SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM BOTH)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)

set(QT_HEADERS_DIR /opt/env/lenny-ppc/usr/lib)
set(QT_LIBRARY_DIR /opt/env/lenny-ppc/usr/include/qt4)

set(QT_QTCORE_LIBRARY /opt/env/lenny-ppc/usr/lib/libQtCore.so)
set(QT_QTCORE_LIBRARY_RELEASE /opt/env/lenny-ppc/usr/lib/libQtCore.so)
set(QT_QTCORE_INCLUDE_DIR /opt/env/lenny-ppc/usr/include/qt4)

set(QT_QTDBUS_LIBRARY /opt/env/lenny-ppc/usr/lib/libQtDBus.so)
set(QT_QTDBUS_LIBRARY_RELEASE /opt/env/lenny-ppc/usr/lib/libQtDBus.so)
set(QT_QTDBUS_INCLUDE_DIR /opt/env/lenny-ppc/usr/include/qt4)

set(QT_QTXML_LIBRARY /opt/env/lenny-ppc/usr/lib/libQtXml.so)
set(QT_QTXML_LIBRARY_RELEASE /opt/env/lenny-ppc/usr/lib/libQtXml.so)
set(QT_QTXML_INCLUDE_DIR /opt/env/lenny-ppc/usr/include/qt4)

#Force -pfPIC when ompiling.
SET(CMAKE_C_FLAGS -fPIC)
SET(CMAKE_C_FLAGS_INIT -fPIC)
SET(CMAKE_CXX_FLAGS_INIT -fPIC)

SET(QT_USE_QTOPENGL TRUE)
