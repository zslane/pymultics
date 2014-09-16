
from pl1types import PL1
class ErrorTable(PL1.Enum):
    def __init__(self, name):
        PL1.Enum.__init__(self, name)
        self._messages = \
{       -1680: 'Undefined forms option.',
        -1679: 'No forms table defined for this request_type or device.',
        -1678: 'Zero length segment.',
        -1677: 'Wrong number of arguments supplied.',
        -1676: 'An event channel is being used in an incorrect ring.',
        -1675: 'Insufficient access to send wakeup.',
        -1674: 'The VTOCE is already free.',
        -1673: 'Some directory or segment in the pathname is not listed in the VTOC.',
        -1672: 'Unrecoverable data-transmission error on VTOC.',
        -1671: 'Volume type unknown to the system.',
        -1670: 'The requested volume is not loaded.',
        -1669: 'The requested volume is not available.',
        -1668: 'The volume is in use by another process.',
        -1667: 'virtual channel not defined.',
        -1666: 'virtual channel is currently in use.',
        -1665: 'The user requested the connection to close.',
        -1664: 'The user voluntarily logged out.',
        -1663: 'User-name not on access control list for branch.',
        -1662: 'The specified terminal is not supported by the video system.',
        -1661: 'The requested operation is not supported.',
        -1660: 'Multi-class volumes are not supported.',
        -1659: 'The specified detachable volume has not been registered.',
        -1658: 'Volume recorded in unrecognized character code.',
        -1657: 'The time zone is not acceptable.',
        -1656: 'The specified tuning parameter does not exist.',
        -1655: 'Unable to continue processing on uninitialized volume.',
        -1654: 'This procedure does not implement the requested version.',
        -1653: 'Pointer name passed to seek or tell not currently implemented by it.',
        -1652: 'Unable to continue processing on unexpired volume.',
        -1651: 'Unable to overwrite an unexpired file.',
        -1650: 'Attempt to execute instruction containing a fault tag 2.',
        -1649: 'Unexpected or inexplicable status received from device.',
        -1648: 'An unexpected condition was signalled during the operation.',
        -1647: 'Cannot delete the only channel leading to an undeleted device.',
        -1646: 'Unrecognizable ptrname on seek or tell call.',
        -1645: 'Undefined order request.',
        -1644: 'Mode not defined.',
        -1643: 'Quotes do not balance.',
        -1642: 'Parentheses do not balance.',
        -1641: 'Brackets do not balance.',
        -1640: 'Unable to perform critical I/O.',
        -1639: 'It was not possible to complete access checking - access denied.',
        -1638: 'Typename not found.',
        -1637: 'Translation failed.',
        -1636: 'Fatal error.  Translation aborted.',
        -1635: 'Trace table is full.',
        -1634: 'Trace table is empty.',
        -1633: 'There are too many links to get to a branch.',
        -1632: 'The string contains more tokens than can be processed.',
        -1631: 'Too many search rules.',
        -1630: 'Unable to increment the reference count because of upper bound limit.',
        -1629: 'Too many read delimiters specified.',
        -1628: 'Name list exceeds maximum size.',
        -1627: 'Too many buffers specified.',
        -1626: 'Maximum number of arguments for this command exceeded.',
        -1625: 'Access control list exceeds maximum size.',
        -1624: 'The operation was not completed within the required time.',
        -1623: 'Specified time limit is too long.',
        -1622: 'Process terminated because of system defined error condition.',
        -1621: 'Tape error.',
        -1620: 'Attempt to segment move synchronized segment with held pages.',
        -1619: 'Too many synchronized segments are active.',
        -1618: 'Subvolume is invalid for this device.',
        -1617: 'Subvolume needed for this type device.',
        -1616: 'Strings are not equal.',
        -1615: 'Not enough room in stack to complete processing.',
        -1614: 'The requested ring-0 stack is not active.',
        -1613: 'All available special channels have been allocated.',
        -1612: 'The event channel specified is a special channel.',
        -1611: 'Security-out-of-service has been set on some branches due to AIM inconsistency.',
        -1610: 'Argument size too small.',
        -1609: 'The size condition has occurred.',
        -1608: "Fault in signaller by user's process.",
        -1607: 'Record is too short.',
        -1606: 'The segment number is in use.',
        -1605: 'Name already on entry.',
        -1604: 'The segment is already locked.',
        -1603: 'Segment already known to process.',
        -1602: 'Segment fault occurred accessing segment.',
        -1601: 'Segment not known to process.',
        -1600: 'Segment not found.',
        -1599: 'The segment has been deleted.',
        -1598: 'Entry has been damaged.  Please type "help damaged_segments.gi".',
        -1597: 'Maximum number of simultaneous scavenges exceeded.',
        -1596: 'The volume is being scavenged.',
        -1595: 'The volume scavenge has been terminated abnormally.',
        -1594: 'Attempt to specify the same segment as both old and new.',
        -1593: 'Fatal salvaging of process directory.',
        -1592: 'Attempt to delete segment whose safety switch is on.',
        -1591: 'There can be only one run unit at a time.',
        -1590: 'Record quota overflow.',
        -1589: 'The directory is the ROOT.',
        -1588: 'Retrieval trap on for file special user is trying to access.',
        -1587: 'Resource not known to the system.',
        -1586: 'No appropriate resource available.',
        -1585: 'Resource not assigned to requesting process.',
        -1584: 'Resource type unknown to the system.',
        -1583: 'Resource type is inappropriate for this request.',
        -1582: 'Resource specification supplied is incomplete.',
        -1581: 'The resource is otherwise reserved.',
        -1580: 'Specified resource property may not be modified in this manner.',
        -1579: 'The resource is not free.',
        -1578: 'The resource is locked.',
        -1577: 'This operation not allowed for a free resource.',
        -1576: 'Resource not accessible to the requesting process.',
        -1575: 'Resource is awaiting clear.',
        -1574: 'Resource already attached to the requesting process.',
        -1573: 'Resource already assigned to requesting process.',
        -1572: 'The resource reservation request has failed.',
        -1571: 'Processing of request has not been completed.',
        -1570: 'Request not recognized.',
        -1569: 'The specified request id matches multiple requests.',
        -1568: 'Cannot delete a base channel with related logical channels still active.',
        -1567: 'Regular expression // is undefined.',
        -1566: 'Regular expression is too long.',
        -1565: 'Regular expression is too complex.',
        -1564: 'Invalid use of * in regular expression.',
        -1563: 'The reference name count is greater than the number of reference names.',
        -1562: 'Infinite recursion.',
        -1561: 'Requested operation completed but non-fatal errors or inconsistencies were encountered.',
        -1560: 'Record locked by another process.',
        -1559: 'The registry was not found.',
        -1558: 'The resource cannot be automatically registered.',
        -1557: 'Missing rcp registry component.',
        -1556: 'Resource attribute specification is invalid.',
        -1555: 'Some attribute specified is protected.',
        -1554: 'Some attribute specified is not permitted for this resource.',
        -1553: 'Attempt to use reference names in ring 0.',
        -1552: 'Aborted by quit or term.',
        -1551: 'The physical volume is not mounted.',
        -1550: 'The physical volume cannot be scavenged.',
        -1549: 'The physical volume is already in the logical volume.',
        -1548: 'Specified project not found.',
        -1547: 'Target process unknown or in deactivated state.',
        -1546: 'Target process in stopped state.',
        -1545: 'The logical volume is private.',
        -1544: 'Tape positioned on leader.',
        -1543: 'The normalized picture exceeds 64 characters.',
        -1542: 'The picture scale factor not in the range -128:+127.',
        -1541: 'The picture contains a syntax error.',
        -1540: 'Pathname too long.',
        -1539: 'The yes and no response characters are not distinct.',
        -1538: 'Error making outward call after stack history destroyed.',
        -1537: 'The point or region specified lies outside the window.',
        -1536: 'A call that must be in a sequence of calls was out of sequence.',
        -1535: 'There is insufficient memory to wire the requested I/O buffer.',
        -1534: 'Reference is outside allowable bounds.',
        -1533: 'An error occurred while processing the order request.',
        -1532: 'There was an attempt to reference a directory which is out of service.',
        -1531: 'Attempt to reference beyond end of stack.',
        -1530: 'User stack space exhausted.',
        -1529: 'Obsolete object segment format.',
        -1528: 'Name not found.',
        -1527: 'Old DIM cannot accept new I/O call.',
        -1526: 'Odd number of arguments.',
        -1525: 'Attempt to perform an operation which is obsolete.',
        -1524: 'The name contains a null component.',
        -1523: 'Pointer to required information is null.',
        -1522: 'The directory specified has no branches.',
        -1521: 'Null bracket set encountered.',
        -1520: 'There is no more room in the KST.',
        -1519: 'Allocation could not be performed.',
        -1518: 'Entry is not a directory.',
        -1517: 'Segment not of type specified.',
        -1516: 'Signaller called while not in ring 0.',
        -1515: 'This operation requires privileged access not given to this process.',
        -1514: 'The specified message was not added by this user.',
        -1513: 'I/O switch is not open.',
        -1512: 'This operation may only be performed on a link entry.',
        -1511: 'Initialization has not been performed.',
        -1510: 'Entry not found in trace table.',
        -1509: 'Not processed.',
        -1508: 'The validation level is higher than the Data Management ring.',
        -1507: 'I/O switch is not detached.',
        -1506: 'I/O switch is not closed.',
        -1505: 'Segment is not bound.',
        -1504: 'Specified channel is not a base channel.',
        -1503: 'I/O switch (or device) is not attached.',
        -1502: 'Segment is not an archive.',
        -1501: 'This active function cannot be invoked as a command.',
        -1500: 'Pathname supplied is not an absolute pathname.',
        -1499: 'Event channel is not a wait channel.',
        -1498: 'The supplied pointer does not point to a valid IOCB.',
        -1497: 'Entry is not a branch.',
        -1496: 'Star convention is not allowed.',
        -1495: 'No part dump card in config deck.',
        -1494: 'The partition was not found.',
        -1493: 'This operation is not allowed for a segment.',
        -1492: 'The operation would leave no names on entry.',
        -1491: 'Unique id of segment does not match unique id argument.',
        -1490: 'Use of star convention resulted in no match.',
        -1489: 'No linkage offset table in this ring.',
        -1488: 'No/bad linkage info in the lot for this segment.',
        -1487: 'Entry not found.',
        -1486: 'Expected argument descriptor missing.',
        -1485: 'Expected argument missing.',
        -1484: 'There is no room to make requested allocations.',
        -1483: 'No wired structure could be allocated for this device request.',
        -1482: 'No working directory set for this process.',
        -1481: 'No write permission on entry.',
        -1480: 'The system does not currently support very large array common.',
        -1479: 'Cannot find procedure to call link trap procedure.',
        -1478: 'An upgraded directory must have terminal quota.',
        -1477: 'Unknown terminal type.',
        -1476: 'The specified table does not exist.',
        -1475: 'A statement delimiter is missing.',
        -1474: 'Unable to set the bit count on the copy.',
        -1473: 'Search list has no default.',
        -1472: 'Search list is not in search segment.',
        -1471: 'Status permission missing on directory containing entry.',
        -1470: 'The record block is too small to contain a lock.',
        -1469: 'No room available for device status block.',
        -1468: 'Supplied machine conditions are not restartable.',
        -1467: 'Record not located.',
        -1466: 'No read permission on entry.',
        -1465: 'Invalid I/O operation.',
        -1464: 'An area may not begin at an odd address.',
        -1463: 'The segment was not initiated with any null reference names.',
        -1462: 'Unable to continue processing on next volume.',
        -1461: 'Unable to move segment because of type, access or quota.',
        -1460: 'Message not found.',
        -1459: 'Insufficient memory for volume scavenge.',
        -1458: 'Unable to make original segment known.',
        -1457: 'Modify permission missing on entry.',
        -1456: 'The requested log message cannot be located.',
        -1455: 'Linkage section not found.',
        -1454: 'No line_status information available.',
        -1453: 'Specified detachable volume has no label.',
        -1452: 'No key defined for this operation.',
        -1451: 'There are no free Data Management journals indices.',
        -1450: 'No I/O switch.',
        -1449: 'Unable to allocate an I/O page table.',
        -1448: 'No interrupt was received on the designated IO channel.',
        -1447: 'No initial string defined for terminal type.',
        -1446: 'Insufficient access to return any information.',
        -1445: 'Heap symbol not found.',
        -1444: 'The heap has not been defined at this execution level.',
        -1443: 'No unclaimed signal handler specified for this process.',
        -1442: 'The FIM flag was not set in the preceding stack frame.',
        -1441: 'File does not exist.',
        -1440: 'External symbol not found.',
        -1439: 'No execute permission on entry.',
        -1438: 'You have no disconnected processes.',
        -1437: 'Some directory in path specified does not exist.',
        -1436: 'The process does not have permission to make dial requests.',
        -1435: 'No device currently available for attachment.',
        -1434: 'No delimiters found in segment to be sorted.',
        -1433: 'Bad definitions pointer in linkage.',
        -1432: 'There is no current record.',
        -1431: 'Unable to create a copy.',
        -1430: 'The requested group of CPUs contains none which are online.',
        -1429: 'Unable to complete connection to external device.',
        -1428: 'Component not found in archive.',
        -1427: 'No meters available for the specified channel.',
        -1426: 'Cannot add channel with its associated base channel inactive.',
        -1425: 'Requested tape backspace unsuccessful.',
        -1424: 'No archive name in original pathname corresponding to equal name.',
        -1423: 'No appropriate device is available.',
        -1422: 'Append permission missing.',
        -1421: 'Append permission missing on directory.',
        -1420: 'Attempt to write invalid data in 9 mode.',
        -1419: 'User name to be added to acl not acceptable to storage system.',
        -1418: 'A new search list was created.',
        -1417: 'New offset for pointer computed by seek entry is negative.',
        -1416: 'Connection not completed within specified time interval.',
        -1415: 'The NCP could not find a free table entry for this request.',
        -1414: 'Specified socket not found in network data base.',
        -1413: 'Network connection closed by foreign host.',
        -1412: 'Request for connection refused by foreign host.',
        -1411: 'Network Control Program not in operation.',
        -1410: 'There is no initial connection in progress from this socket.',
        -1409: 'Process lacks permission to initiate Network connections.',
        -1408: 'Request is inconsistent with state of socket.',
        -1407: 'The initial connection has not yet been completed.',
        -1406: 'A logical error has occurred in initial connection.',
        -1405: 'Initial connection socket is in an improper state.',
        -1404: 'Foreign IMP is down.',
        -1403: 'Communications with this foreign host not enabled.',
        -1402: 'Foreign host is down.',
        -1401: 'Bad socket gender involved in this request.',
        -1400: 'An initial connection is already in progress from this socket.',
        -1399: 'Negative offset supplied to data transmission entry.',
        -1398: 'Negative number of elements supplied to data transmission entry.',
        -1397: 'Network Control Program encountered a software error.',
        -1396: 'Name duplication.',
        -1395: 'The name was not found.',
        -1394: 'There was an attempt to lock a directory already locked to this process.',
        -1393: 'The stream is attached to more than one device.',
        -1392: 'This operation is not allowed for a multisegment file.',
        -1391: 'The multiplexer is not running.',
        -1390: 'Mount request pending.',
        -1389: 'Requested volume not yet mounted.',
        -1388: 'Incorrect access on entry.',
        -1387: 'Mode string has been truncated.',
        -1386: 'Missing entry in outer module.',
        -1385: 'Mismatched iteration sets.',
        -1384: 'Messages are not being accepted.',
        -1383: 'Messages are deferred.',
        -1382: 'The specified volume cannot be unloaded from its device.',
        -1381: 'Master directory missing from MDCS.',
        -1380: 'One or more of the paths given are in error.',
        -1379: 'Path violates volume or account pathname restriction.',
        -1378: 'Pathname not found.',
        -1377: 'Pathname appears more than once in the list.',
        -1376: 'Pathname already listed.',
        -1375: 'This operation allowed only on master directories.',
        -1374: 'No quota account for the logical volume.',
        -1373: 'Insufficient quota on logical volume.',
        -1372: 'Specified quota account not found.',
        -1371: 'Volume cannot be deleted because it contains master directories.',
        -1370: 'Quota account has master directories charged against it.',
        -1369: 'Illegal format of master directory owner name.',
        -1368: 'Illegal format of quota account name.',
        -1367: 'Executive access to logical volume required to perform operation.',
        -1366: 'Master directory quota must be greater than 0.',
        -1365: 'Reply permission missing on message coordinator source.',
        -1364: 'Quit permission missing on message coordinator source.',
        -1363: 'Daemon permission missing on message coordinator source.',
        -1362: 'Control permission missing on message coordinator source.',
        -1361: 'The maximum depth in the storage system hierarchy has been exceeded.',
        -1360: 'This operation is not allowed for a master directory.',
        -1359: 'The channel is masked.',
        -1358: 'A compiler has generated incorrect list template initialization for an array or external variable.',
        -1357: 'Validation level not in ring bracket.',
        -1356: 'The sequential position on the device is unknown.',
        -1355: 'Equals convention makes entry name too long.',
        -1354: 'Record is too long.',
        -1353: 'The logical volume table is full.',
        -1352: 'The logical volume is not mounted.',
        -1351: 'The logical volume is not attached.',
        -1350: 'The logical volume is already mounted.',
        -1349: 'The logical volume is already attached.',
        -1348: 'No more listener entries are cuurrently available for this log.',
        -1347: 'The logical volume is full.',
        -1346: 'The log segment has not yet been initialized.',
        -1345: 'The specified segment is not a valid log segment.',
        -1344: 'The log segment is full.',
        -1343: 'The log segment is empty.',
        -1342: 'The log segment is damaged.',
        -1341: 'The specified log segment is not in service at this time.',
        -1340: 'The specified log message type is invalid.',
        -1339: 'The lock was already locked by this process.',
        -1338: 'Attempt to unlock a lock which was locked by another process.',
        -1337: 'The lock could not be set in the given time.',
        -1336: 'Attempt to unlock a lock that was not locked.',
        -1335: 'The lock does not belong to an existing process.',
        -1334: 'The listen operation has been aborted by a stop_listen request.',
        -1333: 'The execute access is needed to directory containing the link.',
        -1332: 'This operation is not allowed for a link entry.',
        -1331: 'Operation not performed because of outstanding line_status information.',
        -1330: 'Too many "<" \'s in pathname.',
        -1329: 'This operation would cause a reference count to vanish.',
        -1328: 'There was an attempt to terminate a segment which was known in other rings.',
        -1327: 'Key out of order.',
        -1326: 'There is already a record with the same key.',
        -1325: 'Not enough room in ITT for wakeup.',
        -1324: 'The item specified is over the legal size.',
        -1323: 'An interprocess signal has occurred.',
        -1322: 'Ioname already attached and active.',
        -1321: 'Ioname not found.',
        -1320: 'Ioname not active.',
        -1319: 'The IOM has its number set incorrectly.',
        -1318: 'The IOM has its mailbox address switches set incorrectly.',
        -1317: 'A connect to an IOM has left main memory in an unusable state.',
        -1316: 'IOM is already deleted.',
        -1315: 'IOM is already active.',
        -1314: 'Error in internal ioat information.',
        -1313: 'IO device failed to become unassigned.',
        -1312: 'Specified IO resource not defined in configuration.',
        -1311: 'Specified IO resource not configured.',
        -1310: 'Specified IO resource is is use by another process.',
        -1309: 'Specified IO resource not assigned.',
        -1308: 'Process lacks permission to alter device status.',
        -1307: 'There is no available path to the specified IO resource.',
        -1306: 'Specified IO resource already configured.',
        -1305: 'Specified IO resource already assigned.',
        -1304: 'There was an attempt to use an invalid segment number.',
        -1303: 'Attempt to write or move write pointer on device which was not attached as writeable.',
        -1302: 'The VTOCE index specified is not within the range of valid indices for the device.',
        -1301: 'There was an attempt to use a VTOCE with invalid fields.',
        -1300: 'Specified volumes do not comprise a valid volume set.',
        -1299: 'The supplied value is not acceptable for this tuning parameter.',
        -1298: 'The record length is not an integral number of words.',
        -1297: 'The specified system type does not exist.',
        -1296: 'The specified subsystem either does not exist or is inconsistent.',
        -1295: 'Request is inconsistent with current state of device.',
        -1294: 'Attempt to create a stack which exists or which is known to process.',
        -1293: 'Attempt to set delimiters for device while element size is too large to support search.',
        -1292: 'Attempt to manipulate last or bound pointers for device that was not attached as writeable.',
        -1291: 'The ring brackets specified are invalid.',
        -1290: 'The request is inconsistent with the current state of the resource(s).',
        -1289: 'Invalid logical record length.',
        -1288: 'Invalid variable-length record descriptor.',
        -1287: 'Attempt to read or move read pointer on device which was not attached as readable.',
        -1286: 'Invalid Physical Volume Table Entry index specified.',
        -1285: 'Unable to initialize a pointer used as the initial value of an external variable.',
        -1284: 'Invalid project for gate access control list.',
        -1283: 'Undefined preaccess command.',
        -1282: 'Invalid multiplexer type specified.',
        -1281: 'Invalid move of quota would change terminal quota to non terminal.',
        -1280: 'Attempt to move more than maximum amount of quota.',
        -1279: 'Invalid mode specified for ACL.',
        -1278: 'Attempt to set max length of a segment less than its current length.',
        -1277: 'The lock was locked by a process that no longer exists.  Therefore the lock was reset.',
        -1276: 'Line type number exceeds maximum permitted value.',
        -1275: 'File set contains invalid labels.',
        -1274: 'An invalid size has been found for a heap variable.',
        -1273: 'An invalid heap header has been found.  This is likely due to the stack being overwritten.',
        -1272: 'File set structure is invalid.',
        -1271: 'File expiration date exceeds that of previous file.',
        -1270: 'Invalid element size.',
        -1269: 'Invalid data management journal index.',
        -1268: 'Attempt to attach to an invalid device.',
        -1267: 'Invalid delay value specified.',
        -1266: 'Internal inconsistency in control segment.',
        -1265: 'There was an attempt to create a copy without correct access.',
        -1264: 'The event channel specified is not a valid channel.',
        -1263: 'Invalid physical block length.',
        -1262: 'Invalid backspace_read order call.',
        -1261: 'The name specified contains non-ascii characters.',
        -1260: 'The size of an array passed as an argument is invalid.',
        -1259: 'Insufficient information to open file.',
        -1258: 'Process lacks sufficient access to perform this operation.',
        -1257: 'There was an attempt to make a directory unknown that has inferior segments.',
        -1256: 'Volume type is inappropriate for this request.',
        -1255: 'Device type is inappropriate for this request.',
        -1254: 'Incorrect access to directory containing entry.',
        -1253: 'Object MSF is inconsistent.',
        -1252: 'Active Segment Table threads in the SST are inconsistent.',
        -1251: 'The reference name table is in an inconsistent state.',
        -1250: 'Multisegment file is inconsistent.',
        -1249: 'The event channel table was in an inconsistent state.',
        -1248: 'Inconsistent combination of control arguments.',
        -1247: 'Missing components in access name.',
        -1246: 'The specified terminal type is incompatible with the line type.',
        -1245: 'Specified attribute incompatible with file structure.',
        -1244: 'Incompatible character encoding mode.',
        -1243: 'Attach and open are incompatible.',
        -1242: 'An improper attempt was made to terminate the process.',
        -1241: 'Data not in expected format.',
        -1240: 'A RFNM is pending on this IMP link.',
        -1239: 'Multics IMP is down.',
        -1238: 'Bad status received from IMP.',
        -1237: 'Format of IMP message was incorrect.',
        -1236: 'Record size must be positive and smaller than a segment',
        -1235: 'Attempt to indirect through word pair containing a fault tag 2 in the odd word.',
        -1234: 'There was an illegal attempt to delete an AST entry.',
        -1233: 'There was an illegal attempt to activate a segment.',
        -1232: 'Supplied identifier not found in data base.',
        -1231: 'Supplied identifier already exists in data base.',
        -1230: 'The lock was set on behalf of an operation which must be adjusted.',
        -1229: 'Attempt to perform an illegal action on a hardcore segment.',
        -1228: 'There was an attempt to delete a non-empty directory.',
        -1227: 'The directory hash table is full.',
        -1226: 'PVT index out of range.',
        -1225: 'Physical device error.',
        -1224: 'Unsupported VTOC header version.',
        -1223: 'Unsupported label version.',
        -1222: 'Not a storage system drive.',
        -1221: 'Volume not salvaged.',
        -1220: 'Drive not ready.',
        -1219: 'Drive in use already.',
        -1218: 'Invalid storage system volume label.',
        -1217: 'Attempt to reference temporary storage outside the scope of this frame.',
        -1216: 'The Operator refused to honor the mount request.',
        -1215: 'The FNP is not running.',
        -1214: 'A first reference trap was found on the link target segment.',
        -1213: "Illegal procedure fault in FIM by user's process.",
        -1212: 'No file is open under this reference name.',
        -1211: 'There is no more room in the file.',
        -1210: 'File already busy for other I/O activity.',
        -1209: 'File is already opened.',
        -1208: 'Defective file section deleted from file set.',
        -1207: 'A fatal error has occurred.',
        -1206: 'Event channels not in cutoff state.',
        -1205: 'Event channels in cutoff state.',
        -1204: 'Event calls are not in masked state.',
        -1203: 'Encountered end-of-volume on write.',
        -1202: 'End-of-file record encountered.',
        -1201: 'Entry name too long.',
        -1200: 'End of information reached.',
        -1199: 'Search list is empty.',
        -1198: 'File is empty.',
        -1197: 'Archive is empty.',
        -1196: 'ACL is empty.',
        -1195: 'A pointer that must be eight word aligned was not so aligned.',
        -1194: 'The event channel table was full.',
        -1193: 'The event channel table has already been initialized.',
        -1192: 'Echo negotiation race occurred.  Report this as a bug.',
        -1191: 'A duplicate request was encountered.',
        -1190: 'File identifier already appears in file set.',
        -1189: 'Duplicate entry name in bound segment.',
        -1188: 'In the specified time zone, the clock value is before the year 0001.',
        -1187: 'In the specified time zone, the clock value is after the year 9999.',
        -1186: 'An unknown word was found in the time string.',
        -1185: 'The language given is not known to the system.',
        -1184: 'An error has been found while converting a time string.',
        -1183: 'The size condition occurred while converting the time string.',
        -1182: 'Applying an offset gives a date after 9999-12-31 GMT.',
        -1181: 'Applying an offset gives a date before 0001-01-01 GMT.',
        -1180: 'No units were given in which to express the interval.',
        -1179: 'The format string contains no selectors.',
        -1178: 'A time zone value has been given more than once.',
        -1177: 'A time value has been given more than once.',
        -1176: 'The time string does not have the same meaning in all languages.',
        -1175: 'A day of the week value has been given more than once.',
        -1174: 'A date value has been given more than once.',
        -1173: 'The hour value exceeds 12.',
        -1172: 'The date is before 0001-01-01 GMT.',
        -1171: 'The date is after 9999-12-31 GMT.',
        -1170: 'The time period 1582-10-05 through 1582-10-14 does not exist.',
        -1169: 'There is a conflict in the day specifications.',
        -1168: 'The month number is invalid.',
        -1167: 'The fiscal week number is invalid.',
        -1166: 'The format string contains a selector which is not defined.',
        -1165: 'The day of the year is invalid.',
        -1164: 'The day of the month is invalid.',
        -1163: 'The date given is not on the indicated day of the week.',
        -1162: 'All words in a time string must be in the same language.',
        -1161: 'Attempt to modify a valid dump.',
        -1160: 'The resource is presently in use by a system dumper.',
        -1159: 'Attempt to re-copy an invalid dump.',
        -1158: 'Data Management has not been enabled on the system.',
        -1157: 'Pages are held in memory for the journal.',
        -1156: 'Number of blocks read does not agree with recorded block count.',
        -1155: 'This operation is not allowed for a directory.',
        -1154: 'Directory pathname too long.',
        -1153: 'Directory irreparably damaged.',
        -1152: 'The dial identifier is already in use.',
        -1151: 'The process is already serving a dial qualifier.',
        -1150: 'Device type unknown to the system.',
        -1149: 'Unrecoverable data-transmission error on physical device.',
        -1148: 'Device is not currently usable.',
        -1147: 'The device is not currently active.',
        -1146: "The process's limit for this device type is exceeded.",
        -1145: 'Physical end of device encountered.',
        -1144: 'The device is in use.  It will be deleted when it is unassigned.',
        -1143: 'Unrecognized character for this code translation.',
        -1142: 'The requested device is not available.',
        -1141: 'Device attention condition during eof record write.',
        -1140: 'Condition requiring manual intervention with handler.',
        -1139: 'I/O in progress on device.',
        -1138: 'Specified offset out of bounds for this device.',
        -1137: 'IO device not currently assigned.',
        -1136: 'Looping searching definitions.',
        -1135: 'Attempt to deactivate a segment with pages in memory.',
        -1134: 'Unable to convert character date/time to binary.',
        -1133: 'Data sequence error.',
        -1132: 'Data has been lost.',
        -1131: 'Relevant data terminated improperly.',
        -1130: 'Data has been gained.',
        -1129: 'Cyclic synonyms.',
        -1128: 'The command line contained syntax characters not supported in this environment.',
        -1127: 'There was an attempt to delete a segment whose copy switch was set.',
        -1126: 'The command name is unavailable from the argument list.',
        -1125: 'Expanded command line is too large.',
        -1124: 'There was an attempt to move segment to non-zero length entry.',
        -1123: 'Cannot add channel while its IOM is inactive.',
        -1122: 'Cannot delete IOM with active channels.',
        -1121: 'Channel is in the process of being deleted.',
        -1120: 'Channel is already deleted.',
        -1119: 'Channel is already added.',
        -1118: 'Checksum error in data.',
        -1117: 'Segment contains characters after final delimiter.',
        -1116: 'Attempt to change first pointer.',
        -1115: 'This entry cannot be traced.',
        -1114: 'The buffer is in an invalid state.',
        -1113: 'Specified buffer size too large.',
        -1112: 'Attempt to access beyond end of segment.',
        -1111: 'The rest of the tape is blank.',
        -1110: 'Reverse interrupt detected on bisync line.',
        -1109: 'Attempt to write improperly formated bisync block.',
        -1108: 'Bisync line did not respond to line bid sequence.',
        -1107: 'External variable or common block is not the same size as other uses of the same name.',
        -1106: 'Argument too long.',
        -1105: 'Insufficient access to use specified block size.',
        -1104: 'Segment is too large.  Please type "help 256K_segments.gi".',
        -1103: 'Entry is for a begin block.',
        -1102: 'Bad part dump card in config deck.',
        -1101: 'Syntax error in ascii segment.',
        -1100: 'Invalid syntax in starname.',
        -1099: 'Input ring number invalid.',
        -1098: 'Bad syntax in pathname.',
        -1097: 'Specified control argument is not accepted.',
        -1096: 'Illegal use of equals convention.',
        -1095: 'Procedure called improperly.',
        -1094: 'The year is not part of the 20th Century (1901 through 1999).',
        -1093: 'Specified work class is not currently defined.',
        -1092: 'Invalid volume identifier.',
        -1091: 'Incorrect virtual channel specification.',
        -1090: 'UID path cannot be converted to a pathname.',
        -1089: 'Trap-before-link procedure was unable to snap link.',
        -1088: 'The time is incorrect.',
        -1087: 'Invalid volume name.',
        -1086: 'Invalid argument to subroutine.',
        -1085: 'Unable to process a search rule string.',
        -1084: "Improper access on user's stack.",
        -1083: 'Illegal self reference type.',
        -1082: 'There is an internal inconsistency in the segment.',
        -1081: 'Resource specification is invalid.',
        -1080: 'Argument is not an ITS pointer.',
        -1079: 'Current processid does not match stored value.',
        -1078: 'Invalid process type.',
        -1077: 'Illegal syntax in command line pipe.',
        -1076: 'Incorrect password.',
        -1075: 'Bad argument to specify the new key of a record.',
        -1074: 'The access name specified has an illegal syntax.',
        -1073: 'Directory or link found in multisegment file.',
        -1072: 'Inconsistent multiplexer bootload data supplied.',
        -1071: 'Mount request could not be honored.',
        -1070: 'Invalid value for specified mode.',
        -1069: 'Invalid syntax in mode string.',
        -1068: 'Improper mode specification for this device.',
        -1067: 'The s mode is required whenever the r mode is used.  Please type "help mailbox_acls".',
        -1066: 'The a mode is required whenever the w or u mode is used.  Please type "help mailbox_acls".',
        -1065: "Improper access on user's linkage segment.",
        -1064: 'Illegal type code in type pair block.',
        -1063: 'Illegal initialization info passed with create-if-not-found link.',
        -1062: 'Incorrect detachable medium label.',
        -1061: 'Improper target of indirect definition.',
        -1060: 'Internal index out of bounds.',
        -1059: 'Improper access on handler for this signal.',
        -1058: 'Illegal structure provided for trap at first reference.',
        -1057: 'Invalid syntax in entryname.',
        -1056: 'File is not a structured file or is inconsistent.',
        -1055: 'Illegal syntax in equal name.',
        -1054: 'Illegal entry point name in make_ptr call.',
        -1053: 'There is an inconsistency in this directory.',
        -1052: 'Incorrect recording media density.',
        -1051: 'Invalid link reference found in deferred initialiation structure.',
        -1050: 'The day-of-the-week is incorrect.',
        -1049: 'The date is incorrect.',
        -1048: 'Error in conversion.',
        -1047: 'Improper syntax in command name.',
        -1046: 'Bad class code in definition.',
        -1045: 'Incorrect IO channel specification.',
        -1044: 'The signaller could not use the saved sp in the stack base for bar mode.',
        -1043: 'Improper access to given argument.',
        -1042: 'Invalid argument.',
        -1041: 'Bad mode specification for ACL.',
        -1040: 'Unknown authentication code.',
        -1039: 'Incorrect authentication code.',
        -1038: 'Attachment loop.',
        -1037: 'Record with key for insertion has been added by another opening.',
        -1036: 'Record located by seek_key has been deleted by another opening.',
        -1035: 'A previously referenced item has been changed by another opening.',
        -1034: 'A send_admin_command line attempted to read from user_i/o.',
        -1033: 'The AS request message was too short or had a bad request type',
        -1032: 'The sender of an AS request has logged out before being validated',
        -1031: 'The process to be bumped was not found.',
        -1030: 'There is an inconsistency in arguments to the storage system.',
        -1029: 'Argument ignored.',
        -1028: 'Supplied area too small for this request.',
        -1027: 'Archive component pathname not permitted.',
        -1026: 'Format error encountered in archive segment.',
        -1025: 'This procedure may not modify archive components.',
        -1024: 'Active process table is full.  Could not create process.',
        -1023: 'Initialization has already been completed and will not be re-done.',
        -1022: 'Indicated device assigned to another process.',
        -1021: 'Entry access class is less than its parent.',
        -1020: 'Improper access class/authorization to perform operation.',
        -1019: 'Parent access class is greater than its son.',
        -1018: 'The access class/authorization is not within the range in common between the two systems.',
        -1017: 'The specified access class/authorization is not within the permitted range.',
        -1016: 'There are no access classes/authorizations in common between the two systems.',
        -1015: 'Unable to convert access class/authorization to binary.',
        -1014: 'The specified access classes/authorizations are not a valid range.',
        -1013: 'Unable to convert binary access class/authorization to string.',
        -1012: 'Branch and VTOCE access class mismatch.',
        -1011: 'The channel already has a required access class.',
        -1010: 'Specified access class/authorization is greater than allowed maximum.',
        -1009: 'This command cannot be invoked as an active function.',
        -1008: 'The requested action was not performed.',
        -1007: 'One or more memory frames are abs-wired.',
        -1006: 'absentee: CPU time limit exceeded.  Job terminated.',
        -1005: 'absentee: Attempt to reenter user environment via a call to cu_$cl.  Job terminated.',
        -1004: 'No command name available.',
        -1003: 'No such file or directory.',
        -1002: 'Error processing file.',
        -1001: 'Unknown user.'}

        self.no_such_user = PL1.EnumValue(name, 'no_such_user', -1001)
        self.fileioerr = PL1.EnumValue(name, 'fileioerr', -1002)
        self.no_directory_entry = PL1.EnumValue(name, 'no_directory_entry', -1003)
        self.no_command_name_available = PL1.EnumValue(name, 'no_command_name_available', -1004)
        self.abs_reenter = PL1.EnumValue(name, 'abs_reenter', -1005)
        self.absrentr = PL1.EnumValue(name, 'absrentr', -1005)
        self.abstimer = PL1.EnumValue(name, 'abstimer', -1006)
        self.abs_timer_runout = PL1.EnumValue(name, 'abs_timer_runout', -1006)
        self.abswired = PL1.EnumValue(name, 'abswired', -1007)
        self.abs_wired_memory = PL1.EnumValue(name, 'abs_wired_memory', -1007)
        self.notacted = PL1.EnumValue(name, 'notacted', -1008)
        self.action_not_performed = PL1.EnumValue(name, 'action_not_performed', -1008)
        self.not_cmd = PL1.EnumValue(name, 'not_cmd', -1009)
        self.active_function = PL1.EnumValue(name, 'active_function', -1009)
        self.ai_above_allowed_max = PL1.EnumValue(name, 'ai_above_allowed_max', -1010)
        self.ai_max = PL1.EnumValue(name, 'ai_max', -1010)
        self.aialrdy = PL1.EnumValue(name, 'aialrdy', -1011)
        self.ai_already_set = PL1.EnumValue(name, 'ai_already_set', -1011)
        self.ai_entry_vtoce_mismatch = PL1.EnumValue(name, 'ai_entry_vtoce_mismatch', -1012)
        self.aibdvtce = PL1.EnumValue(name, 'aibdvtce', -1012)
        self.aibadbin = PL1.EnumValue(name, 'aibadbin', -1013)
        self.ai_invalid_binary = PL1.EnumValue(name, 'ai_invalid_binary', -1013)
        self.aibadrng = PL1.EnumValue(name, 'aibadrng', -1014)
        self.ai_invalid_range = PL1.EnumValue(name, 'ai_invalid_range', -1014)
        self.aibadstr = PL1.EnumValue(name, 'aibadstr', -1015)
        self.ai_invalid_string = PL1.EnumValue(name, 'ai_invalid_string', -1015)
        self.aincmax = PL1.EnumValue(name, 'aincmax', -1016)
        self.ai_no_common_max = PL1.EnumValue(name, 'ai_no_common_max', -1016)
        self.ai_out_range = PL1.EnumValue(name, 'ai_out_range', -1017)
        self.aioutrng = PL1.EnumValue(name, 'aioutrng', -1017)
        self.ai_outside_common_range = PL1.EnumValue(name, 'ai_outside_common_range', -1018)
        self.aiocr = PL1.EnumValue(name, 'aiocr', -1018)
        self.aiparbig = PL1.EnumValue(name, 'aiparbig', -1019)
        self.ai_parent_greater = PL1.EnumValue(name, 'ai_parent_greater', -1019)
        self.ai_restricted = PL1.EnumValue(name, 'ai_restricted', -1020)
        self.ai_stop = PL1.EnumValue(name, 'ai_stop', -1020)
        self.ai_son_less = PL1.EnumValue(name, 'ai_son_less', -1021)
        self.aisonles = PL1.EnumValue(name, 'aisonles', -1021)
        self.assigned = PL1.EnumValue(name, 'assigned', -1022)
        self.already_assigned = PL1.EnumValue(name, 'already_assigned', -1022)
        self.already_initialized = PL1.EnumValue(name, 'already_initialized', -1023)
        self.noreinit = PL1.EnumValue(name, 'noreinit', -1023)
        self.aptfull = PL1.EnumValue(name, 'aptfull', -1024)
        self.apt_full = PL1.EnumValue(name, 'apt_full', -1024)
        self.compmod = PL1.EnumValue(name, 'compmod', -1025)
        self.archive_component_modification = PL1.EnumValue(name, 'archive_component_modification', -1025)
        self.acfmterr = PL1.EnumValue(name, 'acfmterr', -1026)
        self.archive_fmt_err = PL1.EnumValue(name, 'archive_fmt_err', -1026)
        self.archive_pathname = PL1.EnumValue(name, 'archive_pathname', -1027)
        self.ac_path = PL1.EnumValue(name, 'ac_path', -1027)
        self.area_too_small = PL1.EnumValue(name, 'area_too_small', -1028)
        self.areasmal = PL1.EnumValue(name, 'areasmal', -1028)
        self.arg_ignored = PL1.EnumValue(name, 'arg_ignored', -1029)
        self.arg_ign = PL1.EnumValue(name, 'arg_ign', -1029)
        self.argerr = PL1.EnumValue(name, 'argerr', -1030)
        self.asbmpusr = PL1.EnumValue(name, 'asbmpusr', -1031)
        self.as_bump_user_not_found = PL1.EnumValue(name, 'as_bump_user_not_found', -1031)
        self.assender = PL1.EnumValue(name, 'assender', -1032)
        self.as_request_sender_missing = PL1.EnumValue(name, 'as_request_sender_missing', -1032)
        self.asinval = PL1.EnumValue(name, 'asinval', -1033)
        self.as_request_invalid_request = PL1.EnumValue(name, 'as_request_invalid_request', -1033)
        self.assacrd = PL1.EnumValue(name, 'assacrd', -1034)
        self.as_sac_command_read = PL1.EnumValue(name, 'as_sac_command_read', -1034)
        self.asyncchg = PL1.EnumValue(name, 'asyncchg', -1035)
        self.asynch_change = PL1.EnumValue(name, 'asynch_change', -1035)
        self.asyncdel = PL1.EnumValue(name, 'asyncdel', -1036)
        self.asynch_deletion = PL1.EnumValue(name, 'asynch_deletion', -1036)
        self.as_ins = PL1.EnumValue(name, 'as_ins', -1037)
        self.asynch_insertion = PL1.EnumValue(name, 'asynch_insertion', -1037)
        self.att_loop = PL1.EnumValue(name, 'att_loop', -1038)
        self.auth_incorrect = PL1.EnumValue(name, 'auth_incorrect', -1039)
        self.authinc = PL1.EnumValue(name, 'authinc', -1039)
        self.authun = PL1.EnumValue(name, 'authun', -1040)
        self.auth_unknown = PL1.EnumValue(name, 'auth_unknown', -1040)
        self.bad_acl_mode = PL1.EnumValue(name, 'bad_acl_mode', -1041)
        self.badacmod = PL1.EnumValue(name, 'badacmod', -1041)
        self.badarg = PL1.EnumValue(name, 'badarg', -1042)
        self.bad_arg = PL1.EnumValue(name, 'bad_arg', -1042)
        self.badargac = PL1.EnumValue(name, 'badargac', -1043)
        self.bad_arg_acc = PL1.EnumValue(name, 'bad_arg_acc', -1043)
        self.bad_bar_sp = PL1.EnumValue(name, 'bad_bar_sp', -1044)
        self.badbarsp = PL1.EnumValue(name, 'badbarsp', -1044)
        self.badchnnl = PL1.EnumValue(name, 'badchnnl', -1045)
        self.bad_channel = PL1.EnumValue(name, 'bad_channel', -1045)
        self.bad_class_def = PL1.EnumValue(name, 'bad_class_def', -1046)
        self.badclass = PL1.EnumValue(name, 'badclass', -1046)
        self.badcomnm = PL1.EnumValue(name, 'badcomnm', -1047)
        self.bad_command_name = PL1.EnumValue(name, 'bad_command_name', -1047)
        self.bad_conversion = PL1.EnumValue(name, 'bad_conversion', -1048)
        self.bad_conv = PL1.EnumValue(name, 'bad_conv', -1048)
        self.bad_date = PL1.EnumValue(name, 'bad_date', -1049)
        self.bad_dow = PL1.EnumValue(name, 'bad_dow', -1050)
        self.bad_day_of_week = PL1.EnumValue(name, 'bad_day_of_week', -1050)
        self.baddefin = PL1.EnumValue(name, 'baddefin', -1051)
        self.bad_deferred_init = PL1.EnumValue(name, 'bad_deferred_init', -1051)
        self.bad_dens = PL1.EnumValue(name, 'bad_dens', -1052)
        self.bad_density = PL1.EnumValue(name, 'bad_density', -1052)
        self.bad_dir = PL1.EnumValue(name, 'bad_dir', -1053)
        self.badename = PL1.EnumValue(name, 'badename', -1054)
        self.bad_entry_point_name = PL1.EnumValue(name, 'bad_entry_point_name', -1054)
        self.bad_equal_name = PL1.EnumValue(name, 'bad_equal_name', -1055)
        self.bdeqlnam = PL1.EnumValue(name, 'bdeqlnam', -1055)
        self.bad_file = PL1.EnumValue(name, 'bad_file', -1056)
        self.bad_file_name = PL1.EnumValue(name, 'bad_file_name', -1057)
        self.badentry = PL1.EnumValue(name, 'badentry', -1057)
        self.bad_first_ref_trap = PL1.EnumValue(name, 'bad_first_ref_trap', -1058)
        self.bdfrtrap = PL1.EnumValue(name, 'bdfrtrap', -1058)
        self.noacchd = PL1.EnumValue(name, 'noacchd', -1059)
        self.bad_handler_access = PL1.EnumValue(name, 'bad_handler_access', -1059)
        self.bad_index = PL1.EnumValue(name, 'bad_index', -1060)
        self.badindex = PL1.EnumValue(name, 'badindex', -1060)
        self.bad_indirect_def = PL1.EnumValue(name, 'bad_indirect_def', -1061)
        self.bdinddef = PL1.EnumValue(name, 'bdinddef', -1061)
        self.badlabel = PL1.EnumValue(name, 'badlabel', -1062)
        self.bad_label = PL1.EnumValue(name, 'bad_label', -1062)
        self.bdlkinit = PL1.EnumValue(name, 'bdlkinit', -1063)
        self.bad_link_target_init_info = PL1.EnumValue(name, 'bad_link_target_init_info', -1063)
        self.badlktyp = PL1.EnumValue(name, 'badlktyp', -1064)
        self.bad_link_type = PL1.EnumValue(name, 'bad_link_type', -1064)
        self.bdlnkac = PL1.EnumValue(name, 'bdlnkac', -1065)
        self.bad_linkage_access = PL1.EnumValue(name, 'bad_linkage_access', -1065)
        self.bdmacawu = PL1.EnumValue(name, 'bdmacawu', -1066)
        self.bad_mbx_acl_awu = PL1.EnumValue(name, 'bad_mbx_acl_awu', -1066)
        self.bdmacrs = PL1.EnumValue(name, 'bdmacrs', -1067)
        self.bad_mbx_acl_rs = PL1.EnumValue(name, 'bad_mbx_acl_rs', -1067)
        self.badmode = PL1.EnumValue(name, 'badmode', -1068)
        self.bad_mode = PL1.EnumValue(name, 'bad_mode', -1068)
        self.bad_mode_syntax = PL1.EnumValue(name, 'bad_mode_syntax', -1069)
        self.bdmdsynt = PL1.EnumValue(name, 'bdmdsynt', -1069)
        self.badmdval = PL1.EnumValue(name, 'badmdval', -1070)
        self.bad_mode_value = PL1.EnumValue(name, 'bad_mode_value', -1070)
        self.badmount = PL1.EnumValue(name, 'badmount', -1071)
        self.bad_mount_request = PL1.EnumValue(name, 'bad_mount_request', -1071)
        self.badload = PL1.EnumValue(name, 'badload', -1072)
        self.bad_mpx_load_data = PL1.EnumValue(name, 'bad_mpx_load_data', -1072)
        self.bad_ms_file = PL1.EnumValue(name, 'bad_ms_file', -1073)
        self.badmsfil = PL1.EnumValue(name, 'badmsfil', -1073)
        self.bad_name = PL1.EnumValue(name, 'bad_name', -1074)
        self.x_newkey = PL1.EnumValue(name, 'x_newkey', -1075)
        self.bad_new_key = PL1.EnumValue(name, 'bad_new_key', -1075)
        self.bad_password = PL1.EnumValue(name, 'bad_password', -1076)
        self.badpass = PL1.EnumValue(name, 'badpass', -1076)
        self.bad_pipe_syntax = PL1.EnumValue(name, 'bad_pipe_syntax', -1077)
        self.pipesyn = PL1.EnumValue(name, 'pipesyn', -1077)
        self.bad_process_type = PL1.EnumValue(name, 'bad_process_type', -1078)
        self.badproct = PL1.EnumValue(name, 'badproct', -1078)
        self.bad_processid = PL1.EnumValue(name, 'bad_processid', -1079)
        self.badproci = PL1.EnumValue(name, 'badproci', -1079)
        self.badptr = PL1.EnumValue(name, 'badptr', -1080)
        self.bad_ptr = PL1.EnumValue(name, 'bad_ptr', -1080)
        self.bad_resource_spec = PL1.EnumValue(name, 'bad_resource_spec', -1081)
        self.bad_rsc = PL1.EnumValue(name, 'bad_rsc', -1081)
        self.bad_segment = PL1.EnumValue(name, 'bad_segment', -1082)
        self.badseg = PL1.EnumValue(name, 'badseg', -1082)
        self.bad_self_ref = PL1.EnumValue(name, 'bad_self_ref', -1083)
        self.badslfrf = PL1.EnumValue(name, 'badslfrf', -1083)
        self.bad_stack_access = PL1.EnumValue(name, 'bad_stack_access', -1084)
        self.noaccsp = PL1.EnumValue(name, 'noaccsp', -1084)
        self.badstrng = PL1.EnumValue(name, 'badstrng', -1085)
        self.bad_string = PL1.EnumValue(name, 'bad_string', -1085)
        self.badsbarg = PL1.EnumValue(name, 'badsbarg', -1086)
        self.bad_subr_arg = PL1.EnumValue(name, 'bad_subr_arg', -1086)
        self.bad_tapeid = PL1.EnumValue(name, 'bad_tapeid', -1087)
        self.badtpid = PL1.EnumValue(name, 'badtpid', -1087)
        self.bad_time = PL1.EnumValue(name, 'bad_time', -1088)
        self.bad_trap_before_link = PL1.EnumValue(name, 'bad_trap_before_link', -1089)
        self.bdtrb4lk = PL1.EnumValue(name, 'bdtrb4lk', -1089)
        self.baduidpn = PL1.EnumValue(name, 'baduidpn', -1090)
        self.bad_uidpath = PL1.EnumValue(name, 'bad_uidpath', -1090)
        self.badvchn = PL1.EnumValue(name, 'badvchn', -1091)
        self.bad_vchannel = PL1.EnumValue(name, 'bad_vchannel', -1091)
        self.bad_volid = PL1.EnumValue(name, 'bad_volid', -1092)
        self.badvolid = PL1.EnumValue(name, 'badvolid', -1092)
        self.bad_work_class = PL1.EnumValue(name, 'bad_work_class', -1093)
        self.badwc = PL1.EnumValue(name, 'badwc', -1093)
        self.bad_year = PL1.EnumValue(name, 'bad_year', -1094)
        self.badcall = PL1.EnumValue(name, 'badcall', -1095)
        self.badequal = PL1.EnumValue(name, 'badequal', -1096)
        self.bad_opt = PL1.EnumValue(name, 'bad_opt', -1097)
        self.badopt = PL1.EnumValue(name, 'badopt', -1097)
        self.badpath = PL1.EnumValue(name, 'badpath', -1098)
        self.badrngno = PL1.EnumValue(name, 'badrngno', -1099)
        self.badringno = PL1.EnumValue(name, 'badringno', -1099)
        self.badstar = PL1.EnumValue(name, 'badstar', -1100)
        self.badsyntax = PL1.EnumValue(name, 'badsyntax', -1101)
        self.badsyntx = PL1.EnumValue(name, 'badsyntx', -1101)
        self.bdprtdmp = PL1.EnumValue(name, 'bdprtdmp', -1102)
        self.begin_block = PL1.EnumValue(name, 'begin_block', -1103)
        self.beginent = PL1.EnumValue(name, 'beginent', -1103)
        self.bigseg = PL1.EnumValue(name, 'bigseg', -1104)
        self.big_seg = PL1.EnumValue(name, 'big_seg', -1104)
        self.big_ws_req = PL1.EnumValue(name, 'big_ws_req', -1105)
        self.bigwsreq = PL1.EnumValue(name, 'bigwsreq', -1105)
        self.bigarg = PL1.EnumValue(name, 'bigarg', -1106)
        self.bigger_ext_variable = PL1.EnumValue(name, 'bigger_ext_variable', -1107)
        self.bigexvar = PL1.EnumValue(name, 'bigexvar', -1107)
        self.bscbidf = PL1.EnumValue(name, 'bscbidf', -1108)
        self.bisync_bid_fail = PL1.EnumValue(name, 'bisync_bid_fail', -1108)
        self.bisync_block_bad = PL1.EnumValue(name, 'bisync_block_bad', -1109)
        self.bscblkbd = PL1.EnumValue(name, 'bscblkbd', -1109)
        self.bscrvi = PL1.EnumValue(name, 'bscrvi', -1110)
        self.bisync_reverse_interrupt = PL1.EnumValue(name, 'bisync_reverse_interrupt', -1110)
        self.blank_tape = PL1.EnumValue(name, 'blank_tape', -1111)
        self.blanktap = PL1.EnumValue(name, 'blanktap', -1111)
        self.outbnd = PL1.EnumValue(name, 'outbnd', -1112)
        self.boundviol = PL1.EnumValue(name, 'boundviol', -1112)
        self.buffbig = PL1.EnumValue(name, 'buffbig', -1113)
        self.buffer_big = PL1.EnumValue(name, 'buffer_big', -1113)
        self.buffer_invalid_state = PL1.EnumValue(name, 'buffer_invalid_state', -1114)
        self.bufstate = PL1.EnumValue(name, 'bufstate', -1114)
        self.notrace = PL1.EnumValue(name, 'notrace', -1115)
        self.cannot_trace = PL1.EnumValue(name, 'cannot_trace', -1115)
        self.chfirst = PL1.EnumValue(name, 'chfirst', -1116)
        self.change_first = PL1.EnumValue(name, 'change_first', -1116)
        self.chars_after_delim = PL1.EnumValue(name, 'chars_after_delim', -1117)
        self.undelch = PL1.EnumValue(name, 'undelch', -1117)
        self.checksum_failure = PL1.EnumValue(name, 'checksum_failure', -1118)
        self.NOTchksum = PL1.EnumValue(name, '^chksum', -1118)
        self.chnadded = PL1.EnumValue(name, 'chnadded', -1119)
        self.chnl_already_added = PL1.EnumValue(name, 'chnl_already_added', -1119)
        self.chnl_already_deleted = PL1.EnumValue(name, 'chnl_already_deleted', -1120)
        self.chndltd = PL1.EnumValue(name, 'chndltd', -1120)
        self.chndltg = PL1.EnumValue(name, 'chndltg', -1121)
        self.chnl_being_deleted = PL1.EnumValue(name, 'chnl_being_deleted', -1121)
        self.chnlioma = PL1.EnumValue(name, 'chnlioma', -1122)
        self.chnl_iom_active = PL1.EnumValue(name, 'chnl_iom_active', -1122)
        self.chnl_iom_inactive = PL1.EnumValue(name, 'chnl_iom_inactive', -1123)
        self.chnnoiom = PL1.EnumValue(name, 'chnnoiom', -1123)
        self.clnzero = PL1.EnumValue(name, 'clnzero', -1124)
        self.nonzero = PL1.EnumValue(name, 'nonzero', -1124)
        self.clnovrfl = PL1.EnumValue(name, 'clnovrfl', -1125)
        self.command_line_overflow = PL1.EnumValue(name, 'command_line_overflow', -1125)
        self.command_name_not_available = PL1.EnumValue(name, 'command_name_not_available', -1126)
        self.comnotav = PL1.EnumValue(name, 'comnotav', -1126)
        self.copy_sw_on = PL1.EnumValue(name, 'copy_sw_on', -1127)
        self.copyswon = PL1.EnumValue(name, 'copyswon', -1127)
        self.cpresv = PL1.EnumValue(name, 'cpresv', -1128)
        self.cp_reserved_syntax = PL1.EnumValue(name, 'cp_reserved_syntax', -1128)
        self.cyclic_syn = PL1.EnumValue(name, 'cyclic_syn', -1129)
        self.cyc_syn = PL1.EnumValue(name, 'cyc_syn', -1129)
        self.datagain = PL1.EnumValue(name, 'datagain', -1130)
        self.data_gain = PL1.EnumValue(name, 'data_gain', -1130)
        self.data_improperly_terminated = PL1.EnumValue(name, 'data_improperly_terminated', -1131)
        self.dtnoterm = PL1.EnumValue(name, 'dtnoterm', -1131)
        self.dataloss = PL1.EnumValue(name, 'dataloss', -1132)
        self.data_loss = PL1.EnumValue(name, 'data_loss', -1132)
        self.data_seq_error = PL1.EnumValue(name, 'data_seq_error', -1133)
        self.datasqer = PL1.EnumValue(name, 'datasqer', -1133)
        self.date_conversion_error = PL1.EnumValue(name, 'date_conversion_error', -1134)
        self.daterr = PL1.EnumValue(name, 'daterr', -1134)
        self.deact_in_mem = PL1.EnumValue(name, 'deact_in_mem', -1135)
        self.deactmem = PL1.EnumValue(name, 'deactmem', -1135)
        self.defs_loop = PL1.EnumValue(name, 'defs_loop', -1136)
        self.defsloop = PL1.EnumValue(name, 'defsloop', -1136)
        self.dev_nt_assnd = PL1.EnumValue(name, 'dev_nt_assnd', -1137)
        self.notassnd = PL1.EnumValue(name, 'notassnd', -1137)
        self.dev_offset_out_of_bounds = PL1.EnumValue(name, 'dev_offset_out_of_bounds', -1138)
        self.dvoffoob = PL1.EnumValue(name, 'dvoffoob', -1138)
        self.devactiv = PL1.EnumValue(name, 'devactiv', -1139)
        self.device_active = PL1.EnumValue(name, 'device_active', -1139)
        self.device_attention = PL1.EnumValue(name, 'device_attention', -1140)
        self.dvceattn = PL1.EnumValue(name, 'dvceattn', -1140)
        self.dadwtm = PL1.EnumValue(name, 'dadwtm', -1141)
        self.device_attention_during_tm = PL1.EnumValue(name, 'device_attention_during_tm', -1141)
        self.devbusy = PL1.EnumValue(name, 'devbusy', -1142)
        self.device_busy = PL1.EnumValue(name, 'device_busy', -1142)
        self.devcdalt = PL1.EnumValue(name, 'devcdalt', -1143)
        self.device_code_alert = PL1.EnumValue(name, 'device_code_alert', -1143)
        self.dvdldef = PL1.EnumValue(name, 'dvdldef', -1144)
        self.device_deletion_deferred = PL1.EnumValue(name, 'device_deletion_deferred', -1144)
        self.devend = PL1.EnumValue(name, 'devend', -1145)
        self.device_end = PL1.EnumValue(name, 'device_end', -1145)
        self.device_limit_exceeded = PL1.EnumValue(name, 'device_limit_exceeded', -1146)
        self.devlimex = PL1.EnumValue(name, 'devlimex', -1146)
        self.devntact = PL1.EnumValue(name, 'devntact', -1147)
        self.device_not_active = PL1.EnumValue(name, 'device_not_active', -1147)
        self.device_not_usable = PL1.EnumValue(name, 'device_not_usable', -1148)
        self.devntuse = PL1.EnumValue(name, 'devntuse', -1148)
        self.xmiterr = PL1.EnumValue(name, 'xmiterr', -1149)
        self.device_parity = PL1.EnumValue(name, 'device_parity', -1149)
        self.dtNOTknown = PL1.EnumValue(name, 'dt^known', -1150)
        self.device_type_unknown = PL1.EnumValue(name, 'device_type_unknown', -1150)
        self.dial_active = PL1.EnumValue(name, 'dial_active', -1151)
        self.dialactv = PL1.EnumValue(name, 'dialactv', -1151)
        self.dial_id_busy = PL1.EnumValue(name, 'dial_id_busy', -1152)
        self.dialbusy = PL1.EnumValue(name, 'dialbusy', -1152)
        self.dir_damage = PL1.EnumValue(name, 'dir_damage', -1153)
        self.dirdamag = PL1.EnumValue(name, 'dirdamag', -1153)
        self.dirlong = PL1.EnumValue(name, 'dirlong', -1154)
        self.dirseg = PL1.EnumValue(name, 'dirseg', -1155)
        self.dsblkcnt = PL1.EnumValue(name, 'dsblkcnt', -1156)
        self.discrepant_block_count = PL1.EnumValue(name, 'discrepant_block_count', -1156)
        self.dm_journal_pages_held = PL1.EnumValue(name, 'dm_journal_pages_held', -1157)
        self.dmpghld = PL1.EnumValue(name, 'dmpghld', -1157)
        self.dmnten = PL1.EnumValue(name, 'dmnten', -1158)
        self.dm_not_enabled = PL1.EnumValue(name, 'dm_not_enabled', -1158)
        self.dmpinvld = PL1.EnumValue(name, 'dmpinvld', -1159)
        self.dmpr_in_use = PL1.EnumValue(name, 'dmpr_in_use', -1160)
        self.dmpinuse = PL1.EnumValue(name, 'dmpinuse', -1160)
        self.dmpvalid = PL1.EnumValue(name, 'dmpvalid', -1161)
        self.dt_ambiguous_time = PL1.EnumValue(name, 'dt_ambiguous_time', -1162)
        self.ambigtim = PL1.EnumValue(name, 'ambigtim', -1162)
        self.dt_bad_day_of_week = PL1.EnumValue(name, 'dt_bad_day_of_week', -1163)
        self.baddow = PL1.EnumValue(name, 'baddow', -1163)
        self.bad_dm = PL1.EnumValue(name, 'bad_dm', -1164)
        self.dt_bad_dm = PL1.EnumValue(name, 'dt_bad_dm', -1164)
        self.dt_bad_dy = PL1.EnumValue(name, 'dt_bad_dy', -1165)
        self.bad_dy = PL1.EnumValue(name, 'bad_dy', -1165)
        self.badfsel = PL1.EnumValue(name, 'badfsel', -1166)
        self.dt_bad_format_selector = PL1.EnumValue(name, 'dt_bad_format_selector', -1166)
        self.bad_fw = PL1.EnumValue(name, 'bad_fw', -1167)
        self.dt_bad_fw = PL1.EnumValue(name, 'dt_bad_fw', -1167)
        self.dt_bad_my = PL1.EnumValue(name, 'dt_bad_my', -1168)
        self.bad_my = PL1.EnumValue(name, 'bad_my', -1168)
        self.datemess = PL1.EnumValue(name, 'datemess', -1169)
        self.dt_conflict = PL1.EnumValue(name, 'dt_conflict', -1169)
        self.dt_date_not_exist = PL1.EnumValue(name, 'dt_date_not_exist', -1170)
        self.dategone = PL1.EnumValue(name, 'dategone', -1170)
        self.datebig = PL1.EnumValue(name, 'datebig', -1171)
        self.dt_date_too_big = PL1.EnumValue(name, 'dt_date_too_big', -1171)
        self.dt_date_too_small = PL1.EnumValue(name, 'dt_date_too_small', -1172)
        self.datesmal = PL1.EnumValue(name, 'datesmal', -1172)
        self.dt_hour_gt_twelve = PL1.EnumValue(name, 'dt_hour_gt_twelve', -1173)
        self.hrlarge = PL1.EnumValue(name, 'hrlarge', -1173)
        self.dt_multiple_date_spec = PL1.EnumValue(name, 'dt_multiple_date_spec', -1174)
        self.multdate = PL1.EnumValue(name, 'multdate', -1174)
        self.dt_multiple_diw_spec = PL1.EnumValue(name, 'dt_multiple_diw_spec', -1175)
        self.multdiw = PL1.EnumValue(name, 'multdiw', -1175)
        self.dt_multiple_meaning = PL1.EnumValue(name, 'dt_multiple_meaning', -1176)
        self.multmean = PL1.EnumValue(name, 'multmean', -1176)
        self.dt_multiple_time_spec = PL1.EnumValue(name, 'dt_multiple_time_spec', -1177)
        self.multtime = PL1.EnumValue(name, 'multtime', -1177)
        self.multzone = PL1.EnumValue(name, 'multzone', -1178)
        self.dt_multiple_zone_spec = PL1.EnumValue(name, 'dt_multiple_zone_spec', -1178)
        self.dt_no_format_selector = PL1.EnumValue(name, 'dt_no_format_selector', -1179)
        self.nofsel = PL1.EnumValue(name, 'nofsel', -1179)
        self.noiunit = PL1.EnumValue(name, 'noiunit', -1180)
        self.dt_no_interval_units = PL1.EnumValue(name, 'dt_no_interval_units', -1180)
        self.offbign = PL1.EnumValue(name, 'offbign', -1181)
        self.dt_offset_too_big_negative = PL1.EnumValue(name, 'dt_offset_too_big_negative', -1181)
        self.offbigp = PL1.EnumValue(name, 'offbigp', -1182)
        self.dt_offset_too_big_positive = PL1.EnumValue(name, 'dt_offset_too_big_positive', -1182)
        self.dt_size_error = PL1.EnumValue(name, 'dt_size_error', -1183)
        self.dtsizerr = PL1.EnumValue(name, 'dtsizerr', -1183)
        self.ticverr = PL1.EnumValue(name, 'ticverr', -1184)
        self.dt_time_conversion_error = PL1.EnumValue(name, 'dt_time_conversion_error', -1184)
        self.dt_unknown_time_language = PL1.EnumValue(name, 'dt_unknown_time_language', -1185)
        self.badtlang = PL1.EnumValue(name, 'badtlang', -1185)
        self.badword = PL1.EnumValue(name, 'badword', -1186)
        self.dt_unknown_word = PL1.EnumValue(name, 'dt_unknown_word', -1186)
        self.yearbig = PL1.EnumValue(name, 'yearbig', -1187)
        self.dt_year_too_big = PL1.EnumValue(name, 'dt_year_too_big', -1187)
        self.yearsmal = PL1.EnumValue(name, 'yearsmal', -1188)
        self.dt_year_too_small = PL1.EnumValue(name, 'dt_year_too_small', -1188)
        self.dup_ent_name = PL1.EnumValue(name, 'dup_ent_name', -1189)
        self.dupename = PL1.EnumValue(name, 'dupename', -1189)
        self.duplicate_file_id = PL1.EnumValue(name, 'duplicate_file_id', -1190)
        self.dupfid = PL1.EnumValue(name, 'dupfid', -1190)
        self.dup_req = PL1.EnumValue(name, 'dup_req', -1191)
        self.duplicate_request = PL1.EnumValue(name, 'duplicate_request', -1191)
        self.echostop = PL1.EnumValue(name, 'echostop', -1192)
        self.echnego_awaiting_stop_sync = PL1.EnumValue(name, 'echnego_awaiting_stop_sync', -1192)
        self.ectinit = PL1.EnumValue(name, 'ectinit', -1193)
        self.ect_already_initialized = PL1.EnumValue(name, 'ect_already_initialized', -1193)
        self.ectfull = PL1.EnumValue(name, 'ectfull', -1194)
        self.ect_full = PL1.EnumValue(name, 'ect_full', -1194)
        self.eight_unaligned = PL1.EnumValue(name, 'eight_unaligned', -1195)
        self.not8alin = PL1.EnumValue(name, 'not8alin', -1195)
        self.empty_acl = PL1.EnumValue(name, 'empty_acl', -1196)
        self.emptyacl = PL1.EnumValue(name, 'emptyacl', -1196)
        self.empty_ac = PL1.EnumValue(name, 'empty_ac', -1197)
        self.empty_archive = PL1.EnumValue(name, 'empty_archive', -1197)
        self.mt_file = PL1.EnumValue(name, 'mt_file', -1198)
        self.empty_file = PL1.EnumValue(name, 'empty_file', -1198)
        self.empsrls = PL1.EnumValue(name, 'empsrls', -1199)
        self.empty_search_list = PL1.EnumValue(name, 'empty_search_list', -1199)
        self.eoi = PL1.EnumValue(name, 'eoi', -1200)
        self.end_of_info = PL1.EnumValue(name, 'end_of_info', -1200)
        self.entlong = PL1.EnumValue(name, 'entlong', -1201)
        self.eof_record = PL1.EnumValue(name, 'eof_record', -1202)
        self.eofr = PL1.EnumValue(name, 'eofr', -1202)
        self.eov_on_write = PL1.EnumValue(name, 'eov_on_write', -1203)
        self.eovonw = PL1.EnumValue(name, 'eovonw', -1203)
        self.callnmsk = PL1.EnumValue(name, 'callnmsk', -1204)
        self.event_calls_not_masked = PL1.EnumValue(name, 'event_calls_not_masked', -1204)
        self.event_channel_cutoff = PL1.EnumValue(name, 'event_channel_cutoff', -1205)
        self.chnout = PL1.EnumValue(name, 'chnout', -1205)
        self.chnnout = PL1.EnumValue(name, 'chnnout', -1206)
        self.event_channel_not_cutoff = PL1.EnumValue(name, 'event_channel_not_cutoff', -1206)
        self.fatal_error = PL1.EnumValue(name, 'fatal_error', -1207)
        self.fatalerr = PL1.EnumValue(name, 'fatalerr', -1207)
        self.flabort = PL1.EnumValue(name, 'flabort', -1208)
        self.file_aborted = PL1.EnumValue(name, 'file_aborted', -1208)
        self.fileopen = PL1.EnumValue(name, 'fileopen', -1209)
        self.file_already_opened = PL1.EnumValue(name, 'file_already_opened', -1209)
        self.filebusy = PL1.EnumValue(name, 'filebusy', -1210)
        self.file_busy = PL1.EnumValue(name, 'file_busy', -1210)
        self.file_is_full = PL1.EnumValue(name, 'file_is_full', -1211)
        self.filefull = PL1.EnumValue(name, 'filefull', -1211)
        self.file_not_opened = PL1.EnumValue(name, 'file_not_opened', -1212)
        self.not_open = PL1.EnumValue(name, 'not_open', -1212)
        self.fim_fault = PL1.EnumValue(name, 'fim_fault', -1213)
        self.fimflt = PL1.EnumValue(name, 'fimflt', -1213)
        self.first_reference_trap = PL1.EnumValue(name, 'first_reference_trap', -1214)
        self.firstref = PL1.EnumValue(name, 'firstref', -1214)
        self.fnp_down = PL1.EnumValue(name, 'fnp_down', -1215)
        self.forcunas = PL1.EnumValue(name, 'forcunas', -1216)
        self.force_unassign = PL1.EnumValue(name, 'force_unassign', -1216)
        self.frame_scope_err = PL1.EnumValue(name, 'frame_scope_err', -1217)
        self.fscoperr = PL1.EnumValue(name, 'fscoperr', -1217)
        self.fsdisk_bad_label = PL1.EnumValue(name, 'fsdisk_bad_label', -1218)
        self.fsbdlb = PL1.EnumValue(name, 'fsbdlb', -1218)
        self.fsdinuse = PL1.EnumValue(name, 'fsdinuse', -1219)
        self.fsdisk_drive_in_use = PL1.EnumValue(name, 'fsdisk_drive_in_use', -1219)
        self.fsdisk_not_ready = PL1.EnumValue(name, 'fsdisk_not_ready', -1220)
        self.fsNOTrdy = PL1.EnumValue(name, 'fs^rdy', -1220)
        self.fsNOTsalv = PL1.EnumValue(name, 'fs^salv', -1221)
        self.fsdisk_not_salv = PL1.EnumValue(name, 'fsdisk_not_salv', -1221)
        self.fsdisk_not_storage = PL1.EnumValue(name, 'fsdisk_not_storage', -1222)
        self.fsNOTstor = PL1.EnumValue(name, 'fs^stor', -1222)
        self.fsoldlb = PL1.EnumValue(name, 'fsoldlb', -1223)
        self.fsdisk_old_label = PL1.EnumValue(name, 'fsdisk_old_label', -1223)
        self.fsdisk_old_vtoc = PL1.EnumValue(name, 'fsdisk_old_vtoc', -1224)
        self.fsoldvt = PL1.EnumValue(name, 'fsoldvt', -1224)
        self.fsdisk_phydev_err = PL1.EnumValue(name, 'fsdisk_phydev_err', -1225)
        self.fsdeverr = PL1.EnumValue(name, 'fsdeverr', -1225)
        self.fsdisk_pvtx_oob = PL1.EnumValue(name, 'fsdisk_pvtx_oob', -1226)
        self.fspvxoob = PL1.EnumValue(name, 'fspvxoob', -1226)
        self.full_hashtbl = PL1.EnumValue(name, 'full_hashtbl', -1227)
        self.fullhash = PL1.EnumValue(name, 'fullhash', -1227)
        self.fulldir = PL1.EnumValue(name, 'fulldir', -1228)
        self.hcsdw = PL1.EnumValue(name, 'hcsdw', -1229)
        self.hardcore_sdw = PL1.EnumValue(name, 'hardcore_sdw', -1229)
        self.higher_inconsistency = PL1.EnumValue(name, 'higher_inconsistency', -1230)
        self.hi_incon = PL1.EnumValue(name, 'hi_incon', -1230)
        self.id_already_exists = PL1.EnumValue(name, 'id_already_exists', -1231)
        self.idexists = PL1.EnumValue(name, 'idexists', -1231)
        self.idnotfnd = PL1.EnumValue(name, 'idnotfnd', -1232)
        self.id_not_found = PL1.EnumValue(name, 'id_not_found', -1232)
        self.bad_act = PL1.EnumValue(name, 'bad_act', -1233)
        self.illegal_activation = PL1.EnumValue(name, 'illegal_activation', -1233)
        self.illegal_deactivation = PL1.EnumValue(name, 'illegal_deactivation', -1234)
        self.deactive = PL1.EnumValue(name, 'deactive', -1234)
        self.bad_ft2 = PL1.EnumValue(name, 'bad_ft2', -1235)
        self.illegal_ft2 = PL1.EnumValue(name, 'illegal_ft2', -1235)
        self.illegal_record_size = PL1.EnumValue(name, 'illegal_record_size', -1236)
        self.rec_size = PL1.EnumValue(name, 'rec_size', -1236)
        self.impbdfmt = PL1.EnumValue(name, 'impbdfmt', -1237)
        self.imp_bad_format = PL1.EnumValue(name, 'imp_bad_format', -1237)
        self.imp_bad_status = PL1.EnumValue(name, 'imp_bad_status', -1238)
        self.impbadst = PL1.EnumValue(name, 'impbadst', -1238)
        self.imp_down = PL1.EnumValue(name, 'imp_down', -1239)
        self.impdown = PL1.EnumValue(name, 'impdown', -1239)
        self.imp_rfnm_pending = PL1.EnumValue(name, 'imp_rfnm_pending', -1240)
        self.imprfnm = PL1.EnumValue(name, 'imprfnm', -1240)
        self.baddtfmt = PL1.EnumValue(name, 'baddtfmt', -1241)
        self.improper_data_format = PL1.EnumValue(name, 'improper_data_format', -1241)
        self.badterm = PL1.EnumValue(name, 'badterm', -1242)
        self.improper_termination = PL1.EnumValue(name, 'improper_termination', -1242)
        self.incompatible_attach = PL1.EnumValue(name, 'incompatible_attach', -1243)
        self.attNEopn = PL1.EnumValue(name, 'att^=opn', -1243)
        self.incencmd = PL1.EnumValue(name, 'incencmd', -1244)
        self.incompatible_encoding_mode = PL1.EnumValue(name, 'incompatible_encoding_mode', -1244)
        self.incompatible_file_attribute = PL1.EnumValue(name, 'incompatible_file_attribute', -1245)
        self.incflatt = PL1.EnumValue(name, 'incflatt', -1245)
        self.incompatible_term_type = PL1.EnumValue(name, 'incompatible_term_type', -1246)
        self.intrmtyp = PL1.EnumValue(name, 'intrmtyp', -1246)
        self.incomnam = PL1.EnumValue(name, 'incomnam', -1247)
        self.incomplete_access_name = PL1.EnumValue(name, 'incomplete_access_name', -1247)
        self.incnstnt = PL1.EnumValue(name, 'incnstnt', -1248)
        self.inconsistent = PL1.EnumValue(name, 'inconsistent', -1248)
        self.badect = PL1.EnumValue(name, 'badect', -1249)
        self.inconsistent_ect = PL1.EnumValue(name, 'inconsistent_ect', -1249)
        self.incnsmsf = PL1.EnumValue(name, 'incnsmsf', -1250)
        self.inconsistent_msf = PL1.EnumValue(name, 'inconsistent_msf', -1250)
        self.inconsistent_rnt = PL1.EnumValue(name, 'inconsistent_rnt', -1251)
        self.badrnt = PL1.EnumValue(name, 'badrnt', -1251)
        self.badsst = PL1.EnumValue(name, 'badsst', -1252)
        self.inconsistent_sst = PL1.EnumValue(name, 'inconsistent_sst', -1252)
        self.inconsistent_object_msf = PL1.EnumValue(name, 'inconsistent_object_msf', -1253)
        self.incobmsf = PL1.EnumValue(name, 'incobmsf', -1253)
        self.incacc = PL1.EnumValue(name, 'incacc', -1254)
        self.incorrect_access = PL1.EnumValue(name, 'incorrect_access', -1254)
        self.incdevt = PL1.EnumValue(name, 'incdevt', -1255)
        self.incorrect_device_type = PL1.EnumValue(name, 'incorrect_device_type', -1255)
        self.incorrect_volume_type = PL1.EnumValue(name, 'incorrect_volume_type', -1256)
        self.incvolt = PL1.EnumValue(name, 'incvolt', -1256)
        self.infcnt_non_zero = PL1.EnumValue(name, 'infcnt_non_zero', -1257)
        self.makunk = PL1.EnumValue(name, 'makunk', -1257)
        self.insufacc = PL1.EnumValue(name, 'insufacc', -1258)
        self.mdc_no_access = PL1.EnumValue(name, 'mdc_no_access', -1258)
        self.insufficient_access = PL1.EnumValue(name, 'insufficient_access', -1258)
        self.insufficient_open = PL1.EnumValue(name, 'insufficient_open', -1259)
        self.insufopn = PL1.EnumValue(name, 'insufopn', -1259)
        self.invarsz = PL1.EnumValue(name, 'invarsz', -1260)
        self.invalid_array_size = PL1.EnumValue(name, 'invalid_array_size', -1260)
        self.invalid_ascii = PL1.EnumValue(name, 'invalid_ascii', -1261)
        self.invascii = PL1.EnumValue(name, 'invascii', -1261)
        self.invbsr = PL1.EnumValue(name, 'invbsr', -1262)
        self.invalid_backspace_read = PL1.EnumValue(name, 'invalid_backspace_read', -1262)
        self.invblk = PL1.EnumValue(name, 'invblk', -1263)
        self.invalid_block_length = PL1.EnumValue(name, 'invalid_block_length', -1263)
        self.invalid_channel = PL1.EnumValue(name, 'invalid_channel', -1264)
        self.invalchn = PL1.EnumValue(name, 'invalchn', -1264)
        self.invalcpy = PL1.EnumValue(name, 'invalcpy', -1265)
        self.invalid_copy = PL1.EnumValue(name, 'invalid_copy', -1265)
        self.invcseg = PL1.EnumValue(name, 'invcseg', -1266)
        self.invalid_cseg = PL1.EnumValue(name, 'invalid_cseg', -1266)
        self.invalid_delay_value = PL1.EnumValue(name, 'invalid_delay_value', -1267)
        self.invdelay = PL1.EnumValue(name, 'invdelay', -1267)
        self.invdev = PL1.EnumValue(name, 'invdev', -1268)
        self.invalid_device = PL1.EnumValue(name, 'invalid_device', -1268)
        self.invalid_dm_journal_index = PL1.EnumValue(name, 'invalid_dm_journal_index', -1269)
        self.invjx = PL1.EnumValue(name, 'invjx', -1269)
        self.invalid_elsize = PL1.EnumValue(name, 'invalid_elsize', -1270)
        self.invelsiz = PL1.EnumValue(name, 'invelsiz', -1270)
        self.invexp = PL1.EnumValue(name, 'invexp', -1271)
        self.invalid_expiration = PL1.EnumValue(name, 'invalid_expiration', -1271)
        self.invalid_file_set_format = PL1.EnumValue(name, 'invalid_file_set_format', -1272)
        self.infsfmt = PL1.EnumValue(name, 'infsfmt', -1272)
        self.invalid_heap = PL1.EnumValue(name, 'invalid_heap', -1273)
        self.bad_heap = PL1.EnumValue(name, 'bad_heap', -1273)
        self.inhpvsiz = PL1.EnumValue(name, 'inhpvsiz', -1274)
        self.invalid_heap_var_size = PL1.EnumValue(name, 'invalid_heap_var_size', -1274)
        self.invlbfmt = PL1.EnumValue(name, 'invlbfmt', -1275)
        self.invalid_label_format = PL1.EnumValue(name, 'invalid_label_format', -1275)
        self.invalid_line_type = PL1.EnumValue(name, 'invalid_line_type', -1276)
        self.invlntyp = PL1.EnumValue(name, 'invlntyp', -1276)
        self.invalock = PL1.EnumValue(name, 'invalock', -1277)
        self.invalid_lock_reset = PL1.EnumValue(name, 'invalid_lock_reset', -1277)
        self.mlLTcl = PL1.EnumValue(name, 'ml<cl', -1278)
        self.invalid_max_length = PL1.EnumValue(name, 'invalid_max_length', -1278)
        self.invalid_mode = PL1.EnumValue(name, 'invalid_mode', -1279)
        self.invmode = PL1.EnumValue(name, 'invmode', -1279)
        self.nomvqmax = PL1.EnumValue(name, 'nomvqmax', -1280)
        self.invalid_move_qmax = PL1.EnumValue(name, 'invalid_move_qmax', -1280)
        self.nomvquot = PL1.EnumValue(name, 'nomvquot', -1281)
        self.invalid_move_quota = PL1.EnumValue(name, 'invalid_move_quota', -1281)
        self.invmpx = PL1.EnumValue(name, 'invmpx', -1282)
        self.invalid_mpx_type = PL1.EnumValue(name, 'invalid_mpx_type', -1282)
        self.invalid_preaccess_command = PL1.EnumValue(name, 'invalid_preaccess_command', -1283)
        self.inprecom = PL1.EnumValue(name, 'inprecom', -1283)
        self.invprjgt = PL1.EnumValue(name, 'invprjgt', -1284)
        self.invalid_project_for_gate = PL1.EnumValue(name, 'invalid_project_for_gate', -1284)
        self.invalid_ptr_target = PL1.EnumValue(name, 'invalid_ptr_target', -1285)
        self.invprtar = PL1.EnumValue(name, 'invprtar', -1285)
        self.invalid_pvtx = PL1.EnumValue(name, 'invalid_pvtx', -1286)
        self.invpvtx = PL1.EnumValue(name, 'invpvtx', -1286)
        self.invread = PL1.EnumValue(name, 'invread', -1287)
        self.invalid_read = PL1.EnumValue(name, 'invalid_read', -1287)
        self.invalid_record_desc = PL1.EnumValue(name, 'invalid_record_desc', -1288)
        self.invrdes = PL1.EnumValue(name, 'invrdes', -1288)
        self.invrec = PL1.EnumValue(name, 'invrec', -1289)
        self.invalid_record_length = PL1.EnumValue(name, 'invalid_record_length', -1289)
        self.invrscst = PL1.EnumValue(name, 'invrscst', -1290)
        self.invalid_resource_state = PL1.EnumValue(name, 'invalid_resource_state', -1290)
        self.invalid_ring_brackets = PL1.EnumValue(name, 'invalid_ring_brackets', -1291)
        self.badringb = PL1.EnumValue(name, 'badringb', -1291)
        self.invseek = PL1.EnumValue(name, 'invseek', -1292)
        self.invalid_seek_last_bound = PL1.EnumValue(name, 'invalid_seek_last_bound', -1292)
        self.invsetdl = PL1.EnumValue(name, 'invsetdl', -1293)
        self.invalid_setdelim = PL1.EnumValue(name, 'invalid_setdelim', -1293)
        self.badstkcr = PL1.EnumValue(name, 'badstkcr', -1294)
        self.invalid_stack_creation = PL1.EnumValue(name, 'invalid_stack_creation', -1294)
        self.invalst = PL1.EnumValue(name, 'invalst', -1295)
        self.invalid_state = PL1.EnumValue(name, 'invalid_state', -1295)
        self.invsbsys = PL1.EnumValue(name, 'invsbsys', -1296)
        self.invalid_subsystem = PL1.EnumValue(name, 'invalid_subsystem', -1296)
        self.invalid_system_type = PL1.EnumValue(name, 'invalid_system_type', -1297)
        self.badsystp = PL1.EnumValue(name, 'badsystp', -1297)
        self.invalid_tape_record_length = PL1.EnumValue(name, 'invalid_tape_record_length', -1298)
        self.badtaprl = PL1.EnumValue(name, 'badtaprl', -1298)
        self.badtpval = PL1.EnumValue(name, 'badtpval', -1299)
        self.invalid_tp_value = PL1.EnumValue(name, 'invalid_tp_value', -1299)
        self.invalid_volume_sequence = PL1.EnumValue(name, 'invalid_volume_sequence', -1300)
        self.involseg = PL1.EnumValue(name, 'involseg', -1300)
        self.invalid_vtoce = PL1.EnumValue(name, 'invalid_vtoce', -1301)
        self.invvtoce = PL1.EnumValue(name, 'invvtoce', -1301)
        self.invvtocx = PL1.EnumValue(name, 'invvtocx', -1302)
        self.invalid_vtocx = PL1.EnumValue(name, 'invalid_vtocx', -1302)
        self.invwrite = PL1.EnumValue(name, 'invwrite', -1303)
        self.invalid_write = PL1.EnumValue(name, 'invalid_write', -1303)
        self.invalidsegno = PL1.EnumValue(name, 'invalidsegno', -1304)
        self.badsegno = PL1.EnumValue(name, 'badsegno', -1304)
        self.io_assigned = PL1.EnumValue(name, 'io_assigned', -1305)
        self.ioassgn = PL1.EnumValue(name, 'ioassgn', -1305)
        self.ioconf = PL1.EnumValue(name, 'ioconf', -1306)
        self.io_configured = PL1.EnumValue(name, 'io_configured', -1306)
        self.ionopath = PL1.EnumValue(name, 'ionopath', -1307)
        self.io_no_path = PL1.EnumValue(name, 'io_no_path', -1307)
        self.nopermit = PL1.EnumValue(name, 'nopermit', -1308)
        self.io_no_permission = PL1.EnumValue(name, 'io_no_permission', -1308)
        self.ioNOTassgn = PL1.EnumValue(name, 'io^assgn', -1309)
        self.io_not_assigned = PL1.EnumValue(name, 'io_not_assigned', -1309)
        self.io_not_available = PL1.EnumValue(name, 'io_not_available', -1310)
        self.ioNOTavail = PL1.EnumValue(name, 'io^avail', -1310)
        self.io_not_configured = PL1.EnumValue(name, 'io_not_configured', -1311)
        self.ioNOTconf = PL1.EnumValue(name, 'io^conf', -1311)
        self.ioNOTdef = PL1.EnumValue(name, 'io^def', -1312)
        self.io_not_defined = PL1.EnumValue(name, 'io_not_defined', -1312)
        self.stilasnd = PL1.EnumValue(name, 'stilasnd', -1313)
        self.io_still_assnd = PL1.EnumValue(name, 'io_still_assnd', -1313)
        self.ioaterr = PL1.EnumValue(name, 'ioaterr', -1314)
        self.ioat_err = PL1.EnumValue(name, 'ioat_err', -1314)
        self.iomaadd = PL1.EnumValue(name, 'iomaadd', -1315)
        self.iom_already_added = PL1.EnumValue(name, 'iom_already_added', -1315)
        self.iomadel = PL1.EnumValue(name, 'iomadel', -1316)
        self.iom_already_deleted = PL1.EnumValue(name, 'iom_already_deleted', -1316)
        self.iom_connect_fatal = PL1.EnumValue(name, 'iom_connect_fatal', -1317)
        self.iomfatal = PL1.EnumValue(name, 'iomfatal', -1317)
        self.iom_wrong_mailbox = PL1.EnumValue(name, 'iom_wrong_mailbox', -1318)
        self.iombadmb = PL1.EnumValue(name, 'iombadmb', -1318)
        self.iom_wrong_number = PL1.EnumValue(name, 'iom_wrong_number', -1319)
        self.iombadnm = PL1.EnumValue(name, 'iombadnm', -1319)
        self.ionmnact = PL1.EnumValue(name, 'ionmnact', -1320)
        self.ioname_not_active = PL1.EnumValue(name, 'ioname_not_active', -1320)
        self.ionmnfnd = PL1.EnumValue(name, 'ionmnfnd', -1321)
        self.ioname_not_found = PL1.EnumValue(name, 'ioname_not_found', -1321)
        self.ionmat = PL1.EnumValue(name, 'ionmat', -1322)
        self.ipsoccur = PL1.EnumValue(name, 'ipsoccur', -1323)
        self.ips_has_occurred = PL1.EnumValue(name, 'ips_has_occurred', -1323)
        self.item_too_big = PL1.EnumValue(name, 'item_too_big', -1324)
        self.ittoobig = PL1.EnumValue(name, 'ittoobig', -1324)
        self.itt_overflow = PL1.EnumValue(name, 'itt_overflow', -1325)
        self.ittfull = PL1.EnumValue(name, 'ittfull', -1325)
        self.key_dup = PL1.EnumValue(name, 'key_dup', -1326)
        self.key_duplication = PL1.EnumValue(name, 'key_duplication', -1326)
        self.key_order = PL1.EnumValue(name, 'key_order', -1327)
        self.keyorder = PL1.EnumValue(name, 'keyorder', -1327)
        self.kothrngs = PL1.EnumValue(name, 'kothrngs', -1328)
        self.known_in_other_rings = PL1.EnumValue(name, 'known_in_other_rings', -1328)
        self.last_reference = PL1.EnumValue(name, 'last_reference', -1329)
        self.last_ref = PL1.EnumValue(name, 'last_ref', -1329)
        self.lesserr = PL1.EnumValue(name, 'lesserr', -1330)
        self.lnstatp = PL1.EnumValue(name, 'lnstatp', -1331)
        self.line_status_pending = PL1.EnumValue(name, 'line_status_pending', -1331)
        self.link = PL1.EnumValue(name, 'link', -1332)
        self.linkmode = PL1.EnumValue(name, 'linkmode', -1333)
        self.linkmoderr = PL1.EnumValue(name, 'linkmoderr', -1333)
        self.listen_stopped = PL1.EnumValue(name, 'listen_stopped', -1334)
        self.lstnstop = PL1.EnumValue(name, 'lstnstop', -1334)
        self.lockinv = PL1.EnumValue(name, 'lockinv', -1335)
        self.lock_is_invalid = PL1.EnumValue(name, 'lock_is_invalid', -1335)
        self.lock_not_locked = PL1.EnumValue(name, 'lock_not_locked', -1336)
        self.unlocked = PL1.EnumValue(name, 'unlocked', -1336)
        self.lock_wait_time_exceeded = PL1.EnumValue(name, 'lock_wait_time_exceeded', -1337)
        self.loctimex = PL1.EnumValue(name, 'loctimex', -1337)
        self.locked_by_other_process = PL1.EnumValue(name, 'locked_by_other_process', -1338)
        self.hislock = PL1.EnumValue(name, 'hislock', -1338)
        self.mylock = PL1.EnumValue(name, 'mylock', -1339)
        self.locked_by_this_process = PL1.EnumValue(name, 'locked_by_this_process', -1339)
        self.logNOTtype = PL1.EnumValue(name, 'log^type', -1340)
        self.log_message_invalid_type = PL1.EnumValue(name, 'log_message_invalid_type', -1340)
        self.loginop = PL1.EnumValue(name, 'loginop', -1341)
        self.log_out_of_service = PL1.EnumValue(name, 'log_out_of_service', -1341)
        self.logbust = PL1.EnumValue(name, 'logbust', -1342)
        self.log_segment_damaged = PL1.EnumValue(name, 'log_segment_damaged', -1342)
        self.log_segment_empty = PL1.EnumValue(name, 'log_segment_empty', -1343)
        self.logempty = PL1.EnumValue(name, 'logempty', -1343)
        self.log_segment_full = PL1.EnumValue(name, 'log_segment_full', -1344)
        self.logfull = PL1.EnumValue(name, 'logfull', -1344)
        self.log_segment_invalid = PL1.EnumValue(name, 'log_segment_invalid', -1345)
        self.logNOTval = PL1.EnumValue(name, 'log^val', -1345)
        self.logNOTinit = PL1.EnumValue(name, 'log^init', -1346)
        self.log_uninitialized = PL1.EnumValue(name, 'log_uninitialized', -1346)
        self.log_vol_full = PL1.EnumValue(name, 'log_vol_full', -1347)
        self.logvolfl = PL1.EnumValue(name, 'logvolfl', -1347)
        self.logGTlstn = PL1.EnumValue(name, 'log>lstn', -1348)
        self.log_wakeup_table_full = PL1.EnumValue(name, 'log_wakeup_table_full', -1348)
        self.LViscon = PL1.EnumValue(name, 'LViscon', -1349)
        self.logical_volume_is_connected = PL1.EnumValue(name, 'logical_volume_is_connected', -1349)
        self.LVisdef = PL1.EnumValue(name, 'LVisdef', -1350)
        self.logical_volume_is_defined = PL1.EnumValue(name, 'logical_volume_is_defined', -1350)
        self.logical_volume_not_connected = PL1.EnumValue(name, 'logical_volume_not_connected', -1351)
        self.LVnotcon = PL1.EnumValue(name, 'LVnotcon', -1351)
        self.logical_volume_not_defined = PL1.EnumValue(name, 'logical_volume_not_defined', -1352)
        self.LVnotdef = PL1.EnumValue(name, 'LVnotdef', -1352)
        self.LVT_full = PL1.EnumValue(name, 'LVT_full', -1353)
        self.logical_volume_table_full = PL1.EnumValue(name, 'logical_volume_table_full', -1353)
        self.long_rec = PL1.EnumValue(name, 'long_rec', -1354)
        self.long_record = PL1.EnumValue(name, 'long_record', -1354)
        self.longeql = PL1.EnumValue(name, 'longeql', -1355)
        self.lost_device_position = PL1.EnumValue(name, 'lost_device_position', -1356)
        self.lstdevps = PL1.EnumValue(name, 'lstdevps', -1356)
        self.low_ring = PL1.EnumValue(name, 'low_ring', -1357)
        self.lower_ring = PL1.EnumValue(name, 'lower_ring', -1357)
        self.bad_ring_brackets = PL1.EnumValue(name, 'bad_ring_brackets', -1357)
        self.badlstmp = PL1.EnumValue(name, 'badlstmp', -1358)
        self.malformed_list_template_entry = PL1.EnumValue(name, 'malformed_list_template_entry', -1358)
        self.maskchan = PL1.EnumValue(name, 'maskchan', -1359)
        self.masked_channel = PL1.EnumValue(name, 'masked_channel', -1359)
        self.mastrdir = PL1.EnumValue(name, 'mastrdir', -1360)
        self.master_dir = PL1.EnumValue(name, 'master_dir', -1360)
        self.max_depth_exceeded = PL1.EnumValue(name, 'max_depth_exceeded', -1361)
        self.GTlevels = PL1.EnumValue(name, '>levels', -1361)
        self.mc_no_c_permission = PL1.EnumValue(name, 'mc_no_c_permission', -1362)
        self.mcNOTm = PL1.EnumValue(name, 'mc^m', -1362)
        self.mc_no_d_permission = PL1.EnumValue(name, 'mc_no_d_permission', -1363)
        self.mcNOTd = PL1.EnumValue(name, 'mc^d', -1363)
        self.mcNOTq = PL1.EnumValue(name, 'mc^q', -1364)
        self.mc_no_q_permission = PL1.EnumValue(name, 'mc_no_q_permission', -1364)
        self.mcNOTr = PL1.EnumValue(name, 'mc^r', -1365)
        self.mc_no_r_permission = PL1.EnumValue(name, 'mc_no_r_permission', -1365)
        self.mdc_bad_quota = PL1.EnumValue(name, 'mdc_bad_quota', -1366)
        self.mdcbadq = PL1.EnumValue(name, 'mdcbadq', -1366)
        self.mdc_exec_access = PL1.EnumValue(name, 'mdc_exec_access', -1367)
        self.mdcnoex = PL1.EnumValue(name, 'mdcnoex', -1367)
        self.mdcilacc = PL1.EnumValue(name, 'mdcilacc', -1368)
        self.mdc_illegal_account = PL1.EnumValue(name, 'mdc_illegal_account', -1368)
        self.mdc_illegal_owner = PL1.EnumValue(name, 'mdc_illegal_owner', -1369)
        self.mdcilown = PL1.EnumValue(name, 'mdcilown', -1369)
        self.mdc_mdir_registered = PL1.EnumValue(name, 'mdc_mdir_registered', -1370)
        self.mdcmdirg = PL1.EnumValue(name, 'mdcmdirg', -1370)
        self.mdc_mdirs_registered = PL1.EnumValue(name, 'mdc_mdirs_registered', -1371)
        self.mdcmdreg = PL1.EnumValue(name, 'mdcmdreg', -1371)
        self.mdcnoact = PL1.EnumValue(name, 'mdcnoact', -1372)
        self.mdc_no_account = PL1.EnumValue(name, 'mdc_no_account', -1372)
        self.mdcnoq = PL1.EnumValue(name, 'mdcnoq', -1373)
        self.mdc_no_quota = PL1.EnumValue(name, 'mdc_no_quota', -1373)
        self.mdcnoqa = PL1.EnumValue(name, 'mdcnoqa', -1374)
        self.mdc_no_quota_account = PL1.EnumValue(name, 'mdc_no_quota_account', -1374)
        self.mdc_not_mdir = PL1.EnumValue(name, 'mdc_not_mdir', -1375)
        self.mdcnotmd = PL1.EnumValue(name, 'mdcnotmd', -1375)
        self.mdcpathd = PL1.EnumValue(name, 'mdcpathd', -1376)
        self.mdc_path_dup = PL1.EnumValue(name, 'mdc_path_dup', -1376)
        self.mdcdparg = PL1.EnumValue(name, 'mdcdparg', -1377)
        self.mdc_path_dup_args = PL1.EnumValue(name, 'mdc_path_dup_args', -1377)
        self.mdcpathn = PL1.EnumValue(name, 'mdcpathn', -1378)
        self.mdc_path_not_found = PL1.EnumValue(name, 'mdc_path_not_found', -1378)
        self.mdc_path_restrict = PL1.EnumValue(name, 'mdc_path_restrict', -1379)
        self.mdcpathr = PL1.EnumValue(name, 'mdcpathr', -1379)
        self.mdc_some_error = PL1.EnumValue(name, 'mdc_some_error', -1380)
        self.mdcsome = PL1.EnumValue(name, 'mdcsome', -1380)
        self.mdc_unregistered_mdir = PL1.EnumValue(name, 'mdc_unregistered_mdir', -1381)
        self.mdcunreg = PL1.EnumValue(name, 'mdcunreg', -1381)
        self.media_not_removable = PL1.EnumValue(name, 'media_not_removable', -1382)
        self.mdntrmvb = PL1.EnumValue(name, 'mdntrmvb', -1382)
        self.messages_deferred = PL1.EnumValue(name, 'messages_deferred', -1383)
        self.msgdefer = PL1.EnumValue(name, 'msgdefer', -1383)
        self.msgs_off = PL1.EnumValue(name, 'msgs_off', -1384)
        self.messages_off = PL1.EnumValue(name, 'messages_off', -1384)
        self.mismatit = PL1.EnumValue(name, 'mismatit', -1385)
        self.mismatched_iter = PL1.EnumValue(name, 'mismatched_iter', -1385)
        self.missent = PL1.EnumValue(name, 'missent', -1386)
        self.mode_string_truncated = PL1.EnumValue(name, 'mode_string_truncated', -1387)
        self.mdetrunc = PL1.EnumValue(name, 'mdetrunc', -1387)
        self.moderr = PL1.EnumValue(name, 'moderr', -1388)
        self.mtnotrdy = PL1.EnumValue(name, 'mtnotrdy', -1389)
        self.mount_not_ready = PL1.EnumValue(name, 'mount_not_ready', -1389)
        self.mtpend = PL1.EnumValue(name, 'mtpend', -1390)
        self.mount_pending = PL1.EnumValue(name, 'mount_pending', -1390)
        self.mpx_down = PL1.EnumValue(name, 'mpx_down', -1391)
        self.msf = PL1.EnumValue(name, 'msf', -1392)
        self.multioat = PL1.EnumValue(name, 'multioat', -1393)
        self.multiple_io_attachment = PL1.EnumValue(name, 'multiple_io_attachment', -1393)
        self.mylock = PL1.EnumValue(name, 'mylock', -1394)
        self.name_not_found = PL1.EnumValue(name, 'name_not_found', -1395)
        self.namenfd = PL1.EnumValue(name, 'namenfd', -1395)
        self.namedup = PL1.EnumValue(name, 'namedup', -1396)
        self.ncp_error = PL1.EnumValue(name, 'ncp_error', -1397)
        self.ncperror = PL1.EnumValue(name, 'ncperror', -1397)
        self.negative_nelem = PL1.EnumValue(name, 'negative_nelem', -1398)
        self.negnelem = PL1.EnumValue(name, 'negnelem', -1398)
        self.negative_offset = PL1.EnumValue(name, 'negative_offset', -1399)
        self.negofset = PL1.EnumValue(name, 'negofset', -1399)
        self.net_already_icp = PL1.EnumValue(name, 'net_already_icp', -1400)
        self.sock_icp = PL1.EnumValue(name, 'sock_icp', -1400)
        self.net_bad_gender = PL1.EnumValue(name, 'net_bad_gender', -1401)
        self.netbgend = PL1.EnumValue(name, 'netbgend', -1401)
        self.net_fhost_down = PL1.EnumValue(name, 'net_fhost_down', -1402)
        self.fhostdwn = PL1.EnumValue(name, 'fhostdwn', -1402)
        self.net_fhost_inactive = PL1.EnumValue(name, 'net_fhost_inactive', -1403)
        self.netfhost = PL1.EnumValue(name, 'netfhost', -1403)
        self.net_fimp_down = PL1.EnumValue(name, 'net_fimp_down', -1404)
        self.fimpdwn = PL1.EnumValue(name, 'fimpdwn', -1404)
        self.bad_icp = PL1.EnumValue(name, 'bad_icp', -1405)
        self.net_icp_bad_state = PL1.EnumValue(name, 'net_icp_bad_state', -1405)
        self.net_icp_error = PL1.EnumValue(name, 'net_icp_error', -1406)
        self.icp_err = PL1.EnumValue(name, 'icp_err', -1406)
        self.stillicp = PL1.EnumValue(name, 'stillicp', -1407)
        self.net_icp_not_concluded = PL1.EnumValue(name, 'net_icp_not_concluded', -1407)
        self.netstate = PL1.EnumValue(name, 'netstate', -1408)
        self.net_invalid_state = PL1.EnumValue(name, 'net_invalid_state', -1408)
        self.net_no_connect_permission = PL1.EnumValue(name, 'net_no_connect_permission', -1409)
        self.noconect = PL1.EnumValue(name, 'noconect', -1409)
        self.no_icp = PL1.EnumValue(name, 'no_icp', -1410)
        self.net_no_icp = PL1.EnumValue(name, 'net_no_icp', -1410)
        self.net_not_up = PL1.EnumValue(name, 'net_not_up', -1411)
        self.netnotup = PL1.EnumValue(name, 'netnotup', -1411)
        self.net_rfc_refused = PL1.EnumValue(name, 'net_rfc_refused', -1412)
        self.refused = PL1.EnumValue(name, 'refused', -1412)
        self.netclose = PL1.EnumValue(name, 'netclose', -1413)
        self.net_socket_closed = PL1.EnumValue(name, 'net_socket_closed', -1413)
        self.net_socket_not_found = PL1.EnumValue(name, 'net_socket_not_found', -1414)
        self.netsockf = PL1.EnumValue(name, 'netsockf', -1414)
        self.net_table_space = PL1.EnumValue(name, 'net_table_space', -1415)
        self.nettblsp = PL1.EnumValue(name, 'nettblsp', -1415)
        self.nettime = PL1.EnumValue(name, 'nettime', -1416)
        self.net_timeout = PL1.EnumValue(name, 'net_timeout', -1416)
        self.new_offset_negative = PL1.EnumValue(name, 'new_offset_negative', -1417)
        self.newofneg = PL1.EnumValue(name, 'newofneg', -1417)
        self.new_sl = PL1.EnumValue(name, 'new_sl', -1418)
        self.new_search_list = PL1.EnumValue(name, 'new_search_list', -1418)
        self.newname = PL1.EnumValue(name, 'newname', -1419)
        self.newnamerr = PL1.EnumValue(name, 'newnamerr', -1419)
        self.par9md = PL1.EnumValue(name, 'par9md', -1420)
        self.nine_mode_parity = PL1.EnumValue(name, 'nine_mode_parity', -1420)
        self.no_a = PL1.EnumValue(name, 'no_a', -1421)
        self.no_a_permission = PL1.EnumValue(name, 'no_a_permission', -1421)
        self.no_append = PL1.EnumValue(name, 'no_append', -1422)
        self.noappend = PL1.EnumValue(name, 'noappend', -1422)
        self.noappdev = PL1.EnumValue(name, 'noappdev', -1423)
        self.no_appropriate_device = PL1.EnumValue(name, 'no_appropriate_device', -1423)
        self.noaceql = PL1.EnumValue(name, 'noaceql', -1424)
        self.no_archive_for_equal = PL1.EnumValue(name, 'no_archive_for_equal', -1424)
        self.no_backspace = PL1.EnumValue(name, 'no_backspace', -1425)
        self.nobacksp = PL1.EnumValue(name, 'nobacksp', -1425)
        self.no_base_chnl_active = PL1.EnumValue(name, 'no_base_chnl_active', -1426)
        self.nobaschn = PL1.EnumValue(name, 'nobaschn', -1426)
        self.nochanm = PL1.EnumValue(name, 'nochanm', -1427)
        self.no_channel_meters = PL1.EnumValue(name, 'no_channel_meters', -1427)
        self.no_component = PL1.EnumValue(name, 'no_component', -1428)
        self.no_comp = PL1.EnumValue(name, 'no_comp', -1428)
        self.no_connection = PL1.EnumValue(name, 'no_connection', -1429)
        self.noconect = PL1.EnumValue(name, 'noconect', -1429)
        self.no_cpus_online = PL1.EnumValue(name, 'no_cpus_online', -1430)
        self.nocpus = PL1.EnumValue(name, 'nocpus', -1430)
        self.nocreate = PL1.EnumValue(name, 'nocreate', -1431)
        self.no_create_copy = PL1.EnumValue(name, 'no_create_copy', -1431)
        self.no_current_record = PL1.EnumValue(name, 'no_current_record', -1432)
        self.nocurrec = PL1.EnumValue(name, 'nocurrec', -1432)
        self.no_defs = PL1.EnumValue(name, 'no_defs', -1433)
        self.nolkdefs = PL1.EnumValue(name, 'nolkdefs', -1433)
        self.nodelim = PL1.EnumValue(name, 'nodelim', -1434)
        self.no_delimiter = PL1.EnumValue(name, 'no_delimiter', -1434)
        self.nodevice = PL1.EnumValue(name, 'nodevice', -1435)
        self.no_device = PL1.EnumValue(name, 'no_device', -1435)
        self.no_dialok = PL1.EnumValue(name, 'no_dialok', -1436)
        self.NOTdialok = PL1.EnumValue(name, '^dialok', -1436)
        self.nodir = PL1.EnumValue(name, 'nodir', -1437)
        self.no_dir = PL1.EnumValue(name, 'no_dir', -1437)
        self.noaccess = PL1.EnumValue(name, 'noaccess', -1437)
        self.nodiscpr = PL1.EnumValue(name, 'nodiscpr', -1438)
        self.no_disconnected_processes = PL1.EnumValue(name, 'no_disconnected_processes', -1438)
        self.no_e = PL1.EnumValue(name, 'no_e', -1439)
        self.no_e_permission = PL1.EnumValue(name, 'no_e_permission', -1439)
        self.no_ext_sym = PL1.EnumValue(name, 'no_ext_sym', -1440)
        self.noextsym = PL1.EnumValue(name, 'noextsym', -1440)
        self.no_file = PL1.EnumValue(name, 'no_file', -1441)
        self.nofmflg = PL1.EnumValue(name, 'nofmflg', -1442)
        self.no_fim_flag = PL1.EnumValue(name, 'no_fim_flag', -1442)
        self.nohand = PL1.EnumValue(name, 'nohand', -1443)
        self.no_handler = PL1.EnumValue(name, 'no_handler', -1443)
        self.no_heap_defined = PL1.EnumValue(name, 'no_heap_defined', -1444)
        self.nohpdef = PL1.EnumValue(name, 'nohpdef', -1444)
        self.no_heap_sym = PL1.EnumValue(name, 'no_heap_sym', -1445)
        self.nohpsym = PL1.EnumValue(name, 'nohpsym', -1445)
        self.no_info = PL1.EnumValue(name, 'no_info', -1446)
        self.noinfo = PL1.EnumValue(name, 'noinfo', -1446)
        self.no_istr = PL1.EnumValue(name, 'no_istr', -1447)
        self.no_initial_string = PL1.EnumValue(name, 'no_initial_string', -1447)
        self.noiointr = PL1.EnumValue(name, 'noiointr', -1448)
        self.no_io_interrupt = PL1.EnumValue(name, 'no_io_interrupt', -1448)
        self.no_io_page_tables = PL1.EnumValue(name, 'no_io_page_tables', -1449)
        self.noiopts = PL1.EnumValue(name, 'noiopts', -1449)
        self.no_iocb = PL1.EnumValue(name, 'no_iocb', -1450)
        self.no_journals_free = PL1.EnumValue(name, 'no_journals_free', -1451)
        self.nojrfree = PL1.EnumValue(name, 'nojrfree', -1451)
        self.no_key = PL1.EnumValue(name, 'no_key', -1452)
        self.no_label = PL1.EnumValue(name, 'no_label', -1453)
        self.nolinstt = PL1.EnumValue(name, 'nolinstt', -1454)
        self.no_line_status = PL1.EnumValue(name, 'no_line_status', -1454)
        self.nolksect = PL1.EnumValue(name, 'nolksect', -1455)
        self.no_linkage = PL1.EnumValue(name, 'no_linkage', -1455)
        self.lognomsg = PL1.EnumValue(name, 'lognomsg', -1456)
        self.no_log_message = PL1.EnumValue(name, 'no_log_message', -1456)
        self.no_m = PL1.EnumValue(name, 'no_m', -1457)
        self.no_m_permission = PL1.EnumValue(name, 'no_m_permission', -1457)
        self.nomkknwn = PL1.EnumValue(name, 'nomkknwn', -1458)
        self.no_makeknown = PL1.EnumValue(name, 'no_makeknown', -1458)
        self.nomemsc = PL1.EnumValue(name, 'nomemsc', -1459)
        self.no_memory_for_scavenge = PL1.EnumValue(name, 'no_memory_for_scavenge', -1459)
        self.nomsg = PL1.EnumValue(name, 'nomsg', -1460)
        self.no_message = PL1.EnumValue(name, 'no_message', -1460)
        self.no_move = PL1.EnumValue(name, 'no_move', -1461)
        self.nonxtvol = PL1.EnumValue(name, 'nonxtvol', -1462)
        self.no_next_volume = PL1.EnumValue(name, 'no_next_volume', -1462)
        self.nonullrf = PL1.EnumValue(name, 'nonullrf', -1463)
        self.no_null_refnames = PL1.EnumValue(name, 'no_null_refnames', -1463)
        self.no_odd = PL1.EnumValue(name, 'no_odd', -1464)
        self.no_odd_areas = PL1.EnumValue(name, 'no_odd_areas', -1464)
        self.no_oper = PL1.EnumValue(name, 'no_oper', -1465)
        self.no_operation = PL1.EnumValue(name, 'no_operation', -1465)
        self.no_r_permission = PL1.EnumValue(name, 'no_r_permission', -1466)
        self.no_r = PL1.EnumValue(name, 'no_r', -1466)
        self.no_rec = PL1.EnumValue(name, 'no_rec', -1467)
        self.no_record = PL1.EnumValue(name, 'no_record', -1467)
        self.no_restart = PL1.EnumValue(name, 'no_restart', -1468)
        self.norestrt = PL1.EnumValue(name, 'norestrt', -1468)
        self.nrmdsb = PL1.EnumValue(name, 'nrmdsb', -1469)
        self.no_room_for_dsb = PL1.EnumValue(name, 'no_room_for_dsb', -1469)
        self.no_room_for_lock = PL1.EnumValue(name, 'no_room_for_lock', -1470)
        self.cantlock = PL1.EnumValue(name, 'cantlock', -1470)
        self.no_s_permission = PL1.EnumValue(name, 'no_s_permission', -1471)
        self.no_s = PL1.EnumValue(name, 'no_s', -1471)
        self.no_search_list = PL1.EnumValue(name, 'no_search_list', -1472)
        self.nosrls = PL1.EnumValue(name, 'nosrls', -1472)
        self.no_sldef = PL1.EnumValue(name, 'no_sldef', -1473)
        self.no_search_list_default = PL1.EnumValue(name, 'no_search_list_default', -1473)
        self.nosetbc = PL1.EnumValue(name, 'nosetbc', -1474)
        self.no_set_btcnt = PL1.EnumValue(name, 'no_set_btcnt', -1474)
        self.no_delim = PL1.EnumValue(name, 'no_delim', -1475)
        self.no_stmt_delim = PL1.EnumValue(name, 'no_stmt_delim', -1475)
        self.no_table = PL1.EnumValue(name, 'no_table', -1476)
        self.no_term_type = PL1.EnumValue(name, 'no_term_type', -1477)
        self.notrmtyp = PL1.EnumValue(name, 'notrmtyp', -1477)
        self.no_terminal_quota = PL1.EnumValue(name, 'no_terminal_quota', -1478)
        self.notrmq = PL1.EnumValue(name, 'notrmq', -1478)
        self.no_trap_proc = PL1.EnumValue(name, 'no_trap_proc', -1479)
        self.notrproc = PL1.EnumValue(name, 'notrproc', -1479)
        self.novlasup = PL1.EnumValue(name, 'novlasup', -1480)
        self.no_vla_support = PL1.EnumValue(name, 'no_vla_support', -1480)
        self.no_w = PL1.EnumValue(name, 'no_w', -1481)
        self.no_w_permission = PL1.EnumValue(name, 'no_w_permission', -1481)
        self.no_wdir = PL1.EnumValue(name, 'no_wdir', -1482)
        self.no_wired_structure = PL1.EnumValue(name, 'no_wired_structure', -1483)
        self.nowirebf = PL1.EnumValue(name, 'nowirebf', -1483)
        self.noalloc = PL1.EnumValue(name, 'noalloc', -1484)
        self.noarg = PL1.EnumValue(name, 'noarg', -1485)
        self.nodescr = PL1.EnumValue(name, 'nodescr', -1486)
        self.noentry = PL1.EnumValue(name, 'noentry', -1487)
        self.nolinkag = PL1.EnumValue(name, 'nolinkag', -1488)
        self.nolot = PL1.EnumValue(name, 'nolot', -1489)
        self.nomatch = PL1.EnumValue(name, 'nomatch', -1490)
        self.non_matching_uid = PL1.EnumValue(name, 'non_matching_uid', -1491)
        self.bad_uid = PL1.EnumValue(name, 'bad_uid', -1491)
        self.nonamerr = PL1.EnumValue(name, 'nonamerr', -1492)
        self.noname = PL1.EnumValue(name, 'noname', -1492)
        self.ndirseg = PL1.EnumValue(name, 'ndirseg', -1493)
        self.nondirseg = PL1.EnumValue(name, 'nondirseg', -1493)
        self.nopart = PL1.EnumValue(name, 'nopart', -1494)
        self.noprtdmp = PL1.EnumValue(name, 'noprtdmp', -1495)
        self.nostars = PL1.EnumValue(name, 'nostars', -1496)
        self.not_a_branch = PL1.EnumValue(name, 'not_a_branch', -1497)
        self.notbrnch = PL1.EnumValue(name, 'notbrnch', -1497)
        self.not_a_valid_iocb = PL1.EnumValue(name, 'not_a_valid_iocb', -1498)
        self.badiocb = PL1.EnumValue(name, 'badiocb', -1498)
        self.not_a_wait_channel = PL1.EnumValue(name, 'not_a_wait_channel', -1499)
        self.notwait = PL1.EnumValue(name, 'notwait', -1499)
        self.not_abs_path = PL1.EnumValue(name, 'not_abs_path', -1500)
        self.NOTabspath = PL1.EnumValue(name, '^abspath', -1500)
        self.not_af = PL1.EnumValue(name, 'not_af', -1501)
        self.not_act_fnc = PL1.EnumValue(name, 'not_act_fnc', -1501)
        self.not_archive = PL1.EnumValue(name, 'not_archive', -1502)
        self.not_arch = PL1.EnumValue(name, 'not_arch', -1502)
        self.notattch = PL1.EnumValue(name, 'notattch', -1503)
        self.not_attached = PL1.EnumValue(name, 'not_attached', -1503)
        self.not_base_channel = PL1.EnumValue(name, 'not_base_channel', -1504)
        self.not_base = PL1.EnumValue(name, 'not_base', -1504)
        self.notbound = PL1.EnumValue(name, 'notbound', -1505)
        self.not_bound = PL1.EnumValue(name, 'not_bound', -1505)
        self.not_closed = PL1.EnumValue(name, 'not_closed', -1506)
        self.not_clsd = PL1.EnumValue(name, 'not_clsd', -1506)
        self.not_detached = PL1.EnumValue(name, 'not_detached', -1507)
        self.not_det = PL1.EnumValue(name, 'not_det', -1507)
        self.notdmrg = PL1.EnumValue(name, 'notdmrg', -1508)
        self.not_dm_ring = PL1.EnumValue(name, 'not_dm_ring', -1508)
        self.not_done = PL1.EnumValue(name, 'not_done', -1509)
        self.not_in_trace_table = PL1.EnumValue(name, 'not_in_trace_table', -1510)
        self.notintbl = PL1.EnumValue(name, 'notintbl', -1510)
        self.notinit = PL1.EnumValue(name, 'notinit', -1511)
        self.not_initialized = PL1.EnumValue(name, 'not_initialized', -1511)
        self.NOTlink = PL1.EnumValue(name, '^link', -1512)
        self.not_link = PL1.EnumValue(name, 'not_link', -1512)
        self.not_open = PL1.EnumValue(name, 'not_open', -1513)
        self.NOTownmsg = PL1.EnumValue(name, '^ownmsg', -1514)
        self.not_own_message = PL1.EnumValue(name, 'not_own_message', -1514)
        self.not_priv = PL1.EnumValue(name, 'not_priv', -1515)
        self.not_privileged = PL1.EnumValue(name, 'not_privileged', -1515)
        self.norng0 = PL1.EnumValue(name, 'norng0', -1516)
        self.not_ring_0 = PL1.EnumValue(name, 'not_ring_0', -1516)
        self.notsegt = PL1.EnumValue(name, 'notsegt', -1517)
        self.not_seg_type = PL1.EnumValue(name, 'not_seg_type', -1517)
        self.notadir = PL1.EnumValue(name, 'notadir', -1518)
        self.notalloc = PL1.EnumValue(name, 'notalloc', -1519)
        self.nrmkst = PL1.EnumValue(name, 'nrmkst', -1520)
        self.null_brackets = PL1.EnumValue(name, 'null_brackets', -1521)
        self.nulbrack = PL1.EnumValue(name, 'nulbrack', -1521)
        self.nulldir = PL1.EnumValue(name, 'nulldir', -1522)
        self.null_dir = PL1.EnumValue(name, 'null_dir', -1522)
        self.null_info_ptr = PL1.EnumValue(name, 'null_info_ptr', -1523)
        self.noinfopt = PL1.EnumValue(name, 'noinfopt', -1523)
        self.null_name_component = PL1.EnumValue(name, 'null_name_component', -1524)
        self.nullcomp = PL1.EnumValue(name, 'nullcomp', -1524)
        self.obsolete_function = PL1.EnumValue(name, 'obsolete_function', -1525)
        self.obsfnc = PL1.EnumValue(name, 'obsfnc', -1525)
        self.odd_no_of_args = PL1.EnumValue(name, 'odd_no_of_args', -1526)
        self.odd_arg = PL1.EnumValue(name, 'odd_arg', -1526)
        self.old_dim = PL1.EnumValue(name, 'old_dim', -1527)
        self.oldname = PL1.EnumValue(name, 'oldname', -1528)
        self.oldnamerr = PL1.EnumValue(name, 'oldnamerr', -1528)
        self.oldobj = PL1.EnumValue(name, 'oldobj', -1529)
        self.oob_stack = PL1.EnumValue(name, 'oob_stack', -1530)
        self.oobstk = PL1.EnumValue(name, 'oobstk', -1530)
        self.oobstkrf = PL1.EnumValue(name, 'oobstkrf', -1531)
        self.oob_stack_ref = PL1.EnumValue(name, 'oob_stack_ref', -1531)
        self.oosrv = PL1.EnumValue(name, 'oosrv', -1532)
        self.oosw = PL1.EnumValue(name, 'oosw', -1532)
        self.order_error = PL1.EnumValue(name, 'order_error', -1533)
        self.ordererr = PL1.EnumValue(name, 'ordererr', -1533)
        self.out_of_bounds = PL1.EnumValue(name, 'out_of_bounds', -1534)
        self.oob = PL1.EnumValue(name, 'oob', -1534)
        self.outofmem = PL1.EnumValue(name, 'outofmem', -1535)
        self.out_of_main_memory = PL1.EnumValue(name, 'out_of_main_memory', -1535)
        self.out_of_sequence = PL1.EnumValue(name, 'out_of_sequence', -1536)
        self.outofseq = PL1.EnumValue(name, 'outofseq', -1536)
        self.oowndow = PL1.EnumValue(name, 'oowndow', -1537)
        self.out_of_window = PL1.EnumValue(name, 'out_of_window', -1537)
        self.outward_call_failed = PL1.EnumValue(name, 'outward_call_failed', -1538)
        self.NOToutcall = PL1.EnumValue(name, '^outcall', -1538)
        self.overlapping_more_responses = PL1.EnumValue(name, 'overlapping_more_responses', -1539)
        self.badmore = PL1.EnumValue(name, 'badmore', -1539)
        self.pathlong = PL1.EnumValue(name, 'pathlong', -1540)
        self.picture_bad = PL1.EnumValue(name, 'picture_bad', -1541)
        self.picbad = PL1.EnumValue(name, 'picbad', -1541)
        self.picture_scale = PL1.EnumValue(name, 'picture_scale', -1542)
        self.picscl = PL1.EnumValue(name, 'picscl', -1542)
        self.picbig = PL1.EnumValue(name, 'picbig', -1543)
        self.picture_too_big = PL1.EnumValue(name, 'picture_too_big', -1543)
        self.ponbot = PL1.EnumValue(name, 'ponbot', -1544)
        self.positioned_on_bot = PL1.EnumValue(name, 'positioned_on_bot', -1544)
        self.private_volume = PL1.EnumValue(name, 'private_volume', -1545)
        self.lvprivat = PL1.EnumValue(name, 'lvprivat', -1545)
        self.procstop = PL1.EnumValue(name, 'procstop', -1546)
        self.process_stopped = PL1.EnumValue(name, 'process_stopped', -1546)
        self.process_unknown = PL1.EnumValue(name, 'process_unknown', -1547)
        self.procunkn = PL1.EnumValue(name, 'procunkn', -1547)
        self.proj_not_found = PL1.EnumValue(name, 'proj_not_found', -1548)
        self.no_proj = PL1.EnumValue(name, 'no_proj', -1548)
        self.PV_in_LV = PL1.EnumValue(name, 'PV_in_LV', -1549)
        self.pv_is_in_lv = PL1.EnumValue(name, 'pv_is_in_lv', -1549)
        self.pv_no_scavenge = PL1.EnumValue(name, 'pv_no_scavenge', -1550)
        self.pvnosc = PL1.EnumValue(name, 'pvnosc', -1550)
        self.pvid_not_found = PL1.EnumValue(name, 'pvid_not_found', -1551)
        self.pvntfnd = PL1.EnumValue(name, 'pvntfnd', -1551)
        self.qtabt = PL1.EnumValue(name, 'qtabt', -1552)
        self.quit_term_abort = PL1.EnumValue(name, 'quit_term_abort', -1552)
        self.r0_refname = PL1.EnumValue(name, 'r0_refname', -1553)
        self.r0refnam = PL1.EnumValue(name, 'r0refnam', -1553)
        self.attrNOTpmt = PL1.EnumValue(name, 'attr^pmt', -1554)
        self.rcp_attr_not_permitted = PL1.EnumValue(name, 'rcp_attr_not_permitted', -1554)
        self.rcp_attr_protected = PL1.EnumValue(name, 'rcp_attr_protected', -1555)
        self.prot_att = PL1.EnumValue(name, 'prot_att', -1555)
        self.rcpxatts = PL1.EnumValue(name, 'rcpxatts', -1556)
        self.rcp_bad_attributes = PL1.EnumValue(name, 'rcp_bad_attributes', -1556)
        self.rcprgcmp = PL1.EnumValue(name, 'rcprgcmp', -1557)
        self.rcp_missing_registry_component = PL1.EnumValue(name, 'rcp_missing_registry_component', -1557)
        self.NOTautoreg = PL1.EnumValue(name, '^autoreg', -1558)
        self.rcp_no_auto_reg = PL1.EnumValue(name, 'rcp_no_auto_reg', -1558)
        self.rcp_no_registry = PL1.EnumValue(name, 'rcp_no_registry', -1559)
        self.norgstry = PL1.EnumValue(name, 'norgstry', -1559)
        self.record_busy = PL1.EnumValue(name, 'record_busy', -1560)
        self.recbusy = PL1.EnumValue(name, 'recbusy', -1560)
        self.recoverr = PL1.EnumValue(name, 'recoverr', -1561)
        self.recoverable_error = PL1.EnumValue(name, 'recoverable_error', -1561)
        self.recurerr = PL1.EnumValue(name, 'recurerr', -1562)
        self.recursion_error = PL1.EnumValue(name, 'recursion_error', -1562)
        self.rcnt_big = PL1.EnumValue(name, 'rcnt_big', -1563)
        self.refname_count_too_big = PL1.EnumValue(name, 'refname_count_too_big', -1563)
        self.regexp_invalid_star = PL1.EnumValue(name, 'regexp_invalid_star', -1564)
        self.rgxpinvs = PL1.EnumValue(name, 'rgxpinvs', -1564)
        self.regexp_too_complex = PL1.EnumValue(name, 'regexp_too_complex', -1565)
        self.rgxpcplx = PL1.EnumValue(name, 'rgxpcplx', -1565)
        self.regexp_too_long = PL1.EnumValue(name, 'regexp_too_long', -1566)
        self.rgxplong = PL1.EnumValue(name, 'rgxplong', -1566)
        self.rgxpundf = PL1.EnumValue(name, 'rgxpundf', -1567)
        self.regexp_undefined = PL1.EnumValue(name, 'regexp_undefined', -1567)
        self.rchnact = PL1.EnumValue(name, 'rchnact', -1568)
        self.rel_chnl_active = PL1.EnumValue(name, 'rel_chnl_active', -1568)
        self.reqidamb = PL1.EnumValue(name, 'reqidamb', -1569)
        self.request_id_ambiguous = PL1.EnumValue(name, 'request_id_ambiguous', -1569)
        self.request_not_recognized = PL1.EnumValue(name, 'request_not_recognized', -1570)
        self.reqnorec = PL1.EnumValue(name, 'reqnorec', -1570)
        self.request_pending = PL1.EnumValue(name, 'request_pending', -1571)
        self.reqpend = PL1.EnumValue(name, 'reqpend', -1571)
        self.reservation_failed = PL1.EnumValue(name, 'reservation_failed', -1572)
        self.resbad = PL1.EnumValue(name, 'resbad', -1572)
        self.resource_assigned = PL1.EnumValue(name, 'resource_assigned', -1573)
        self.rassnd = PL1.EnumValue(name, 'rassnd', -1573)
        self.resource_attached = PL1.EnumValue(name, 'resource_attached', -1574)
        self.rattchd = PL1.EnumValue(name, 'rattchd', -1574)
        self.resource_awaiting_clear = PL1.EnumValue(name, 'resource_awaiting_clear', -1575)
        self.rsawclr = PL1.EnumValue(name, 'rsawclr', -1575)
        self.rbadacc = PL1.EnumValue(name, 'rbadacc', -1576)
        self.resource_bad_access = PL1.EnumValue(name, 'resource_bad_access', -1576)
        self.resource_free = PL1.EnumValue(name, 'resource_free', -1577)
        self.rsc_free = PL1.EnumValue(name, 'rsc_free', -1577)
        self.resource_locked = PL1.EnumValue(name, 'resource_locked', -1578)
        self.rsc_lock = PL1.EnumValue(name, 'rsc_lock', -1578)
        self.not_free = PL1.EnumValue(name, 'not_free', -1579)
        self.resource_not_free = PL1.EnumValue(name, 'resource_not_free', -1579)
        self.rscNOTmodf = PL1.EnumValue(name, 'rsc^modf', -1580)
        self.resource_not_modified = PL1.EnumValue(name, 'resource_not_modified', -1580)
        self.rresvd = PL1.EnumValue(name, 'rresvd', -1581)
        self.resource_reserved = PL1.EnumValue(name, 'resource_reserved', -1581)
        self.resource_spec_ambiguous = PL1.EnumValue(name, 'resource_spec_ambiguous', -1582)
        self.rscambig = PL1.EnumValue(name, 'rscambig', -1582)
        self.rcpinapp = PL1.EnumValue(name, 'rcpinapp', -1583)
        self.resource_type_inappropriate = PL1.EnumValue(name, 'resource_type_inappropriate', -1583)
        self.unkrsctp = PL1.EnumValue(name, 'unkrsctp', -1584)
        self.resource_type_unknown = PL1.EnumValue(name, 'resource_type_unknown', -1584)
        self.resource_unassigned = PL1.EnumValue(name, 'resource_unassigned', -1585)
        self.runasnd = PL1.EnumValue(name, 'runasnd', -1585)
        self.runavail = PL1.EnumValue(name, 'runavail', -1586)
        self.resource_unavailable = PL1.EnumValue(name, 'resource_unavailable', -1586)
        self.runknown = PL1.EnumValue(name, 'runknown', -1587)
        self.resource_unknown = PL1.EnumValue(name, 'resource_unknown', -1587)
        self.retrieval_trap_on = PL1.EnumValue(name, 'retrieval_trap_on', -1588)
        self.retrap = PL1.EnumValue(name, 'retrap', -1588)
        self.root = PL1.EnumValue(name, 'root', -1589)
        self.rqover = PL1.EnumValue(name, 'rqover', -1590)
        self.norunrec = PL1.EnumValue(name, 'norunrec', -1591)
        self.run_unit_not_recursive = PL1.EnumValue(name, 'run_unit_not_recursive', -1591)
        self.safety_sw_on = PL1.EnumValue(name, 'safety_sw_on', -1592)
        self.sson = PL1.EnumValue(name, 'sson', -1592)
        self.salv_pdir_procterm = PL1.EnumValue(name, 'salv_pdir_procterm', -1593)
        self.salvptrm = PL1.EnumValue(name, 'salvptrm', -1593)
        self.sameseg = PL1.EnumValue(name, 'sameseg', -1594)
        self.scavenge_aborted = PL1.EnumValue(name, 'scavenge_aborted', -1595)
        self.scabrt = PL1.EnumValue(name, 'scabrt', -1595)
        self.scavenge_in_progress = PL1.EnumValue(name, 'scavenge_in_progress', -1596)
        self.scinprg = PL1.EnumValue(name, 'scinprg', -1596)
        self.scprlmt = PL1.EnumValue(name, 'scprlmt', -1597)
        self.scavenge_process_limit = PL1.EnumValue(name, 'scavenge_process_limit', -1597)
        self.seg_busted = PL1.EnumValue(name, 'seg_busted', -1598)
        self.segbust = PL1.EnumValue(name, 'segbust', -1598)
        self.seg_deleted = PL1.EnumValue(name, 'seg_deleted', -1599)
        self.segdel = PL1.EnumValue(name, 'segdel', -1599)
        self.seg_not_found = PL1.EnumValue(name, 'seg_not_found', -1600)
        self.segntfnd = PL1.EnumValue(name, 'segntfnd', -1600)
        self.notknown = PL1.EnumValue(name, 'notknown', -1601)
        self.seg_unknown = PL1.EnumValue(name, 'seg_unknown', -1601)
        self.segfault = PL1.EnumValue(name, 'segfault', -1602)
        self.segknown = PL1.EnumValue(name, 'segknown', -1603)
        self.seglock = PL1.EnumValue(name, 'seglock', -1604)
        self.segnamdp = PL1.EnumValue(name, 'segnamdp', -1605)
        self.segnamedup = PL1.EnumValue(name, 'segnamedup', -1605)
        self.segno_in_use = PL1.EnumValue(name, 'segno_in_use', -1606)
        self.seginuse = PL1.EnumValue(name, 'seginuse', -1606)
        self.shortrec = PL1.EnumValue(name, 'shortrec', -1607)
        self.short_record = PL1.EnumValue(name, 'short_record', -1607)
        self.signaller_fault = PL1.EnumValue(name, 'signaller_fault', -1608)
        self.sigflt = PL1.EnumValue(name, 'sigflt', -1608)
        self.size_error = PL1.EnumValue(name, 'size_error', -1609)
        self.sizeerr = PL1.EnumValue(name, 'sizeerr', -1609)
        self.smallarg = PL1.EnumValue(name, 'smallarg', -1610)
        self.soos_set = PL1.EnumValue(name, 'soos_set', -1611)
        self.spechan = PL1.EnumValue(name, 'spechan', -1612)
        self.special_channel = PL1.EnumValue(name, 'special_channel', -1612)
        self.chnsfull = PL1.EnumValue(name, 'chnsfull', -1613)
        self.special_channels_full = PL1.EnumValue(name, 'special_channels_full', -1613)
        self.stkinact = PL1.EnumValue(name, 'stkinact', -1614)
        self.stack_not_active = PL1.EnumValue(name, 'stack_not_active', -1614)
        self.stkovrfl = PL1.EnumValue(name, 'stkovrfl', -1615)
        self.stack_overflow = PL1.EnumValue(name, 'stack_overflow', -1615)
        self.strings_not_equal = PL1.EnumValue(name, 'strings_not_equal', -1616)
        self.stringNE = PL1.EnumValue(name, 'string^=', -1616)
        self.subvol_needed = PL1.EnumValue(name, 'subvol_needed', -1617)
        self.subvn = PL1.EnumValue(name, 'subvn', -1617)
        self.subinv = PL1.EnumValue(name, 'subinv', -1618)
        self.subvol_invalid = PL1.EnumValue(name, 'subvol_invalid', -1618)
        self.synch_seg_limit = PL1.EnumValue(name, 'synch_seg_limit', -1619)
        self.synchlim = PL1.EnumValue(name, 'synchlim', -1619)
        self.synch_seg_segmove = PL1.EnumValue(name, 'synch_seg_segmove', -1620)
        self.synchsgm = PL1.EnumValue(name, 'synchsgm', -1620)
        self.tape_error = PL1.EnumValue(name, 'tape_error', -1621)
        self.tape_err = PL1.EnumValue(name, 'tape_err', -1621)
        self.termrqu = PL1.EnumValue(name, 'termrqu', -1622)
        self.termination_requested = PL1.EnumValue(name, 'termination_requested', -1622)
        self.time_too_long = PL1.EnumValue(name, 'time_too_long', -1623)
        self.timelong = PL1.EnumValue(name, 'timelong', -1623)
        self.timeout = PL1.EnumValue(name, 'timeout', -1624)
        self.too_many_acl_entries = PL1.EnumValue(name, 'too_many_acl_entries', -1625)
        self.manyacle = PL1.EnumValue(name, 'manyacle', -1625)
        self.t_m_args = PL1.EnumValue(name, 't_m_args', -1626)
        self.too_many_args = PL1.EnumValue(name, 'too_many_args', -1626)
        self.too_many_buffers = PL1.EnumValue(name, 'too_many_buffers', -1627)
        self.manybufs = PL1.EnumValue(name, 'manybufs', -1627)
        self.too_many_names = PL1.EnumValue(name, 'too_many_names', -1628)
        self.GTnames = PL1.EnumValue(name, '>names', -1628)
        self.tmrdelim = PL1.EnumValue(name, 'tmrdelim', -1629)
        self.too_many_read_delimiters = PL1.EnumValue(name, 'too_many_read_delimiters', -1629)
        self.manyrefs = PL1.EnumValue(name, 'manyrefs', -1630)
        self.too_many_refs = PL1.EnumValue(name, 'too_many_refs', -1630)
        self.toomnysr = PL1.EnumValue(name, 'toomnysr', -1631)
        self.too_many_sr = PL1.EnumValue(name, 'too_many_sr', -1631)
        self.too_many_tokens = PL1.EnumValue(name, 'too_many_tokens', -1632)
        self.numtoken = PL1.EnumValue(name, 'numtoken', -1632)
        self.toomanylinks = PL1.EnumValue(name, 'toomanylinks', -1633)
        self.GTlinks = PL1.EnumValue(name, '>links', -1633)
        self.trace_table_empty = PL1.EnumValue(name, 'trace_table_empty', -1634)
        self.emptytbl = PL1.EnumValue(name, 'emptytbl', -1634)
        self.fulltbl = PL1.EnumValue(name, 'fulltbl', -1635)
        self.trace_table_full = PL1.EnumValue(name, 'trace_table_full', -1635)
        self.tranabor = PL1.EnumValue(name, 'tranabor', -1636)
        self.translation_aborted = PL1.EnumValue(name, 'translation_aborted', -1636)
        self.translation_failed = PL1.EnumValue(name, 'translation_failed', -1637)
        self.tranfail = PL1.EnumValue(name, 'tranfail', -1637)
        self.typenfnd = PL1.EnumValue(name, 'typenfnd', -1638)
        self.typename_not_found = PL1.EnumValue(name, 'typename_not_found', -1638)
        self.unable_to_check_access = PL1.EnumValue(name, 'unable_to_check_access', -1639)
        self.cantchk = PL1.EnumValue(name, 'cantchk', -1639)
        self.no_io = PL1.EnumValue(name, 'no_io', -1640)
        self.unable_to_do_io = PL1.EnumValue(name, 'unable_to_do_io', -1640)
        self.unbalbra = PL1.EnumValue(name, 'unbalbra', -1641)
        self.unbalanced_brackets = PL1.EnumValue(name, 'unbalanced_brackets', -1641)
        self.unbalpar = PL1.EnumValue(name, 'unbalpar', -1642)
        self.unbalanced_parentheses = PL1.EnumValue(name, 'unbalanced_parentheses', -1642)
        self.unbalanced_quotes = PL1.EnumValue(name, 'unbalanced_quotes', -1643)
        self.unbalquo = PL1.EnumValue(name, 'unbalquo', -1643)
        self.undefmod = PL1.EnumValue(name, 'undefmod', -1644)
        self.undefined_mode = PL1.EnumValue(name, 'undefined_mode', -1644)
        self.undefined_order_request = PL1.EnumValue(name, 'undefined_order_request', -1645)
        self.undorder = PL1.EnumValue(name, 'undorder', -1645)
        self.undptnam = PL1.EnumValue(name, 'undptnam', -1646)
        self.undefined_ptrname = PL1.EnumValue(name, 'undefined_ptrname', -1646)
        self.undeldev = PL1.EnumValue(name, 'undeldev', -1647)
        self.undeleted_device = PL1.EnumValue(name, 'undeleted_device', -1647)
        self.exexpcon = PL1.EnumValue(name, 'exexpcon', -1648)
        self.unexpected_condition = PL1.EnumValue(name, 'unexpected_condition', -1648)
        self.unxpstat = PL1.EnumValue(name, 'unxpstat', -1649)
        self.unexpected_device_status = PL1.EnumValue(name, 'unexpected_device_status', -1649)
        self.unexpected_ft2 = PL1.EnumValue(name, 'unexpected_ft2', -1650)
        self.unexpft2 = PL1.EnumValue(name, 'unexpft2', -1650)
        self.unexpfl = PL1.EnumValue(name, 'unexpfl', -1651)
        self.unexpired_file = PL1.EnumValue(name, 'unexpired_file', -1651)
        self.unexpired_volume = PL1.EnumValue(name, 'unexpired_volume', -1652)
        self.unexpvl = PL1.EnumValue(name, 'unexpvl', -1652)
        self.unimptnm = PL1.EnumValue(name, 'unimptnm', -1653)
        self.unimplemented_ptrname = PL1.EnumValue(name, 'unimplemented_ptrname', -1653)
        self.unimplemented_version = PL1.EnumValue(name, 'unimplemented_version', -1654)
        self.not_imp = PL1.EnumValue(name, 'not_imp', -1654)
        self.uninitialized_volume = PL1.EnumValue(name, 'uninitialized_volume', -1655)
        self.uninitvl = PL1.EnumValue(name, 'uninitvl', -1655)
        self.unknown_tp = PL1.EnumValue(name, 'unknown_tp', -1656)
        self.bad_tp = PL1.EnumValue(name, 'bad_tp', -1656)
        self.unknown_zone = PL1.EnumValue(name, 'unknown_zone', -1657)
        self.bad_zone = PL1.EnumValue(name, 'bad_zone', -1657)
        self.unrecognized_char_code = PL1.EnumValue(name, 'unrecognized_char_code', -1658)
        self.urecgcc = PL1.EnumValue(name, 'urecgcc', -1658)
        self.unregvol = PL1.EnumValue(name, 'unregvol', -1659)
        self.unregistered_volume = PL1.EnumValue(name, 'unregistered_volume', -1659)
        self.unsupported_multi_class_volume = PL1.EnumValue(name, 'unsupported_multi_class_volume', -1660)
        self.unsupvol = PL1.EnumValue(name, 'unsupvol', -1660)
        self.unsupop = PL1.EnumValue(name, 'unsupop', -1661)
        self.unsupported_operation = PL1.EnumValue(name, 'unsupported_operation', -1661)
        self.bad_term = PL1.EnumValue(name, 'bad_term', -1662)
        self.unsupported_terminal = PL1.EnumValue(name, 'unsupported_terminal', -1662)
        self.user_not_found = PL1.EnumValue(name, 'user_not_found', -1663)
        self.usernfd = PL1.EnumValue(name, 'usernfd', -1663)
        self.user_requested_logout = PL1.EnumValue(name, 'user_requested_logout', -1664)
        self.userlogo = PL1.EnumValue(name, 'userlogo', -1664)
        self.user_requested_hangup = PL1.EnumValue(name, 'user_requested_hangup', -1665)
        self.userhngp = PL1.EnumValue(name, 'userhngp', -1665)
        self.vchn_active = PL1.EnumValue(name, 'vchn_active', -1666)
        self.vchnact = PL1.EnumValue(name, 'vchnact', -1666)
        self.vchnnfnd = PL1.EnumValue(name, 'vchnnfnd', -1667)
        self.vchn_not_found = PL1.EnumValue(name, 'vchn_not_found', -1667)
        self.vol_in_use = PL1.EnumValue(name, 'vol_in_use', -1668)
        self.volinuse = PL1.EnumValue(name, 'volinuse', -1668)
        self.volbusy = PL1.EnumValue(name, 'volbusy', -1669)
        self.volume_busy = PL1.EnumValue(name, 'volume_busy', -1669)
        self.volume_not_loaded = PL1.EnumValue(name, 'volume_not_loaded', -1670)
        self.volntld = PL1.EnumValue(name, 'volntld', -1670)
        self.vtNOTknown = PL1.EnumValue(name, 'vt^known', -1671)
        self.volume_type_unknown = PL1.EnumValue(name, 'volume_type_unknown', -1671)
        self.vtoc_io_err = PL1.EnumValue(name, 'vtoc_io_err', -1672)
        self.vtocioer = PL1.EnumValue(name, 'vtocioer', -1672)
        self.vtocecnf = PL1.EnumValue(name, 'vtocecnf', -1673)
        self.vtoce_connection_fail = PL1.EnumValue(name, 'vtoce_connection_fail', -1673)
        self.vtocefr = PL1.EnumValue(name, 'vtocefr', -1674)
        self.vtoce_free = PL1.EnumValue(name, 'vtoce_free', -1674)
        self.wakeup_denied = PL1.EnumValue(name, 'wakeup_denied', -1675)
        self.nowakeup = PL1.EnumValue(name, 'nowakeup', -1675)
        self.wrong_channel_ring = PL1.EnumValue(name, 'wrong_channel_ring', -1676)
        self.wrchring = PL1.EnumValue(name, 'wrchring', -1676)
        self.badargno = PL1.EnumValue(name, 'badargno', -1677)
        self.wrong_no_of_args = PL1.EnumValue(name, 'wrong_no_of_args', -1677)
        self.zerosegl = PL1.EnumValue(name, 'zerosegl', -1678)
        self.zero_length_seg = PL1.EnumValue(name, 'zero_length_seg', -1678)
        self.no_forms_table_defined = PL1.EnumValue(name, 'no_forms_table_defined', -1679)
        self.notabdef = PL1.EnumValue(name, 'notabdef', -1679)
        self.badfrmop = PL1.EnumValue(name, 'badfrmop', -1680)
        self.bad_forms_option = PL1.EnumValue(name, 'bad_forms_option', -1680)
