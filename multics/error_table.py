
from pl1types import PL1
class ErrorTable(PL1.Enum):
    def __init__(self, name):
        PL1.Enum.__init__(self, name)
        self._messages = \
{   -678: 'Undefined forms option.',
    -677: 'No forms table defined for this request_type or device.',
    -676: 'Zero length segment.',
    -675: 'Wrong number of arguments supplied.',
    -674: 'An event channel is being used in an incorrect ring.',
    -673: 'Insufficient access to send wakeup.',
    -672: 'The VTOCE is already free.',
    -671: 'Some directory or segment in the pathname is not listed in the VTOC.',
    -670: 'Unrecoverable data-transmission error on VTOC.',
    -669: 'Volume type unknown to the system.',
    -668: 'The requested volume is not loaded.',
    -667: 'The requested volume is not available.',
    -666: 'The volume is in use by another process.',
    -665: 'virtual channel not defined.',
    -664: 'virtual channel is currently in use.',
    -663: 'The user requested the connection to close.',
    -662: 'The user voluntarily logged out.',
    -661: 'User-name not on access control list for branch.',
    -660: 'The specified terminal is not supported by the video system.',
    -659: 'The requested operation is not supported.',
    -658: 'Multi-class volumes are not supported.',
    -657: 'The specified detachable volume has not been registered.',
    -656: 'Volume recorded in unrecognized character code.',
    -655: 'The time zone is not acceptable.',
    -654: 'The specified tuning parameter does not exist.',
    -653: 'Unable to continue processing on uninitialized volume.',
    -652: 'This procedure does not implement the requested version.',
    -651: 'Pointer name passed to seek or tell not currently implemented by it.',
    -650: 'Unable to continue processing on unexpired volume.',
    -649: 'Unable to overwrite an unexpired file.',
    -648: 'Attempt to execute instruction containing a fault tag 2.',
    -647: 'Unexpected or inexplicable status received from device.',
    -646: 'An unexpected condition was signalled during the operation.',
    -645: 'Cannot delete the only channel leading to an undeleted device.',
    -644: 'Unrecognizable ptrname on seek or tell call.',
    -643: 'Undefined order request.',
    -642: 'Mode not defined.',
    -641: 'Quotes do not balance.',
    -640: 'Parentheses do not balance.',
    -639: 'Brackets do not balance.',
    -638: 'Unable to perform critical I/O.',
    -637: 'It was not possible to complete access checking - access denied.',
    -636: 'Typename not found.',
    -635: 'Translation failed.',
    -634: 'Fatal error.  Translation aborted.',
    -633: 'Trace table is full.',
    -632: 'Trace table is empty.',
    -631: 'There are too many links to get to a branch.',
    -630: 'The string contains more tokens than can be processed.',
    -629: 'Too many search rules.',
    -628: 'Unable to increment the reference count because of upper bound limit.',
    -627: 'Too many read delimiters specified.',
    -626: 'Name list exceeds maximum size.',
    -625: 'Too many buffers specified.',
    -624: 'Maximum number of arguments for this command exceeded.',
    -623: 'Access control list exceeds maximum size.',
    -622: 'The operation was not completed within the required time.',
    -621: 'Specified time limit is too long.',
    -620: 'Process terminated because of system defined error condition.',
    -619: 'Tape error.',
    -618: 'Attempt to segment move synchronized segment with held pages.',
    -617: 'Too many synchronized segments are active.',
    -616: 'Subvolume is invalid for this device.',
    -615: 'Subvolume needed for this type device.',
    -614: 'Strings are not equal.',
    -613: 'Not enough room in stack to complete processing.',
    -612: 'The requested ring-0 stack is not active.',
    -611: 'All available special channels have been allocated.',
    -610: 'The event channel specified is a special channel.',
    -609: 'Security-out-of-service has been set on some branches due to AIM inconsistency.',
    -608: 'Argument size too small.',
    -607: 'The size condition has occurred.',
    -606: "Fault in signaller by user's process.",
    -605: 'Record is too short.',
    -604: 'The segment number is in use.',
    -603: 'Name already on entry.',
    -602: 'The segment is already locked.',
    -601: 'Segment already known to process.',
    -600: 'Segment fault occurred accessing segment.',
    -599: 'Segment not known to process.',
    -598: 'Segment not found.',
    -597: 'The segment has been deleted.',
    -596: 'Maximum number of simultaneous scavenges exceeded.',
    -595: 'The volume is being scavenged.',
    -594: 'The volume scavenge has been terminated abnormally.',
    -593: 'Attempt to specify the same segment as both old and new.',
    -592: 'Fatal salvaging of process directory.',
    -591: 'Attempt to delete segment whose safety switch is on.',
    -590: 'There can be only one run unit at a time.',
    -589: 'Record quota overflow.',
    -588: 'The directory is the ROOT.',
    -587: 'Retrieval trap on for file special user is trying to access.',
    -586: 'Resource not known to the system.',
    -585: 'No appropriate resource available.',
    -584: 'Resource not assigned to requesting process.',
    -583: 'Resource type unknown to the system.',
    -582: 'Resource type is inappropriate for this request.',
    -581: 'Resource specification supplied is incomplete.',
    -580: 'The resource is otherwise reserved.',
    -579: 'Specified resource property may not be modified in this manner.',
    -578: 'The resource is not free.',
    -577: 'The resource is locked.',
    -576: 'This operation not allowed for a free resource.',
    -575: 'Resource not accessible to the requesting process.',
    -574: 'Resource is awaiting clear.',
    -573: 'Resource already attached to the requesting process.',
    -572: 'Resource already assigned to requesting process.',
    -571: 'The resource reservation request has failed.',
    -570: 'Processing of request has not been completed.',
    -569: 'Request not recognized.',
    -568: 'The specified request id matches multiple requests.',
    -567: 'Cannot delete a base channel with related logical channels still active.',
    -566: 'Regular expression // is undefined.',
    -565: 'Regular expression is too long.',
    -564: 'Regular expression is too complex.',
    -563: 'Invalid use of * in regular expression.',
    -562: 'The reference name count is greater than the number of reference names.',
    -561: 'Infinite recursion.',
    -560: 'Requested operation completed but non-fatal errors or inconsistencies were encountered.',
    -559: 'Record locked by another process.',
    -558: 'The registry was not found.',
    -557: 'The resource cannot be automatically registered.',
    -556: 'Missing rcp registry component.',
    -555: 'Resource attribute specification is invalid.',
    -554: 'Some attribute specified is protected.',
    -553: 'Some attribute specified is not permitted for this resource.',
    -552: 'Attempt to use reference names in ring 0.',
    -551: 'Aborted by quit or term.',
    -550: 'The physical volume is not mounted.',
    -549: 'The physical volume cannot be scavenged.',
    -548: 'The physical volume is already in the logical volume.',
    -547: 'Specified project not found.',
    -546: 'Target process unknown or in deactivated state.',
    -545: 'Target process in stopped state.',
    -544: 'The logical volume is private.',
    -543: 'Tape positioned on leader.',
    -542: 'The normalized picture exceeds 64 characters.',
    -541: 'The picture scale factor not in the range -128:+127.',
    -540: 'The picture contains a syntax error.',
    -539: 'Pathname too long.',
    -538: 'The yes and no response characters are not distinct.',
    -537: 'Error making outward call after stack history destroyed.',
    -536: 'The point or region specified lies outside the window.',
    -535: 'A call that must be in a sequence of calls was out of sequence.',
    -534: 'There is insufficient memory to wire the requested I/O buffer.',
    -533: 'Reference is outside allowable bounds.',
    -532: 'An error occurred while processing the order request.',
    -531: 'There was an attempt to reference a directory which is out of service.',
    -530: 'Attempt to reference beyond end of stack.',
    -529: 'User stack space exhausted.',
    -528: 'Obsolete object segment format.',
    -527: 'Name not found.',
    -526: 'Old DIM cannot accept new I/O call.',
    -525: 'Odd number of arguments.',
    -524: 'Attempt to perform an operation which is obsolete.',
    -523: 'The name contains a null component.',
    -522: 'Pointer to required information is null.',
    -521: 'The directory specified has no branches.',
    -520: 'Null bracket set encountered.',
    -519: 'There is no more room in the KST.',
    -518: 'Allocation could not be performed.',
    -517: 'Entry is not a directory.',
    -516: 'Segment not of type specified.',
    -515: 'Signaller called while not in ring 0.',
    -514: 'This operation requires privileged access not given to this process.',
    -513: 'The specified message was not added by this user.',
    -512: 'I/O switch is not open.',
    -511: 'This operation may only be performed on a link entry.',
    -510: 'Initialization has not been performed.',
    -509: 'Entry not found in trace table.',
    -508: 'Not processed.',
    -507: 'The validation level is higher than the Data Management ring.',
    -506: 'I/O switch is not detached.',
    -505: 'I/O switch is not closed.',
    -504: 'Segment is not bound.',
    -503: 'Specified channel is not a base channel.',
    -502: 'I/O switch (or device) is not attached.',
    -501: 'Segment is not an archive.',
    -500: 'This active function cannot be invoked as a command.',
    -499: 'Pathname supplied is not an absolute pathname.',
    -498: 'Event channel is not a wait channel.',
    -497: 'The supplied pointer does not point to a valid IOCB.',
    -496: 'Entry is not a branch.',
    -495: 'Star convention is not allowed.',
    -494: 'No part dump card in config deck.',
    -493: 'The partition was not found.',
    -492: 'This operation is not allowed for a segment.',
    -491: 'The operation would leave no names on entry.',
    -490: 'Unique id of segment does not match unique id argument.',
    -489: 'Use of star convention resulted in no match.',
    -488: 'No linkage offset table in this ring.',
    -487: 'No/bad linkage info in the lot for this segment.',
    -486: 'Entry not found.',
    -485: 'Expected argument descriptor missing.',
    -484: 'Expected argument missing.',
    -483: 'There is no room to make requested allocations.',
    -482: 'No wired structure could be allocated for this device request.',
    -481: 'No working directory set for this process.',
    -480: 'No write permission on entry.',
    -479: 'The system does not currently support very large array common.',
    -478: 'Cannot find procedure to call link trap procedure.',
    -477: 'An upgraded directory must have terminal quota.',
    -476: 'Unknown terminal type.',
    -475: 'The specified table does not exist.',
    -474: 'A statement delimiter is missing.',
    -473: 'Unable to set the bit count on the copy.',
    -472: 'Search list has no default.',
    -471: 'Search list is not in search segment.',
    -470: 'Status permission missing on directory containing entry.',
    -469: 'The record block is too small to contain a lock.',
    -468: 'No room available for device status block.',
    -467: 'Supplied machine conditions are not restartable.',
    -466: 'Record not located.',
    -465: 'No read permission on entry.',
    -464: 'Invalid I/O operation.',
    -463: 'An area may not begin at an odd address.',
    -462: 'The segment was not initiated with any null reference names.',
    -461: 'Unable to continue processing on next volume.',
    -460: 'Unable to move segment because of type, access or quota.',
    -459: 'Message not found.',
    -458: 'Insufficient memory for volume scavenge.',
    -457: 'Unable to make original segment known.',
    -456: 'Modify permission missing on entry.',
    -455: 'The requested log message cannot be located.',
    -454: 'Linkage section not found.',
    -453: 'No line_status information available.',
    -452: 'Specified detachable volume has no label.',
    -451: 'No key defined for this operation.',
    -450: 'There are no free Data Management journals indices.',
    -449: 'No I/O switch.',
    -448: 'Unable to allocate an I/O page table.',
    -447: 'No interrupt was received on the designated IO channel.',
    -446: 'No initial string defined for terminal type.',
    -445: 'Insufficient access to return any information.',
    -444: 'Heap symbol not found.',
    -443: 'The heap has not been defined at this execution level.',
    -442: 'No unclaimed signal handler specified for this process.',
    -441: 'The FIM flag was not set in the preceding stack frame.',
    -440: 'File does not exist.',
    -439: 'External symbol not found.',
    -438: 'No execute permission on entry.',
    -437: 'You have no disconnected processes.',
    -436: 'Some directory in path specified does not exist.',
    -435: 'The process does not have permission to make dial requests.',
    -434: 'No device currently available for attachment.',
    -433: 'No delimiters found in segment to be sorted.',
    -432: 'Bad definitions pointer in linkage.',
    -431: 'There is no current record.',
    -430: 'Unable to create a copy.',
    -429: 'The requested group of CPUs contains none which are online.',
    -428: 'Unable to complete connection to external device.',
    -427: 'Component not found in archive.',
    -426: 'No meters available for the specified channel.',
    -425: 'Cannot add channel with its associated base channel inactive.',
    -424: 'Requested tape backspace unsuccessful.',
    -423: 'No archive name in original pathname corresponding to equal name.',
    -422: 'No appropriate device is available.',
    -421: 'Append permission missing.',
    -420: 'Append permission missing on directory.',
    -419: 'Attempt to write invalid data in 9 mode.',
    -418: 'User name to be added to acl not acceptable to storage system.',
    -417: 'A new search list was created.',
    -416: 'New offset for pointer computed by seek entry is negative.',
    -415: 'Connection not completed within specified time interval.',
    -414: 'The NCP could not find a free table entry for this request.',
    -413: 'Specified socket not found in network data base.',
    -412: 'Network connection closed by foreign host.',
    -411: 'Request for connection refused by foreign host.',
    -410: 'Network Control Program not in operation.',
    -409: 'There is no initial connection in progress from this socket.',
    -408: 'Process lacks permission to initiate Network connections.',
    -407: 'Request is inconsistent with state of socket.',
    -406: 'The initial connection has not yet been completed.',
    -405: 'A logical error has occurred in initial connection.',
    -404: 'Initial connection socket is in an improper state.',
    -403: 'Foreign IMP is down.',
    -402: 'Communications with this foreign host not enabled.',
    -401: 'Foreign host is down.',
    -400: 'Bad socket gender involved in this request.',
    -399: 'An initial connection is already in progress from this socket.',
    -398: 'Negative offset supplied to data transmission entry.',
    -397: 'Negative number of elements supplied to data transmission entry.',
    -396: 'Network Control Program encountered a software error.',
    -395: 'Name duplication.',
    -394: 'The name was not found.',
    -393: 'There was an attempt to lock a directory already locked to this process.',
    -392: 'The stream is attached to more than one device.',
    -391: 'This operation is not allowed for a multisegment file.',
    -390: 'The multiplexer is not running.',
    -389: 'Mount request pending.',
    -388: 'Requested volume not yet mounted.',
    -387: 'Incorrect access on entry.',
    -386: 'Mode string has been truncated.',
    -385: 'Missing entry in outer module.',
    -384: 'Mismatched iteration sets.',
    -383: 'Messages are not being accepted.',
    -382: 'Messages are deferred.',
    -381: 'The specified volume cannot be unloaded from its device.',
    -380: 'Master directory missing from MDCS.',
    -379: 'One or more of the paths given are in error.',
    -378: 'Path violates volume or account pathname restriction.',
    -377: 'Pathname not found.',
    -376: 'Pathname appears more than once in the list.',
    -375: 'Pathname already listed.',
    -374: 'This operation allowed only on master directories.',
    -373: 'No quota account for the logical volume.',
    -372: 'Insufficient quota on logical volume.',
    -371: 'Specified quota account not found.',
    -370: 'Volume cannot be deleted because it contains master directories.',
    -369: 'Quota account has master directories charged against it.',
    -368: 'Illegal format of master directory owner name.',
    -367: 'Illegal format of quota account name.',
    -366: 'Executive access to logical volume required to perform operation.',
    -365: 'Master directory quota must be greater than 0.',
    -364: 'Reply permission missing on message coordinator source.',
    -363: 'Quit permission missing on message coordinator source.',
    -362: 'Daemon permission missing on message coordinator source.',
    -361: 'Control permission missing on message coordinator source.',
    -360: 'The maximum depth in the storage system hierarchy has been exceeded.',
    -359: 'This operation is not allowed for a master directory.',
    -358: 'The channel is masked.',
    -357: 'A compiler has generated incorrect list template initialization for an array or external variable.',
    -356: 'Validation level not in ring bracket.',
    -355: 'The sequential position on the device is unknown.',
    -354: 'Equals convention makes entry name too long.',
    -353: 'Record is too long.',
    -352: 'The logical volume table is full.',
    -351: 'The logical volume is not mounted.',
    -350: 'The logical volume is not attached.',
    -349: 'The logical volume is already mounted.',
    -348: 'The logical volume is already attached.',
    -347: 'No more listener entries are cuurrently available for this log.',
    -346: 'The logical volume is full.',
    -345: 'The log segment has not yet been initialized.',
    -344: 'The specified segment is not a valid log segment.',
    -343: 'The log segment is full.',
    -342: 'The log segment is empty.',
    -341: 'The log segment is damaged.',
    -340: 'The specified log segment is not in service at this time.',
    -339: 'The specified log message type is invalid.',
    -338: 'The lock was already locked by this process.',
    -337: 'Attempt to unlock a lock which was locked by another process.',
    -336: 'The lock could not be set in the given time.',
    -335: 'Attempt to unlock a lock that was not locked.',
    -334: 'The lock does not belong to an existing process.',
    -333: 'The listen operation has been aborted by a stop_listen request.',
    -332: 'The execute access is needed to directory containing the link.',
    -331: 'This operation is not allowed for a link entry.',
    -330: 'Operation not performed because of outstanding line_status information.',
    -329: 'This operation would cause a reference count to vanish.',
    -328: 'There was an attempt to terminate a segment which was known in other rings.',
    -327: 'Key out of order.',
    -326: 'There is already a record with the same key.',
    -325: 'Not enough room in ITT for wakeup.',
    -324: 'The item specified is over the legal size.',
    -323: 'An interprocess signal has occurred.',
    -322: 'Ioname already attached and active.',
    -321: 'Ioname not found.',
    -320: 'Ioname not active.',
    -319: 'The IOM has its number set incorrectly.',
    -318: 'The IOM has its mailbox address switches set incorrectly.',
    -317: 'A connect to an IOM has left main memory in an unusable state.',
    -316: 'IOM is already deleted.',
    -315: 'IOM is already active.',
    -314: 'Error in internal ioat information.',
    -313: 'IO device failed to become unassigned.',
    -312: 'Specified IO resource not defined in configuration.',
    -311: 'Specified IO resource not configured.',
    -310: 'Specified IO resource is is use by another process.',
    -309: 'Specified IO resource not assigned.',
    -308: 'Process lacks permission to alter device status.',
    -307: 'There is no available path to the specified IO resource.',
    -306: 'Specified IO resource already configured.',
    -305: 'Specified IO resource already assigned.',
    -304: 'There was an attempt to use an invalid segment number.',
    -303: 'Attempt to write or move write pointer on device which was not attached as writeable.',
    -302: 'The VTOCE index specified is not within the range of valid indices for the device.',
    -301: 'There was an attempt to use a VTOCE with invalid fields.',
    -300: 'Specified volumes do not comprise a valid volume set.',
    -299: 'The supplied value is not acceptable for this tuning parameter.',
    -298: 'The record length is not an integral number of words.',
    -297: 'The specified system type does not exist.',
    -296: 'The specified subsystem either does not exist or is inconsistent.',
    -295: 'Request is inconsistent with current state of device.',
    -294: 'Attempt to create a stack which exists or which is known to process.',
    -293: 'Attempt to set delimiters for device while element size is too large to support search.',
    -292: 'Attempt to manipulate last or bound pointers for device that was not attached as writeable.',
    -291: 'The ring brackets specified are invalid.',
    -290: 'The request is inconsistent with the current state of the resource(s).',
    -289: 'Invalid logical record length.',
    -288: 'Invalid variable-length record descriptor.',
    -287: 'Attempt to read or move read pointer on device which was not attached as readable.',
    -286: 'Invalid Physical Volume Table Entry index specified.',
    -285: 'Unable to initialize a pointer used as the initial value of an external variable.',
    -284: 'Invalid project for gate access control list.',
    -283: 'Undefined preaccess command.',
    -282: 'Invalid multiplexer type specified.',
    -281: 'Invalid move of quota would change terminal quota to non terminal.',
    -280: 'Attempt to move more than maximum amount of quota.',
    -279: 'Invalid mode specified for ACL.',
    -278: 'Attempt to set max length of a segment less than its current length.',
    -277: 'The lock was locked by a process that no longer exists.  Therefore the lock was reset.',
    -276: 'Line type number exceeds maximum permitted value.',
    -275: 'File set contains invalid labels.',
    -274: 'An invalid size has been found for a heap variable.',
    -273: 'An invalid heap header has been found.  This is likely due to the stack being overwritten.',
    -272: 'File set structure is invalid.',
    -271: 'File expiration date exceeds that of previous file.',
    -270: 'Invalid element size.',
    -269: 'Invalid data management journal index.',
    -268: 'Attempt to attach to an invalid device.',
    -267: 'Invalid delay value specified.',
    -266: 'Internal inconsistency in control segment.',
    -265: 'There was an attempt to create a copy without correct access.',
    -264: 'The event channel specified is not a valid channel.',
    -263: 'Invalid physical block length.',
    -262: 'Invalid backspace_read order call.',
    -261: 'The name specified contains non-ascii characters.',
    -260: 'The size of an array passed as an argument is invalid.',
    -259: 'Insufficient information to open file.',
    -258: 'Process lacks sufficient access to perform this operation.',
    -257: 'There was an attempt to make a directory unknown that has inferior segments.',
    -256: 'Volume type is inappropriate for this request.',
    -255: 'Device type is inappropriate for this request.',
    -254: 'Incorrect access to directory containing entry.',
    -253: 'Object MSF is inconsistent.',
    -252: 'Active Segment Table threads in the SST are inconsistent.',
    -251: 'The reference name table is in an inconsistent state.',
    -250: 'Multisegment file is inconsistent.',
    -249: 'The event channel table was in an inconsistent state.',
    -248: 'Inconsistent combination of control arguments.',
    -247: 'Missing components in access name.',
    -246: 'The specified terminal type is incompatible with the line type.',
    -245: 'Specified attribute incompatible with file structure.',
    -244: 'Incompatible character encoding mode.',
    -243: 'Attach and open are incompatible.',
    -242: 'An improper attempt was made to terminate the process.',
    -241: 'Data not in expected format.',
    -240: 'A RFNM is pending on this IMP link.',
    -239: 'Multics IMP is down.',
    -238: 'Bad status received from IMP.',
    -237: 'Format of IMP message was incorrect.',
    -236: 'Record size must be positive and smaller than a segment',
    -235: 'Attempt to indirect through word pair containing a fault tag 2 in the odd word.',
    -234: 'There was an illegal attempt to delete an AST entry.',
    -233: 'There was an illegal attempt to activate a segment.',
    -232: 'Supplied identifier not found in data base.',
    -231: 'Supplied identifier already exists in data base.',
    -230: 'The lock was set on behalf of an operation which must be adjusted.',
    -229: 'Attempt to perform an illegal action on a hardcore segment.',
    -228: 'There was an attempt to delete a non-empty directory.',
    -227: 'The directory hash table is full.',
    -226: 'PVT index out of range.',
    -225: 'Physical device error.',
    -224: 'Unsupported VTOC header version.',
    -223: 'Unsupported label version.',
    -222: 'Not a storage system drive.',
    -221: 'Volume not salvaged.',
    -220: 'Drive not ready.',
    -219: 'Drive in use already.',
    -218: 'Invalid storage system volume label.',
    -217: 'Attempt to reference temporary storage outside the scope of this frame.',
    -216: 'The Operator refused to honor the mount request.',
    -215: 'The FNP is not running.',
    -214: 'A first reference trap was found on the link target segment.',
    -213: "Illegal procedure fault in FIM by user's process.",
    -212: 'No file is open under this reference name.',
    -211: 'There is no more room in the file.',
    -210: 'File already busy for other I/O activity.',
    -209: 'File is already opened.',
    -208: 'Defective file section deleted from file set.',
    -207: 'A fatal error has occurred.',
    -206: 'Event channels not in cutoff state.',
    -205: 'Event channels in cutoff state.',
    -204: 'Event calls are not in masked state.',
    -203: 'Encountered end-of-volume on write.',
    -202: 'End-of-file record encountered.',
    -201: 'Entry name too long.',
    -200: 'End of information reached.',
    -199: 'Search list is empty.',
    -198: 'File is empty.',
    -197: 'Archive is empty.',
    -196: 'ACL is empty.',
    -195: 'A pointer that must be eight word aligned was not so aligned.',
    -194: 'The event channel table was full.',
    -193: 'The event channel table has already been initialized.',
    -192: 'Echo negotiation race occurred.  Report this as a bug.',
    -191: 'A duplicate request was encountered.',
    -190: 'File identifier already appears in file set.',
    -189: 'Duplicate entry name in bound segment.',
    -188: 'In the specified time zone, the clock value is before the year 0001.',
    -187: 'In the specified time zone, the clock value is after the year 9999.',
    -186: 'An unknown word was found in the time string.',
    -185: 'The language given is not known to the system.',
    -184: 'An error has been found while converting a time string.',
    -183: 'The size condition occurred while converting the time string.',
    -182: 'Applying an offset gives a date after 9999-12-31 GMT.',
    -181: 'Applying an offset gives a date before 0001-01-01 GMT.',
    -180: 'No units were given in which to express the interval.',
    -179: 'The format string contains no selectors.',
    -178: 'A time zone value has been given more than once.',
    -177: 'A time value has been given more than once.',
    -176: 'The time string does not have the same meaning in all languages.',
    -175: 'A day of the week value has been given more than once.',
    -174: 'A date value has been given more than once.',
    -173: 'The hour value exceeds 12.',
    -172: 'The date is before 0001-01-01 GMT.',
    -171: 'The date is after 9999-12-31 GMT.',
    -170: 'The time period 1582-10-05 through 1582-10-14 does not exist.',
    -169: 'There is a conflict in the day specifications.',
    -168: 'The month number is invalid.',
    -167: 'The fiscal week number is invalid.',
    -166: 'The format string contains a selector which is not defined.',
    -165: 'The day of the year is invalid.',
    -164: 'The day of the month is invalid.',
    -163: 'The date given is not on the indicated day of the week.',
    -162: 'All words in a time string must be in the same language.',
    -161: 'Attempt to modify a valid dump.',
    -160: 'The resource is presently in use by a system dumper.',
    -159: 'Attempt to re-copy an invalid dump.',
    -158: 'Data Management has not been enabled on the system.',
    -157: 'Pages are held in memory for the journal.',
    -156: 'Number of blocks read does not agree with recorded block count.',
    -155: 'This operation is not allowed for a directory.',
    -154: 'Directory pathname too long.',
    -153: 'Directory irreparably damaged.',
    -152: 'The dial identifier is already in use.',
    -151: 'The process is already serving a dial qualifier.',
    -150: 'Device type unknown to the system.',
    -149: 'Unrecoverable data-transmission error on physical device.',
    -148: 'Device is not currently usable.',
    -147: 'The device is not currently active.',
    -146: "The process's limit for this device type is exceeded.",
    -145: 'Physical end of device encountered.',
    -144: 'The device is in use.  It will be deleted when it is unassigned.',
    -143: 'Unrecognized character for this code translation.',
    -142: 'The requested device is not available.',
    -141: 'Device attention condition during eof record write.',
    -140: 'Condition requiring manual intervention with handler.',
    -139: 'I/O in progress on device.',
    -138: 'Specified offset out of bounds for this device.',
    -137: 'IO device not currently assigned.',
    -136: 'Looping searching definitions.',
    -135: 'Attempt to deactivate a segment with pages in memory.',
    -134: 'Unable to convert character date/time to binary.',
    -133: 'Data sequence error.',
    -132: 'Data has been lost.',
    -131: 'Relevant data terminated improperly.',
    -130: 'Data has been gained.',
    -129: 'Cyclic synonyms.',
    -128: 'The command line contained syntax characters not supported in this environment.',
    -127: 'There was an attempt to delete a segment whose copy switch was set.',
    -126: 'The command name is unavailable from the argument list.',
    -125: 'Expanded command line is too large.',
    -124: 'There was an attempt to move segment to non-zero length entry.',
    -123: 'Cannot add channel while its IOM is inactive.',
    -122: 'Cannot delete IOM with active channels.',
    -121: 'Channel is in the process of being deleted.',
    -120: 'Channel is already deleted.',
    -119: 'Channel is already added.',
    -118: 'Checksum error in data.',
    -117: 'Segment contains characters after final delimiter.',
    -116: 'Attempt to change first pointer.',
    -115: 'This entry cannot be traced.',
    -114: 'The buffer is in an invalid state.',
    -113: 'Specified buffer size too large.',
    -112: 'Attempt to access beyond end of segment.',
    -111: 'The rest of the tape is blank.',
    -110: 'Reverse interrupt detected on bisync line.',
    -109: 'Attempt to write improperly formated bisync block.',
    -108: 'Bisync line did not respond to line bid sequence.',
    -107: 'External variable or common block is not the same size as other uses of the same name.',
    -106: 'Argument too long.',
    -105: 'Insufficient access to use specified block size.',
    -104: 'Entry is for a begin block.',
    -103: 'Bad part dump card in config deck.',
    -102: 'Syntax error in ascii segment.',
    -101: 'Invalid syntax in starname.',
    -100: 'Input ring number invalid.',
    -99: 'Bad syntax in pathname.',
    -98: 'Specified control argument is not accepted.',
    -97: 'Illegal use of equals convention.',
    -96: 'Procedure called improperly.',
    -95: 'The year is not part of the 20th Century (1901 through 1999).',
    -94: 'Specified work class is not currently defined.',
    -93: 'Invalid volume identifier.',
    -92: 'Incorrect virtual channel specification.',
    -91: 'UID path cannot be converted to a pathname.',
    -90: 'Trap-before-link procedure was unable to snap link.',
    -89: 'The time is incorrect.',
    -88: 'Invalid volume name.',
    -87: 'Invalid argument to subroutine.',
    -86: 'Unable to process a search rule string.',
    -85: "Improper access on user's stack.",
    -84: 'Illegal self reference type.',
    -83: 'There is an internal inconsistency in the segment.',
    -82: 'Resource specification is invalid.',
    -81: 'Argument is not an ITS pointer.',
    -80: 'Current processid does not match stored value.',
    -79: 'Invalid process type.',
    -78: 'Illegal syntax in command line pipe.',
    -77: 'Incorrect password.',
    -76: 'Bad argument to specify the new key of a record.',
    -75: 'The access name specified has an illegal syntax.',
    -74: 'Directory or link found in multisegment file.',
    -73: 'Inconsistent multiplexer bootload data supplied.',
    -72: 'Mount request could not be honored.',
    -71: 'Invalid value for specified mode.',
    -70: 'Invalid syntax in mode string.',
    -69: 'Improper mode specification for this device.',
    -68: "Improper access on user's linkage segment.",
    -67: 'Illegal type code in type pair block.',
    -66: 'Illegal initialization info passed with create-if-not-found link.',
    -65: 'Incorrect detachable medium label.',
    -64: 'Improper target of indirect definition.',
    -63: 'Internal index out of bounds.',
    -62: 'Improper access on handler for this signal.',
    -61: 'Illegal structure provided for trap at first reference.',
    -60: 'Invalid syntax in entryname.',
    -59: 'File is not a structured file or is inconsistent.',
    -58: 'Illegal syntax in equal name.',
    -57: 'Illegal entry point name in make_ptr call.',
    -56: 'There is an inconsistency in this directory.',
    -55: 'Incorrect recording media density.',
    -54: 'Invalid link reference found in deferred initialiation structure.',
    -53: 'The day-of-the-week is incorrect.',
    -52: 'The date is incorrect.',
    -51: 'Error in conversion.',
    -50: 'Improper syntax in command name.',
    -49: 'Bad class code in definition.',
    -48: 'Incorrect IO channel specification.',
    -47: 'The signaller could not use the saved sp in the stack base for bar mode.',
    -46: 'Improper access to given argument.',
    -45: 'Invalid argument.',
    -44: 'Bad mode specification for ACL.',
    -43: 'Unknown authentication code.',
    -42: 'Incorrect authentication code.',
    -41: 'Attachment loop.',
    -40: 'Record with key for insertion has been added by another opening.',
    -39: 'Record located by seek_key has been deleted by another opening.',
    -38: 'A previously referenced item has been changed by another opening.',
    -37: 'A send_admin_command line attempted to read from user_i/o.',
    -36: 'The AS request message was too short or had a bad request type',
    -35: 'The sender of an AS request has logged out before being validated',
    -34: 'The process to be bumped was not found.',
    -33: 'There is an inconsistency in arguments to the storage system.',
    -32: 'Argument ignored.',
    -31: 'Supplied area too small for this request.',
    -30: 'Archive component pathname not permitted.',
    -29: 'Format error encountered in archive segment.',
    -28: 'This procedure may not modify archive components.',
    -27: 'Active process table is full.  Could not create process.',
    -26: 'Initialization has already been completed and will not be re-done.',
    -25: 'Indicated device assigned to another process.',
    -24: 'Entry access class is less than its parent.',
    -23: 'Improper access class/authorization to perform operation.',
    -22: 'Parent access class is greater than its son.',
    -21: 'The access class/authorization is not within the range in common between the two systems.',
    -20: 'The specified access class/authorization is not within the permitted range.',
    -19: 'There are no access classes/authorizations in common between the two systems.',
    -18: 'Unable to convert access class/authorization to binary.',
    -17: 'The specified access classes/authorizations are not a valid range.',
    -16: 'Unable to convert binary access class/authorization to string.',
    -15: 'Branch and VTOCE access class mismatch.',
    -14: 'The channel already has a required access class.',
    -13: 'Specified access class/authorization is greater than allowed maximum.',
    -12: 'This command cannot be invoked as an active function.',
    -11: 'The requested action was not performed.',
    -10: 'One or more memory frames are abs-wired.',
    -9: 'absentee: CPU time limit exceeded.  Job terminated.',
    -8: 'absentee: Attempt to reenter user environment via a call to cu_$cl.  Job terminated.',
    -7: 'No command name available.',
    -6: 'No such file or directory.',
    -5: 'Error processing file.',
    -4: 'Unknown user.'}
        self.no_such_user = PL1.EnumValue(name, 'no_such_user', -4)
        self.fileioerr = PL1.EnumValue(name, 'fileioerr', -5)
        self.no_directory_entry = PL1.EnumValue(name, 'no_directory_entry', -6)
        self.no_command_name_available = PL1.EnumValue(name, 'no_command_name_available', -7)
        self.abs_reenter = PL1.EnumValue(name, 'abs_reenter', -8)
        self.absrentr = PL1.EnumValue(name, 'absrentr', -8)
        self.abs_timer_runout = PL1.EnumValue(name, 'abs_timer_runout', -9)
        self.abstimer = PL1.EnumValue(name, 'abstimer', -9)
        self.abs_wired_memory = PL1.EnumValue(name, 'abs_wired_memory', -10)
        self.abswired = PL1.EnumValue(name, 'abswired', -10)
        self.action_not_performed = PL1.EnumValue(name, 'action_not_performed', -11)
        self.notacted = PL1.EnumValue(name, 'notacted', -11)
        self.active_function = PL1.EnumValue(name, 'active_function', -12)
        self.not_cmd = PL1.EnumValue(name, 'not_cmd', -12)
        self.ai_above_allowed_max = PL1.EnumValue(name, 'ai_above_allowed_max', -13)
        self.ai_max = PL1.EnumValue(name, 'ai_max', -13)
        self.ai_already_set = PL1.EnumValue(name, 'ai_already_set', -14)
        self.aialrdy = PL1.EnumValue(name, 'aialrdy', -14)
        self.ai_entry_vtoce_mismatch = PL1.EnumValue(name, 'ai_entry_vtoce_mismatch', -15)
        self.aibdvtce = PL1.EnumValue(name, 'aibdvtce', -15)
        self.ai_invalid_binary = PL1.EnumValue(name, 'ai_invalid_binary', -16)
        self.aibadbin = PL1.EnumValue(name, 'aibadbin', -16)
        self.ai_invalid_range = PL1.EnumValue(name, 'ai_invalid_range', -17)
        self.aibadrng = PL1.EnumValue(name, 'aibadrng', -17)
        self.ai_invalid_string = PL1.EnumValue(name, 'ai_invalid_string', -18)
        self.aibadstr = PL1.EnumValue(name, 'aibadstr', -18)
        self.ai_no_common_max = PL1.EnumValue(name, 'ai_no_common_max', -19)
        self.aincmax = PL1.EnumValue(name, 'aincmax', -19)
        self.ai_out_range = PL1.EnumValue(name, 'ai_out_range', -20)
        self.aioutrng = PL1.EnumValue(name, 'aioutrng', -20)
        self.ai_outside_common_range = PL1.EnumValue(name, 'ai_outside_common_range', -21)
        self.aiocr = PL1.EnumValue(name, 'aiocr', -21)
        self.ai_parent_greater = PL1.EnumValue(name, 'ai_parent_greater', -22)
        self.aiparbig = PL1.EnumValue(name, 'aiparbig', -22)
        self.ai_restricted = PL1.EnumValue(name, 'ai_restricted', -23)
        self.ai_stop = PL1.EnumValue(name, 'ai_stop', -23)
        self.ai_son_less = PL1.EnumValue(name, 'ai_son_less', -24)
        self.aisonles = PL1.EnumValue(name, 'aisonles', -24)
        self.already_assigned = PL1.EnumValue(name, 'already_assigned', -25)
        self.assigned = PL1.EnumValue(name, 'assigned', -25)
        self.already_initialized = PL1.EnumValue(name, 'already_initialized', -26)
        self.noreinit = PL1.EnumValue(name, 'noreinit', -26)
        self.apt_full = PL1.EnumValue(name, 'apt_full', -27)
        self.aptfull = PL1.EnumValue(name, 'aptfull', -27)
        self.archive_component_modification = PL1.EnumValue(name, 'archive_component_modification', -28)
        self.compmod = PL1.EnumValue(name, 'compmod', -28)
        self.archive_fmt_err = PL1.EnumValue(name, 'archive_fmt_err', -29)
        self.acfmterr = PL1.EnumValue(name, 'acfmterr', -29)
        self.archive_pathname = PL1.EnumValue(name, 'archive_pathname', -30)
        self.ac_path = PL1.EnumValue(name, 'ac_path', -30)
        self.area_too_small = PL1.EnumValue(name, 'area_too_small', -31)
        self.areasmal = PL1.EnumValue(name, 'areasmal', -31)
        self.arg_ignored = PL1.EnumValue(name, 'arg_ignored', -32)
        self.arg_ign = PL1.EnumValue(name, 'arg_ign', -32)
        self.argerr = PL1.EnumValue(name, 'argerr', -33)
        self.as_bump_user_not_found = PL1.EnumValue(name, 'as_bump_user_not_found', -34)
        self.asbmpusr = PL1.EnumValue(name, 'asbmpusr', -34)
        self.as_request_sender_missing = PL1.EnumValue(name, 'as_request_sender_missing', -35)
        self.assender = PL1.EnumValue(name, 'assender', -35)
        self.as_request_invalid_request = PL1.EnumValue(name, 'as_request_invalid_request', -36)
        self.asinval = PL1.EnumValue(name, 'asinval', -36)
        self.as_sac_command_read = PL1.EnumValue(name, 'as_sac_command_read', -37)
        self.assacrd = PL1.EnumValue(name, 'assacrd', -37)
        self.asynch_change = PL1.EnumValue(name, 'asynch_change', -38)
        self.asyncchg = PL1.EnumValue(name, 'asyncchg', -38)
        self.asynch_deletion = PL1.EnumValue(name, 'asynch_deletion', -39)
        self.asyncdel = PL1.EnumValue(name, 'asyncdel', -39)
        self.asynch_insertion = PL1.EnumValue(name, 'asynch_insertion', -40)
        self.as_ins = PL1.EnumValue(name, 'as_ins', -40)
        self.att_loop = PL1.EnumValue(name, 'att_loop', -41)
        self.auth_incorrect = PL1.EnumValue(name, 'auth_incorrect', -42)
        self.authinc = PL1.EnumValue(name, 'authinc', -42)
        self.auth_unknown = PL1.EnumValue(name, 'auth_unknown', -43)
        self.authun = PL1.EnumValue(name, 'authun', -43)
        self.bad_acl_mode = PL1.EnumValue(name, 'bad_acl_mode', -44)
        self.badacmod = PL1.EnumValue(name, 'badacmod', -44)
        self.bad_arg = PL1.EnumValue(name, 'bad_arg', -45)
        self.badarg = PL1.EnumValue(name, 'badarg', -45)
        self.bad_arg = PL1.EnumValue(name, 'bad_arg', -45)
        self.bad_arg_acc = PL1.EnumValue(name, 'bad_arg_acc', -46)
        self.badargac = PL1.EnumValue(name, 'badargac', -46)
        self.bad_bar_sp = PL1.EnumValue(name, 'bad_bar_sp', -47)
        self.badbarsp = PL1.EnumValue(name, 'badbarsp', -47)
        self.bad_channel = PL1.EnumValue(name, 'bad_channel', -48)
        self.badchnnl = PL1.EnumValue(name, 'badchnnl', -48)
        self.bad_class_def = PL1.EnumValue(name, 'bad_class_def', -49)
        self.badclass = PL1.EnumValue(name, 'badclass', -49)
        self.bad_command_name = PL1.EnumValue(name, 'bad_command_name', -50)
        self.badcomnm = PL1.EnumValue(name, 'badcomnm', -50)
        self.bad_conversion = PL1.EnumValue(name, 'bad_conversion', -51)
        self.bad_conv = PL1.EnumValue(name, 'bad_conv', -51)
        self.bad_date = PL1.EnumValue(name, 'bad_date', -52)
        self.bad_date = PL1.EnumValue(name, 'bad_date', -52)
        self.bad_day_of_week = PL1.EnumValue(name, 'bad_day_of_week', -53)
        self.bad_dow = PL1.EnumValue(name, 'bad_dow', -53)
        self.bad_deferred_init = PL1.EnumValue(name, 'bad_deferred_init', -54)
        self.baddefin = PL1.EnumValue(name, 'baddefin', -54)
        self.bad_density = PL1.EnumValue(name, 'bad_density', -55)
        self.bad_dens = PL1.EnumValue(name, 'bad_dens', -55)
        self.bad_dir = PL1.EnumValue(name, 'bad_dir', -56)
        self.bad_entry_point_name = PL1.EnumValue(name, 'bad_entry_point_name', -57)
        self.badename = PL1.EnumValue(name, 'badename', -57)
        self.bad_equal_name = PL1.EnumValue(name, 'bad_equal_name', -58)
        self.bdeqlnam = PL1.EnumValue(name, 'bdeqlnam', -58)
        self.bad_file = PL1.EnumValue(name, 'bad_file', -59)
        self.bad_file = PL1.EnumValue(name, 'bad_file', -59)
        self.bad_file_name = PL1.EnumValue(name, 'bad_file_name', -60)
        self.badentry = PL1.EnumValue(name, 'badentry', -60)
        self.bad_first_ref_trap = PL1.EnumValue(name, 'bad_first_ref_trap', -61)
        self.bdfrtrap = PL1.EnumValue(name, 'bdfrtrap', -61)
        self.bad_handler_access = PL1.EnumValue(name, 'bad_handler_access', -62)
        self.noacchd = PL1.EnumValue(name, 'noacchd', -62)
        self.bad_index = PL1.EnumValue(name, 'bad_index', -63)
        self.badindex = PL1.EnumValue(name, 'badindex', -63)
        self.bad_indirect_def = PL1.EnumValue(name, 'bad_indirect_def', -64)
        self.bdinddef = PL1.EnumValue(name, 'bdinddef', -64)
        self.bad_label = PL1.EnumValue(name, 'bad_label', -65)
        self.badlabel = PL1.EnumValue(name, 'badlabel', -65)
        self.bad_link_target_init_info = PL1.EnumValue(name, 'bad_link_target_init_info', -66)
        self.bdlkinit = PL1.EnumValue(name, 'bdlkinit', -66)
        self.bad_link_type = PL1.EnumValue(name, 'bad_link_type', -67)
        self.badlktyp = PL1.EnumValue(name, 'badlktyp', -67)
        self.bad_linkage_access = PL1.EnumValue(name, 'bad_linkage_access', -68)
        self.bdlnkac = PL1.EnumValue(name, 'bdlnkac', -68)
        self.bad_mode = PL1.EnumValue(name, 'bad_mode', -69)
        self.badmode = PL1.EnumValue(name, 'badmode', -69)
        self.bad_mode_syntax = PL1.EnumValue(name, 'bad_mode_syntax', -70)
        self.bdmdsynt = PL1.EnumValue(name, 'bdmdsynt', -70)
        self.bad_mode_value = PL1.EnumValue(name, 'bad_mode_value', -71)
        self.badmdval = PL1.EnumValue(name, 'badmdval', -71)
        self.bad_mount_request = PL1.EnumValue(name, 'bad_mount_request', -72)
        self.badmount = PL1.EnumValue(name, 'badmount', -72)
        self.bad_mpx_load_data = PL1.EnumValue(name, 'bad_mpx_load_data', -73)
        self.badload = PL1.EnumValue(name, 'badload', -73)
        self.bad_ms_file = PL1.EnumValue(name, 'bad_ms_file', -74)
        self.badmsfil = PL1.EnumValue(name, 'badmsfil', -74)
        self.bad_name = PL1.EnumValue(name, 'bad_name', -75)
        self.bad_new_key = PL1.EnumValue(name, 'bad_new_key', -76)
        self.x_newkey = PL1.EnumValue(name, 'x_newkey', -76)
        self.bad_password = PL1.EnumValue(name, 'bad_password', -77)
        self.badpass = PL1.EnumValue(name, 'badpass', -77)
        self.bad_pipe_syntax = PL1.EnumValue(name, 'bad_pipe_syntax', -78)
        self.pipesyn = PL1.EnumValue(name, 'pipesyn', -78)
        self.bad_process_type = PL1.EnumValue(name, 'bad_process_type', -79)
        self.badproct = PL1.EnumValue(name, 'badproct', -79)
        self.bad_processid = PL1.EnumValue(name, 'bad_processid', -80)
        self.badproci = PL1.EnumValue(name, 'badproci', -80)
        self.bad_ptr = PL1.EnumValue(name, 'bad_ptr', -81)
        self.badptr = PL1.EnumValue(name, 'badptr', -81)
        self.bad_resource_spec = PL1.EnumValue(name, 'bad_resource_spec', -82)
        self.bad_rsc = PL1.EnumValue(name, 'bad_rsc', -82)
        self.bad_segment = PL1.EnumValue(name, 'bad_segment', -83)
        self.badseg = PL1.EnumValue(name, 'badseg', -83)
        self.bad_self_ref = PL1.EnumValue(name, 'bad_self_ref', -84)
        self.badslfrf = PL1.EnumValue(name, 'badslfrf', -84)
        self.bad_stack_access = PL1.EnumValue(name, 'bad_stack_access', -85)
        self.noaccsp = PL1.EnumValue(name, 'noaccsp', -85)
        self.bad_string = PL1.EnumValue(name, 'bad_string', -86)
        self.badstrng = PL1.EnumValue(name, 'badstrng', -86)
        self.bad_subr_arg = PL1.EnumValue(name, 'bad_subr_arg', -87)
        self.badsbarg = PL1.EnumValue(name, 'badsbarg', -87)
        self.bad_tapeid = PL1.EnumValue(name, 'bad_tapeid', -88)
        self.badtpid = PL1.EnumValue(name, 'badtpid', -88)
        self.bad_time = PL1.EnumValue(name, 'bad_time', -89)
        self.bad_time = PL1.EnumValue(name, 'bad_time', -89)
        self.bad_trap_before_link = PL1.EnumValue(name, 'bad_trap_before_link', -90)
        self.bdtrb4lk = PL1.EnumValue(name, 'bdtrb4lk', -90)
        self.bad_uidpath = PL1.EnumValue(name, 'bad_uidpath', -91)
        self.baduidpn = PL1.EnumValue(name, 'baduidpn', -91)
        self.bad_vchannel = PL1.EnumValue(name, 'bad_vchannel', -92)
        self.badvchn = PL1.EnumValue(name, 'badvchn', -92)
        self.bad_volid = PL1.EnumValue(name, 'bad_volid', -93)
        self.badvolid = PL1.EnumValue(name, 'badvolid', -93)
        self.bad_work_class = PL1.EnumValue(name, 'bad_work_class', -94)
        self.badwc = PL1.EnumValue(name, 'badwc', -94)
        self.bad_year = PL1.EnumValue(name, 'bad_year', -95)
        self.bad_year = PL1.EnumValue(name, 'bad_year', -95)
        self.badcall = PL1.EnumValue(name, 'badcall', -96)
        self.badequal = PL1.EnumValue(name, 'badequal', -97)
        self.badopt = PL1.EnumValue(name, 'badopt', -98)
        self.bad_opt = PL1.EnumValue(name, 'bad_opt', -98)
        self.badpath = PL1.EnumValue(name, 'badpath', -99)
        self.badringno = PL1.EnumValue(name, 'badringno', -100)
        self.badrngno = PL1.EnumValue(name, 'badrngno', -100)
        self.badstar = PL1.EnumValue(name, 'badstar', -101)
        self.badsyntax = PL1.EnumValue(name, 'badsyntax', -102)
        self.badsyntx = PL1.EnumValue(name, 'badsyntx', -102)
        self.bdprtdmp = PL1.EnumValue(name, 'bdprtdmp', -103)
        self.begin_block = PL1.EnumValue(name, 'begin_block', -104)
        self.beginent = PL1.EnumValue(name, 'beginent', -104)
        self.big_ws_req = PL1.EnumValue(name, 'big_ws_req', -105)
        self.bigwsreq = PL1.EnumValue(name, 'bigwsreq', -105)
        self.bigarg = PL1.EnumValue(name, 'bigarg', -106)
        self.bigger_ext_variable = PL1.EnumValue(name, 'bigger_ext_variable', -107)
        self.bigexvar = PL1.EnumValue(name, 'bigexvar', -107)
        self.bisync_bid_fail = PL1.EnumValue(name, 'bisync_bid_fail', -108)
        self.bscbidf = PL1.EnumValue(name, 'bscbidf', -108)
        self.bisync_block_bad = PL1.EnumValue(name, 'bisync_block_bad', -109)
        self.bscblkbd = PL1.EnumValue(name, 'bscblkbd', -109)
        self.bisync_reverse_interrupt = PL1.EnumValue(name, 'bisync_reverse_interrupt', -110)
        self.bscrvi = PL1.EnumValue(name, 'bscrvi', -110)
        self.blank_tape = PL1.EnumValue(name, 'blank_tape', -111)
        self.blanktap = PL1.EnumValue(name, 'blanktap', -111)
        self.boundviol = PL1.EnumValue(name, 'boundviol', -112)
        self.outbnd = PL1.EnumValue(name, 'outbnd', -112)
        self.buffer_big = PL1.EnumValue(name, 'buffer_big', -113)
        self.buffbig = PL1.EnumValue(name, 'buffbig', -113)
        self.buffer_invalid_state = PL1.EnumValue(name, 'buffer_invalid_state', -114)
        self.bufstate = PL1.EnumValue(name, 'bufstate', -114)
        self.cannot_trace = PL1.EnumValue(name, 'cannot_trace', -115)
        self.notrace = PL1.EnumValue(name, 'notrace', -115)
        self.change_first = PL1.EnumValue(name, 'change_first', -116)
        self.chfirst = PL1.EnumValue(name, 'chfirst', -116)
        self.chars_after_delim = PL1.EnumValue(name, 'chars_after_delim', -117)
        self.undelch = PL1.EnumValue(name, 'undelch', -117)
        self.checksum_failure = PL1.EnumValue(name, 'checksum_failure', -118)
        self.NOTchksum = PL1.EnumValue(name, 'NOTchksum', -118)
        self.chnl_already_added = PL1.EnumValue(name, 'chnl_already_added', -119)
        self.chnadded = PL1.EnumValue(name, 'chnadded', -119)
        self.chnl_already_deleted = PL1.EnumValue(name, 'chnl_already_deleted', -120)
        self.chndltd = PL1.EnumValue(name, 'chndltd', -120)
        self.chnl_being_deleted = PL1.EnumValue(name, 'chnl_being_deleted', -121)
        self.chndltg = PL1.EnumValue(name, 'chndltg', -121)
        self.chnl_iom_active = PL1.EnumValue(name, 'chnl_iom_active', -122)
        self.chnlioma = PL1.EnumValue(name, 'chnlioma', -122)
        self.chnl_iom_inactive = PL1.EnumValue(name, 'chnl_iom_inactive', -123)
        self.chnnoiom = PL1.EnumValue(name, 'chnnoiom', -123)
        self.clnzero = PL1.EnumValue(name, 'clnzero', -124)
        self.nonzero = PL1.EnumValue(name, 'nonzero', -124)
        self.command_line_overflow = PL1.EnumValue(name, 'command_line_overflow', -125)
        self.clnovrfl = PL1.EnumValue(name, 'clnovrfl', -125)
        self.command_name_not_available = PL1.EnumValue(name, 'command_name_not_available', -126)
        self.comnotav = PL1.EnumValue(name, 'comnotav', -126)
        self.copy_sw_on = PL1.EnumValue(name, 'copy_sw_on', -127)
        self.copyswon = PL1.EnumValue(name, 'copyswon', -127)
        self.cp_reserved_syntax = PL1.EnumValue(name, 'cp_reserved_syntax', -128)
        self.cpresv = PL1.EnumValue(name, 'cpresv', -128)
        self.cyclic_syn = PL1.EnumValue(name, 'cyclic_syn', -129)
        self.cyc_syn = PL1.EnumValue(name, 'cyc_syn', -129)
        self.data_gain = PL1.EnumValue(name, 'data_gain', -130)
        self.datagain = PL1.EnumValue(name, 'datagain', -130)
        self.data_improperly_terminated = PL1.EnumValue(name, 'data_improperly_terminated', -131)
        self.dtnoterm = PL1.EnumValue(name, 'dtnoterm', -131)
        self.data_loss = PL1.EnumValue(name, 'data_loss', -132)
        self.dataloss = PL1.EnumValue(name, 'dataloss', -132)
        self.data_seq_error = PL1.EnumValue(name, 'data_seq_error', -133)
        self.datasqer = PL1.EnumValue(name, 'datasqer', -133)
        self.date_conversion_error = PL1.EnumValue(name, 'date_conversion_error', -134)
        self.daterr = PL1.EnumValue(name, 'daterr', -134)
        self.deact_in_mem = PL1.EnumValue(name, 'deact_in_mem', -135)
        self.deactmem = PL1.EnumValue(name, 'deactmem', -135)
        self.defs_loop = PL1.EnumValue(name, 'defs_loop', -136)
        self.defsloop = PL1.EnumValue(name, 'defsloop', -136)
        self.dev_nt_assnd = PL1.EnumValue(name, 'dev_nt_assnd', -137)
        self.notassnd = PL1.EnumValue(name, 'notassnd', -137)
        self.dev_offset_out_of_bounds = PL1.EnumValue(name, 'dev_offset_out_of_bounds', -138)
        self.dvoffoob = PL1.EnumValue(name, 'dvoffoob', -138)
        self.device_active = PL1.EnumValue(name, 'device_active', -139)
        self.devactiv = PL1.EnumValue(name, 'devactiv', -139)
        self.device_attention = PL1.EnumValue(name, 'device_attention', -140)
        self.dvceattn = PL1.EnumValue(name, 'dvceattn', -140)
        self.device_attention_during_tm = PL1.EnumValue(name, 'device_attention_during_tm', -141)
        self.dadwtm = PL1.EnumValue(name, 'dadwtm', -141)
        self.device_busy = PL1.EnumValue(name, 'device_busy', -142)
        self.devbusy = PL1.EnumValue(name, 'devbusy', -142)
        self.device_code_alert = PL1.EnumValue(name, 'device_code_alert', -143)
        self.devcdalt = PL1.EnumValue(name, 'devcdalt', -143)
        self.device_deletion_deferred = PL1.EnumValue(name, 'device_deletion_deferred', -144)
        self.dvdldef = PL1.EnumValue(name, 'dvdldef', -144)
        self.device_end = PL1.EnumValue(name, 'device_end', -145)
        self.devend = PL1.EnumValue(name, 'devend', -145)
        self.device_limit_exceeded = PL1.EnumValue(name, 'device_limit_exceeded', -146)
        self.devlimex = PL1.EnumValue(name, 'devlimex', -146)
        self.device_not_active = PL1.EnumValue(name, 'device_not_active', -147)
        self.devntact = PL1.EnumValue(name, 'devntact', -147)
        self.device_not_usable = PL1.EnumValue(name, 'device_not_usable', -148)
        self.devntuse = PL1.EnumValue(name, 'devntuse', -148)
        self.device_parity = PL1.EnumValue(name, 'device_parity', -149)
        self.xmiterr = PL1.EnumValue(name, 'xmiterr', -149)
        self.device_type_unknown = PL1.EnumValue(name, 'device_type_unknown', -150)
        self.dtNOTknown = PL1.EnumValue(name, 'dtNOTknown', -150)
        self.dial_active = PL1.EnumValue(name, 'dial_active', -151)
        self.dialactv = PL1.EnumValue(name, 'dialactv', -151)
        self.dial_id_busy = PL1.EnumValue(name, 'dial_id_busy', -152)
        self.dialbusy = PL1.EnumValue(name, 'dialbusy', -152)
        self.dir_damage = PL1.EnumValue(name, 'dir_damage', -153)
        self.dirdamag = PL1.EnumValue(name, 'dirdamag', -153)
        self.dirlong = PL1.EnumValue(name, 'dirlong', -154)
        self.dirseg = PL1.EnumValue(name, 'dirseg', -155)
        self.discrepant_block_count = PL1.EnumValue(name, 'discrepant_block_count', -156)
        self.dsblkcnt = PL1.EnumValue(name, 'dsblkcnt', -156)
        self.dm_journal_pages_held = PL1.EnumValue(name, 'dm_journal_pages_held', -157)
        self.dmpghld = PL1.EnumValue(name, 'dmpghld', -157)
        self.dm_not_enabled = PL1.EnumValue(name, 'dm_not_enabled', -158)
        self.dmnten = PL1.EnumValue(name, 'dmnten', -158)
        self.dmpinvld = PL1.EnumValue(name, 'dmpinvld', -159)
        self.dmpr_in_use = PL1.EnumValue(name, 'dmpr_in_use', -160)
        self.dmpinuse = PL1.EnumValue(name, 'dmpinuse', -160)
        self.dmpvalid = PL1.EnumValue(name, 'dmpvalid', -161)
        self.dt_ambiguous_time = PL1.EnumValue(name, 'dt_ambiguous_time', -162)
        self.ambigtim = PL1.EnumValue(name, 'ambigtim', -162)
        self.dt_bad_day_of_week = PL1.EnumValue(name, 'dt_bad_day_of_week', -163)
        self.baddow = PL1.EnumValue(name, 'baddow', -163)
        self.dt_bad_dm = PL1.EnumValue(name, 'dt_bad_dm', -164)
        self.bad_dm = PL1.EnumValue(name, 'bad_dm', -164)
        self.dt_bad_dy = PL1.EnumValue(name, 'dt_bad_dy', -165)
        self.bad_dy = PL1.EnumValue(name, 'bad_dy', -165)
        self.dt_bad_format_selector = PL1.EnumValue(name, 'dt_bad_format_selector', -166)
        self.badfsel = PL1.EnumValue(name, 'badfsel', -166)
        self.dt_bad_fw = PL1.EnumValue(name, 'dt_bad_fw', -167)
        self.bad_fw = PL1.EnumValue(name, 'bad_fw', -167)
        self.dt_bad_my = PL1.EnumValue(name, 'dt_bad_my', -168)
        self.bad_my = PL1.EnumValue(name, 'bad_my', -168)
        self.dt_conflict = PL1.EnumValue(name, 'dt_conflict', -169)
        self.datemess = PL1.EnumValue(name, 'datemess', -169)
        self.dt_date_not_exist = PL1.EnumValue(name, 'dt_date_not_exist', -170)
        self.dategone = PL1.EnumValue(name, 'dategone', -170)
        self.dt_date_too_big = PL1.EnumValue(name, 'dt_date_too_big', -171)
        self.datebig = PL1.EnumValue(name, 'datebig', -171)
        self.dt_date_too_small = PL1.EnumValue(name, 'dt_date_too_small', -172)
        self.datesmal = PL1.EnumValue(name, 'datesmal', -172)
        self.dt_hour_gt_twelve = PL1.EnumValue(name, 'dt_hour_gt_twelve', -173)
        self.hrlarge = PL1.EnumValue(name, 'hrlarge', -173)
        self.dt_multiple_date_spec = PL1.EnumValue(name, 'dt_multiple_date_spec', -174)
        self.multdate = PL1.EnumValue(name, 'multdate', -174)
        self.dt_multiple_diw_spec = PL1.EnumValue(name, 'dt_multiple_diw_spec', -175)
        self.multdiw = PL1.EnumValue(name, 'multdiw', -175)
        self.dt_multiple_meaning = PL1.EnumValue(name, 'dt_multiple_meaning', -176)
        self.multmean = PL1.EnumValue(name, 'multmean', -176)
        self.dt_multiple_time_spec = PL1.EnumValue(name, 'dt_multiple_time_spec', -177)
        self.multtime = PL1.EnumValue(name, 'multtime', -177)
        self.dt_multiple_zone_spec = PL1.EnumValue(name, 'dt_multiple_zone_spec', -178)
        self.multzone = PL1.EnumValue(name, 'multzone', -178)
        self.dt_no_format_selector = PL1.EnumValue(name, 'dt_no_format_selector', -179)
        self.nofsel = PL1.EnumValue(name, 'nofsel', -179)
        self.dt_no_interval_units = PL1.EnumValue(name, 'dt_no_interval_units', -180)
        self.noiunit = PL1.EnumValue(name, 'noiunit', -180)
        self.dt_offset_too_big_negative = PL1.EnumValue(name, 'dt_offset_too_big_negative', -181)
        self.offbign = PL1.EnumValue(name, 'offbign', -181)
        self.dt_offset_too_big_positive = PL1.EnumValue(name, 'dt_offset_too_big_positive', -182)
        self.offbigp = PL1.EnumValue(name, 'offbigp', -182)
        self.dt_size_error = PL1.EnumValue(name, 'dt_size_error', -183)
        self.dtsizerr = PL1.EnumValue(name, 'dtsizerr', -183)
        self.dt_time_conversion_error = PL1.EnumValue(name, 'dt_time_conversion_error', -184)
        self.ticverr = PL1.EnumValue(name, 'ticverr', -184)
        self.dt_unknown_time_language = PL1.EnumValue(name, 'dt_unknown_time_language', -185)
        self.badtlang = PL1.EnumValue(name, 'badtlang', -185)
        self.dt_unknown_word = PL1.EnumValue(name, 'dt_unknown_word', -186)
        self.badword = PL1.EnumValue(name, 'badword', -186)
        self.dt_year_too_big = PL1.EnumValue(name, 'dt_year_too_big', -187)
        self.yearbig = PL1.EnumValue(name, 'yearbig', -187)
        self.dt_year_too_small = PL1.EnumValue(name, 'dt_year_too_small', -188)
        self.yearsmal = PL1.EnumValue(name, 'yearsmal', -188)
        self.dup_ent_name = PL1.EnumValue(name, 'dup_ent_name', -189)
        self.dupename = PL1.EnumValue(name, 'dupename', -189)
        self.duplicate_file_id = PL1.EnumValue(name, 'duplicate_file_id', -190)
        self.dupfid = PL1.EnumValue(name, 'dupfid', -190)
        self.duplicate_request = PL1.EnumValue(name, 'duplicate_request', -191)
        self.dup_req = PL1.EnumValue(name, 'dup_req', -191)
        self.echnego_awaiting_stop_sync = PL1.EnumValue(name, 'echnego_awaiting_stop_sync', -192)
        self.echostop = PL1.EnumValue(name, 'echostop', -192)
        self.ect_already_initialized = PL1.EnumValue(name, 'ect_already_initialized', -193)
        self.ectinit = PL1.EnumValue(name, 'ectinit', -193)
        self.ect_full = PL1.EnumValue(name, 'ect_full', -194)
        self.ectfull = PL1.EnumValue(name, 'ectfull', -194)
        self.eight_unaligned = PL1.EnumValue(name, 'eight_unaligned', -195)
        self.not8alin = PL1.EnumValue(name, 'not8alin', -195)
        self.empty_acl = PL1.EnumValue(name, 'empty_acl', -196)
        self.emptyacl = PL1.EnumValue(name, 'emptyacl', -196)
        self.empty_archive = PL1.EnumValue(name, 'empty_archive', -197)
        self.empty_ac = PL1.EnumValue(name, 'empty_ac', -197)
        self.empty_file = PL1.EnumValue(name, 'empty_file', -198)
        self.mt_file = PL1.EnumValue(name, 'mt_file', -198)
        self.empty_search_list = PL1.EnumValue(name, 'empty_search_list', -199)
        self.empsrls = PL1.EnumValue(name, 'empsrls', -199)
        self.end_of_info = PL1.EnumValue(name, 'end_of_info', -200)
        self.eoi = PL1.EnumValue(name, 'eoi', -200)
        self.entlong = PL1.EnumValue(name, 'entlong', -201)
        self.eof_record = PL1.EnumValue(name, 'eof_record', -202)
        self.eofr = PL1.EnumValue(name, 'eofr', -202)
        self.eov_on_write = PL1.EnumValue(name, 'eov_on_write', -203)
        self.eovonw = PL1.EnumValue(name, 'eovonw', -203)
        self.event_calls_not_masked = PL1.EnumValue(name, 'event_calls_not_masked', -204)
        self.callnmsk = PL1.EnumValue(name, 'callnmsk', -204)
        self.event_channel_cutoff = PL1.EnumValue(name, 'event_channel_cutoff', -205)
        self.chnout = PL1.EnumValue(name, 'chnout', -205)
        self.event_channel_not_cutoff = PL1.EnumValue(name, 'event_channel_not_cutoff', -206)
        self.chnnout = PL1.EnumValue(name, 'chnnout', -206)
        self.fatal_error = PL1.EnumValue(name, 'fatal_error', -207)
        self.fatalerr = PL1.EnumValue(name, 'fatalerr', -207)
        self.file_aborted = PL1.EnumValue(name, 'file_aborted', -208)
        self.flabort = PL1.EnumValue(name, 'flabort', -208)
        self.file_already_opened = PL1.EnumValue(name, 'file_already_opened', -209)
        self.fileopen = PL1.EnumValue(name, 'fileopen', -209)
        self.file_busy = PL1.EnumValue(name, 'file_busy', -210)
        self.filebusy = PL1.EnumValue(name, 'filebusy', -210)
        self.file_is_full = PL1.EnumValue(name, 'file_is_full', -211)
        self.filefull = PL1.EnumValue(name, 'filefull', -211)
        self.file_not_opened = PL1.EnumValue(name, 'file_not_opened', -212)
        self.not_open = PL1.EnumValue(name, 'not_open', -212)
        self.fim_fault = PL1.EnumValue(name, 'fim_fault', -213)
        self.fimflt = PL1.EnumValue(name, 'fimflt', -213)
        self.first_reference_trap = PL1.EnumValue(name, 'first_reference_trap', -214)
        self.firstref = PL1.EnumValue(name, 'firstref', -214)
        self.fnp_down = PL1.EnumValue(name, 'fnp_down', -215)
        self.force_unassign = PL1.EnumValue(name, 'force_unassign', -216)
        self.forcunas = PL1.EnumValue(name, 'forcunas', -216)
        self.frame_scope_err = PL1.EnumValue(name, 'frame_scope_err', -217)
        self.fscoperr = PL1.EnumValue(name, 'fscoperr', -217)
        self.fsdisk_bad_label = PL1.EnumValue(name, 'fsdisk_bad_label', -218)
        self.fsbdlb = PL1.EnumValue(name, 'fsbdlb', -218)
        self.fsdisk_drive_in_use = PL1.EnumValue(name, 'fsdisk_drive_in_use', -219)
        self.fsdinuse = PL1.EnumValue(name, 'fsdinuse', -219)
        self.fsdisk_not_ready = PL1.EnumValue(name, 'fsdisk_not_ready', -220)
        self.fsNOTrdy = PL1.EnumValue(name, 'fsNOTrdy', -220)
        self.fsdisk_not_salv = PL1.EnumValue(name, 'fsdisk_not_salv', -221)
        self.fsNOTsalv = PL1.EnumValue(name, 'fsNOTsalv', -221)
        self.fsdisk_not_storage = PL1.EnumValue(name, 'fsdisk_not_storage', -222)
        self.fsNOTstor = PL1.EnumValue(name, 'fsNOTstor', -222)
        self.fsdisk_old_label = PL1.EnumValue(name, 'fsdisk_old_label', -223)
        self.fsoldlb = PL1.EnumValue(name, 'fsoldlb', -223)
        self.fsdisk_old_vtoc = PL1.EnumValue(name, 'fsdisk_old_vtoc', -224)
        self.fsoldvt = PL1.EnumValue(name, 'fsoldvt', -224)
        self.fsdisk_phydev_err = PL1.EnumValue(name, 'fsdisk_phydev_err', -225)
        self.fsdeverr = PL1.EnumValue(name, 'fsdeverr', -225)
        self.fsdisk_pvtx_oob = PL1.EnumValue(name, 'fsdisk_pvtx_oob', -226)
        self.fspvxoob = PL1.EnumValue(name, 'fspvxoob', -226)
        self.full_hashtbl = PL1.EnumValue(name, 'full_hashtbl', -227)
        self.fullhash = PL1.EnumValue(name, 'fullhash', -227)
        self.fulldir = PL1.EnumValue(name, 'fulldir', -228)
        self.hardcore_sdw = PL1.EnumValue(name, 'hardcore_sdw', -229)
        self.hcsdw = PL1.EnumValue(name, 'hcsdw', -229)
        self.higher_inconsistency = PL1.EnumValue(name, 'higher_inconsistency', -230)
        self.hi_incon = PL1.EnumValue(name, 'hi_incon', -230)
        self.id_already_exists = PL1.EnumValue(name, 'id_already_exists', -231)
        self.idexists = PL1.EnumValue(name, 'idexists', -231)
        self.id_not_found = PL1.EnumValue(name, 'id_not_found', -232)
        self.idnotfnd = PL1.EnumValue(name, 'idnotfnd', -232)
        self.illegal_activation = PL1.EnumValue(name, 'illegal_activation', -233)
        self.bad_act = PL1.EnumValue(name, 'bad_act', -233)
        self.illegal_deactivation = PL1.EnumValue(name, 'illegal_deactivation', -234)
        self.deactive = PL1.EnumValue(name, 'deactive', -234)
        self.illegal_ft2 = PL1.EnumValue(name, 'illegal_ft2', -235)
        self.bad_ft2 = PL1.EnumValue(name, 'bad_ft2', -235)
        self.illegal_record_size = PL1.EnumValue(name, 'illegal_record_size', -236)
        self.rec_size = PL1.EnumValue(name, 'rec_size', -236)
        self.imp_bad_format = PL1.EnumValue(name, 'imp_bad_format', -237)
        self.impbdfmt = PL1.EnumValue(name, 'impbdfmt', -237)
        self.imp_bad_status = PL1.EnumValue(name, 'imp_bad_status', -238)
        self.impbadst = PL1.EnumValue(name, 'impbadst', -238)
        self.imp_down = PL1.EnumValue(name, 'imp_down', -239)
        self.impdown = PL1.EnumValue(name, 'impdown', -239)
        self.imp_rfnm_pending = PL1.EnumValue(name, 'imp_rfnm_pending', -240)
        self.imprfnm = PL1.EnumValue(name, 'imprfnm', -240)
        self.improper_data_format = PL1.EnumValue(name, 'improper_data_format', -241)
        self.baddtfmt = PL1.EnumValue(name, 'baddtfmt', -241)
        self.improper_termination = PL1.EnumValue(name, 'improper_termination', -242)
        self.badterm = PL1.EnumValue(name, 'badterm', -242)
        self.incompatible_attach = PL1.EnumValue(name, 'incompatible_attach', -243)
        self.attNEopn = PL1.EnumValue(name, 'attNEopn', -243)
        self.incompatible_encoding_mode = PL1.EnumValue(name, 'incompatible_encoding_mode', -244)
        self.incencmd = PL1.EnumValue(name, 'incencmd', -244)
        self.incompatible_file_attribute = PL1.EnumValue(name, 'incompatible_file_attribute', -245)
        self.incflatt = PL1.EnumValue(name, 'incflatt', -245)
        self.incompatible_term_type = PL1.EnumValue(name, 'incompatible_term_type', -246)
        self.intrmtyp = PL1.EnumValue(name, 'intrmtyp', -246)
        self.incomplete_access_name = PL1.EnumValue(name, 'incomplete_access_name', -247)
        self.incomnam = PL1.EnumValue(name, 'incomnam', -247)
        self.inconsistent = PL1.EnumValue(name, 'inconsistent', -248)
        self.incnstnt = PL1.EnumValue(name, 'incnstnt', -248)
        self.inconsistent_ect = PL1.EnumValue(name, 'inconsistent_ect', -249)
        self.badect = PL1.EnumValue(name, 'badect', -249)
        self.inconsistent_msf = PL1.EnumValue(name, 'inconsistent_msf', -250)
        self.incnsmsf = PL1.EnumValue(name, 'incnsmsf', -250)
        self.inconsistent_rnt = PL1.EnumValue(name, 'inconsistent_rnt', -251)
        self.badrnt = PL1.EnumValue(name, 'badrnt', -251)
        self.inconsistent_sst = PL1.EnumValue(name, 'inconsistent_sst', -252)
        self.badsst = PL1.EnumValue(name, 'badsst', -252)
        self.inconsistent_object_msf = PL1.EnumValue(name, 'inconsistent_object_msf', -253)
        self.incobmsf = PL1.EnumValue(name, 'incobmsf', -253)
        self.incorrect_access = PL1.EnumValue(name, 'incorrect_access', -254)
        self.incacc = PL1.EnumValue(name, 'incacc', -254)
        self.incorrect_device_type = PL1.EnumValue(name, 'incorrect_device_type', -255)
        self.incdevt = PL1.EnumValue(name, 'incdevt', -255)
        self.incorrect_volume_type = PL1.EnumValue(name, 'incorrect_volume_type', -256)
        self.incvolt = PL1.EnumValue(name, 'incvolt', -256)
        self.infcnt_non_zero = PL1.EnumValue(name, 'infcnt_non_zero', -257)
        self.makunk = PL1.EnumValue(name, 'makunk', -257)
        self.insufficient_access = PL1.EnumValue(name, 'insufficient_access', -258)
        self.mdc_no_access = PL1.EnumValue(name, 'mdc_no_access', -258)
        self.insufacc = PL1.EnumValue(name, 'insufacc', -258)
        self.insufficient_open = PL1.EnumValue(name, 'insufficient_open', -259)
        self.insufopn = PL1.EnumValue(name, 'insufopn', -259)
        self.invalid_array_size = PL1.EnumValue(name, 'invalid_array_size', -260)
        self.invarsz = PL1.EnumValue(name, 'invarsz', -260)
        self.invalid_ascii = PL1.EnumValue(name, 'invalid_ascii', -261)
        self.invascii = PL1.EnumValue(name, 'invascii', -261)
        self.invalid_backspace_read = PL1.EnumValue(name, 'invalid_backspace_read', -262)
        self.invbsr = PL1.EnumValue(name, 'invbsr', -262)
        self.invalid_block_length = PL1.EnumValue(name, 'invalid_block_length', -263)
        self.invblk = PL1.EnumValue(name, 'invblk', -263)
        self.invalid_channel = PL1.EnumValue(name, 'invalid_channel', -264)
        self.invalchn = PL1.EnumValue(name, 'invalchn', -264)
        self.invalid_copy = PL1.EnumValue(name, 'invalid_copy', -265)
        self.invalcpy = PL1.EnumValue(name, 'invalcpy', -265)
        self.invalid_cseg = PL1.EnumValue(name, 'invalid_cseg', -266)
        self.invcseg = PL1.EnumValue(name, 'invcseg', -266)
        self.invalid_delay_value = PL1.EnumValue(name, 'invalid_delay_value', -267)
        self.invdelay = PL1.EnumValue(name, 'invdelay', -267)
        self.invalid_device = PL1.EnumValue(name, 'invalid_device', -268)
        self.invdev = PL1.EnumValue(name, 'invdev', -268)
        self.invalid_dm_journal_index = PL1.EnumValue(name, 'invalid_dm_journal_index', -269)
        self.invjx = PL1.EnumValue(name, 'invjx', -269)
        self.invalid_elsize = PL1.EnumValue(name, 'invalid_elsize', -270)
        self.invelsiz = PL1.EnumValue(name, 'invelsiz', -270)
        self.invalid_expiration = PL1.EnumValue(name, 'invalid_expiration', -271)
        self.invexp = PL1.EnumValue(name, 'invexp', -271)
        self.invalid_file_set_format = PL1.EnumValue(name, 'invalid_file_set_format', -272)
        self.infsfmt = PL1.EnumValue(name, 'infsfmt', -272)
        self.invalid_heap = PL1.EnumValue(name, 'invalid_heap', -273)
        self.bad_heap = PL1.EnumValue(name, 'bad_heap', -273)
        self.invalid_heap_var_size = PL1.EnumValue(name, 'invalid_heap_var_size', -274)
        self.inhpvsiz = PL1.EnumValue(name, 'inhpvsiz', -274)
        self.invalid_label_format = PL1.EnumValue(name, 'invalid_label_format', -275)
        self.invlbfmt = PL1.EnumValue(name, 'invlbfmt', -275)
        self.invalid_line_type = PL1.EnumValue(name, 'invalid_line_type', -276)
        self.invlntyp = PL1.EnumValue(name, 'invlntyp', -276)
        self.invalid_lock_reset = PL1.EnumValue(name, 'invalid_lock_reset', -277)
        self.invalock = PL1.EnumValue(name, 'invalock', -277)
        self.invalid_max_length = PL1.EnumValue(name, 'invalid_max_length', -278)
        self.mlLTcl = PL1.EnumValue(name, 'mlLTcl', -278)
        self.invalid_mode = PL1.EnumValue(name, 'invalid_mode', -279)
        self.invmode = PL1.EnumValue(name, 'invmode', -279)
        self.invalid_move_qmax = PL1.EnumValue(name, 'invalid_move_qmax', -280)
        self.nomvqmax = PL1.EnumValue(name, 'nomvqmax', -280)
        self.invalid_move_quota = PL1.EnumValue(name, 'invalid_move_quota', -281)
        self.nomvquot = PL1.EnumValue(name, 'nomvquot', -281)
        self.invalid_mpx_type = PL1.EnumValue(name, 'invalid_mpx_type', -282)
        self.invmpx = PL1.EnumValue(name, 'invmpx', -282)
        self.invalid_preaccess_command = PL1.EnumValue(name, 'invalid_preaccess_command', -283)
        self.inprecom = PL1.EnumValue(name, 'inprecom', -283)
        self.invalid_project_for_gate = PL1.EnumValue(name, 'invalid_project_for_gate', -284)
        self.invprjgt = PL1.EnumValue(name, 'invprjgt', -284)
        self.invalid_ptr_target = PL1.EnumValue(name, 'invalid_ptr_target', -285)
        self.invprtar = PL1.EnumValue(name, 'invprtar', -285)
        self.invalid_pvtx = PL1.EnumValue(name, 'invalid_pvtx', -286)
        self.invpvtx = PL1.EnumValue(name, 'invpvtx', -286)
        self.invalid_read = PL1.EnumValue(name, 'invalid_read', -287)
        self.invread = PL1.EnumValue(name, 'invread', -287)
        self.invalid_record_desc = PL1.EnumValue(name, 'invalid_record_desc', -288)
        self.invrdes = PL1.EnumValue(name, 'invrdes', -288)
        self.invalid_record_length = PL1.EnumValue(name, 'invalid_record_length', -289)
        self.invrec = PL1.EnumValue(name, 'invrec', -289)
        self.invalid_resource_state = PL1.EnumValue(name, 'invalid_resource_state', -290)
        self.invrscst = PL1.EnumValue(name, 'invrscst', -290)
        self.invalid_ring_brackets = PL1.EnumValue(name, 'invalid_ring_brackets', -291)
        self.badringb = PL1.EnumValue(name, 'badringb', -291)
        self.invalid_seek_last_bound = PL1.EnumValue(name, 'invalid_seek_last_bound', -292)
        self.invseek = PL1.EnumValue(name, 'invseek', -292)
        self.invalid_setdelim = PL1.EnumValue(name, 'invalid_setdelim', -293)
        self.invsetdl = PL1.EnumValue(name, 'invsetdl', -293)
        self.invalid_stack_creation = PL1.EnumValue(name, 'invalid_stack_creation', -294)
        self.badstkcr = PL1.EnumValue(name, 'badstkcr', -294)
        self.invalid_state = PL1.EnumValue(name, 'invalid_state', -295)
        self.invalst = PL1.EnumValue(name, 'invalst', -295)
        self.invalid_subsystem = PL1.EnumValue(name, 'invalid_subsystem', -296)
        self.invsbsys = PL1.EnumValue(name, 'invsbsys', -296)
        self.invalid_system_type = PL1.EnumValue(name, 'invalid_system_type', -297)
        self.badsystp = PL1.EnumValue(name, 'badsystp', -297)
        self.invalid_tape_record_length = PL1.EnumValue(name, 'invalid_tape_record_length', -298)
        self.badtaprl = PL1.EnumValue(name, 'badtaprl', -298)
        self.invalid_tp_value = PL1.EnumValue(name, 'invalid_tp_value', -299)
        self.badtpval = PL1.EnumValue(name, 'badtpval', -299)
        self.invalid_volume_sequence = PL1.EnumValue(name, 'invalid_volume_sequence', -300)
        self.involseg = PL1.EnumValue(name, 'involseg', -300)
        self.invalid_vtoce = PL1.EnumValue(name, 'invalid_vtoce', -301)
        self.invvtoce = PL1.EnumValue(name, 'invvtoce', -301)
        self.invalid_vtocx = PL1.EnumValue(name, 'invalid_vtocx', -302)
        self.invvtocx = PL1.EnumValue(name, 'invvtocx', -302)
        self.invalid_write = PL1.EnumValue(name, 'invalid_write', -303)
        self.invwrite = PL1.EnumValue(name, 'invwrite', -303)
        self.invalidsegno = PL1.EnumValue(name, 'invalidsegno', -304)
        self.badsegno = PL1.EnumValue(name, 'badsegno', -304)
        self.io_assigned = PL1.EnumValue(name, 'io_assigned', -305)
        self.ioassgn = PL1.EnumValue(name, 'ioassgn', -305)
        self.io_configured = PL1.EnumValue(name, 'io_configured', -306)
        self.ioconf = PL1.EnumValue(name, 'ioconf', -306)
        self.io_no_path = PL1.EnumValue(name, 'io_no_path', -307)
        self.ionopath = PL1.EnumValue(name, 'ionopath', -307)
        self.io_no_permission = PL1.EnumValue(name, 'io_no_permission', -308)
        self.nopermit = PL1.EnumValue(name, 'nopermit', -308)
        self.io_not_assigned = PL1.EnumValue(name, 'io_not_assigned', -309)
        self.ioNOTassgn = PL1.EnumValue(name, 'ioNOTassgn', -309)
        self.io_not_available = PL1.EnumValue(name, 'io_not_available', -310)
        self.ioNOTavail = PL1.EnumValue(name, 'ioNOTavail', -310)
        self.io_not_configured = PL1.EnumValue(name, 'io_not_configured', -311)
        self.ioNOTconf = PL1.EnumValue(name, 'ioNOTconf', -311)
        self.io_not_defined = PL1.EnumValue(name, 'io_not_defined', -312)
        self.ioNOTdef = PL1.EnumValue(name, 'ioNOTdef', -312)
        self.io_still_assnd = PL1.EnumValue(name, 'io_still_assnd', -313)
        self.stilasnd = PL1.EnumValue(name, 'stilasnd', -313)
        self.ioat_err = PL1.EnumValue(name, 'ioat_err', -314)
        self.ioaterr = PL1.EnumValue(name, 'ioaterr', -314)
        self.iom_already_added = PL1.EnumValue(name, 'iom_already_added', -315)
        self.iomaadd = PL1.EnumValue(name, 'iomaadd', -315)
        self.iom_already_deleted = PL1.EnumValue(name, 'iom_already_deleted', -316)
        self.iomadel = PL1.EnumValue(name, 'iomadel', -316)
        self.iom_connect_fatal = PL1.EnumValue(name, 'iom_connect_fatal', -317)
        self.iomfatal = PL1.EnumValue(name, 'iomfatal', -317)
        self.iom_wrong_mailbox = PL1.EnumValue(name, 'iom_wrong_mailbox', -318)
        self.iombadmb = PL1.EnumValue(name, 'iombadmb', -318)
        self.iom_wrong_number = PL1.EnumValue(name, 'iom_wrong_number', -319)
        self.iombadnm = PL1.EnumValue(name, 'iombadnm', -319)
        self.ioname_not_active = PL1.EnumValue(name, 'ioname_not_active', -320)
        self.ionmnact = PL1.EnumValue(name, 'ionmnact', -320)
        self.ioname_not_found = PL1.EnumValue(name, 'ioname_not_found', -321)
        self.ionmnfnd = PL1.EnumValue(name, 'ionmnfnd', -321)
        self.ionmat = PL1.EnumValue(name, 'ionmat', -322)
        self.ips_has_occurred = PL1.EnumValue(name, 'ips_has_occurred', -323)
        self.ipsoccur = PL1.EnumValue(name, 'ipsoccur', -323)
        self.item_too_big = PL1.EnumValue(name, 'item_too_big', -324)
        self.ittoobig = PL1.EnumValue(name, 'ittoobig', -324)
        self.itt_overflow = PL1.EnumValue(name, 'itt_overflow', -325)
        self.ittfull = PL1.EnumValue(name, 'ittfull', -325)
        self.key_duplication = PL1.EnumValue(name, 'key_duplication', -326)
        self.key_dup = PL1.EnumValue(name, 'key_dup', -326)
        self.key_order = PL1.EnumValue(name, 'key_order', -327)
        self.keyorder = PL1.EnumValue(name, 'keyorder', -327)
        self.known_in_other_rings = PL1.EnumValue(name, 'known_in_other_rings', -328)
        self.kothrngs = PL1.EnumValue(name, 'kothrngs', -328)
        self.last_reference = PL1.EnumValue(name, 'last_reference', -329)
        self.last_ref = PL1.EnumValue(name, 'last_ref', -329)
        self.line_status_pending = PL1.EnumValue(name, 'line_status_pending', -330)
        self.lnstatp = PL1.EnumValue(name, 'lnstatp', -330)
        self.link = PL1.EnumValue(name, 'link', -331)
        self.link = PL1.EnumValue(name, 'link', -331)
        self.linkmoderr = PL1.EnumValue(name, 'linkmoderr', -332)
        self.linkmode = PL1.EnumValue(name, 'linkmode', -332)
        self.listen_stopped = PL1.EnumValue(name, 'listen_stopped', -333)
        self.lstnstop = PL1.EnumValue(name, 'lstnstop', -333)
        self.lock_is_invalid = PL1.EnumValue(name, 'lock_is_invalid', -334)
        self.lockinv = PL1.EnumValue(name, 'lockinv', -334)
        self.lock_not_locked = PL1.EnumValue(name, 'lock_not_locked', -335)
        self.unlocked = PL1.EnumValue(name, 'unlocked', -335)
        self.lock_wait_time_exceeded = PL1.EnumValue(name, 'lock_wait_time_exceeded', -336)
        self.loctimex = PL1.EnumValue(name, 'loctimex', -336)
        self.locked_by_other_process = PL1.EnumValue(name, 'locked_by_other_process', -337)
        self.hislock = PL1.EnumValue(name, 'hislock', -337)
        self.locked_by_this_process = PL1.EnumValue(name, 'locked_by_this_process', -338)
        self.mylock = PL1.EnumValue(name, 'mylock', -338)
        self.log_message_invalid_type = PL1.EnumValue(name, 'log_message_invalid_type', -339)
        self.logNOTtype = PL1.EnumValue(name, 'logNOTtype', -339)
        self.log_out_of_service = PL1.EnumValue(name, 'log_out_of_service', -340)
        self.loginop = PL1.EnumValue(name, 'loginop', -340)
        self.log_segment_damaged = PL1.EnumValue(name, 'log_segment_damaged', -341)
        self.logbust = PL1.EnumValue(name, 'logbust', -341)
        self.log_segment_empty = PL1.EnumValue(name, 'log_segment_empty', -342)
        self.logempty = PL1.EnumValue(name, 'logempty', -342)
        self.log_segment_full = PL1.EnumValue(name, 'log_segment_full', -343)
        self.logfull = PL1.EnumValue(name, 'logfull', -343)
        self.log_segment_invalid = PL1.EnumValue(name, 'log_segment_invalid', -344)
        self.logNOTval = PL1.EnumValue(name, 'logNOTval', -344)
        self.log_uninitialized = PL1.EnumValue(name, 'log_uninitialized', -345)
        self.logNOTinit = PL1.EnumValue(name, 'logNOTinit', -345)
        self.log_vol_full = PL1.EnumValue(name, 'log_vol_full', -346)
        self.logvolfl = PL1.EnumValue(name, 'logvolfl', -346)
        self.log_wakeup_table_full = PL1.EnumValue(name, 'log_wakeup_table_full', -347)
        self.logGTlstn = PL1.EnumValue(name, 'logGTlstn', -347)
        self.logical_volume_is_connected = PL1.EnumValue(name, 'logical_volume_is_connected', -348)
        self.LViscon = PL1.EnumValue(name, 'LViscon', -348)
        self.logical_volume_is_defined = PL1.EnumValue(name, 'logical_volume_is_defined', -349)
        self.LVisdef = PL1.EnumValue(name, 'LVisdef', -349)
        self.logical_volume_not_connected = PL1.EnumValue(name, 'logical_volume_not_connected', -350)
        self.LVnotcon = PL1.EnumValue(name, 'LVnotcon', -350)
        self.logical_volume_not_defined = PL1.EnumValue(name, 'logical_volume_not_defined', -351)
        self.LVnotdef = PL1.EnumValue(name, 'LVnotdef', -351)
        self.logical_volume_table_full = PL1.EnumValue(name, 'logical_volume_table_full', -352)
        self.LVT_full = PL1.EnumValue(name, 'LVT_full', -352)
        self.long_record = PL1.EnumValue(name, 'long_record', -353)
        self.long_rec = PL1.EnumValue(name, 'long_rec', -353)
        self.longeql = PL1.EnumValue(name, 'longeql', -354)
        self.lost_device_position = PL1.EnumValue(name, 'lost_device_position', -355)
        self.lstdevps = PL1.EnumValue(name, 'lstdevps', -355)
        self.lower_ring = PL1.EnumValue(name, 'lower_ring', -356)
        self.bad_ring_brackets = PL1.EnumValue(name, 'bad_ring_brackets', -356)
        self.low_ring = PL1.EnumValue(name, 'low_ring', -356)
        self.malformed_list_template_entry = PL1.EnumValue(name, 'malformed_list_template_entry', -357)
        self.badlstmp = PL1.EnumValue(name, 'badlstmp', -357)
        self.masked_channel = PL1.EnumValue(name, 'masked_channel', -358)
        self.maskchan = PL1.EnumValue(name, 'maskchan', -358)
        self.master_dir = PL1.EnumValue(name, 'master_dir', -359)
        self.mastrdir = PL1.EnumValue(name, 'mastrdir', -359)
        self.max_depth_exceeded = PL1.EnumValue(name, 'max_depth_exceeded', -360)
        self.GTlevels = PL1.EnumValue(name, 'GTlevels', -360)
        self.mc_no_c_permission = PL1.EnumValue(name, 'mc_no_c_permission', -361)
        self.mcNOTm = PL1.EnumValue(name, 'mcNOTm', -361)
        self.mc_no_d_permission = PL1.EnumValue(name, 'mc_no_d_permission', -362)
        self.mcNOTd = PL1.EnumValue(name, 'mcNOTd', -362)
        self.mc_no_q_permission = PL1.EnumValue(name, 'mc_no_q_permission', -363)
        self.mcNOTq = PL1.EnumValue(name, 'mcNOTq', -363)
        self.mc_no_r_permission = PL1.EnumValue(name, 'mc_no_r_permission', -364)
        self.mcNOTr = PL1.EnumValue(name, 'mcNOTr', -364)
        self.mdc_bad_quota = PL1.EnumValue(name, 'mdc_bad_quota', -365)
        self.mdcbadq = PL1.EnumValue(name, 'mdcbadq', -365)
        self.mdc_exec_access = PL1.EnumValue(name, 'mdc_exec_access', -366)
        self.mdcnoex = PL1.EnumValue(name, 'mdcnoex', -366)
        self.mdc_illegal_account = PL1.EnumValue(name, 'mdc_illegal_account', -367)
        self.mdcilacc = PL1.EnumValue(name, 'mdcilacc', -367)
        self.mdc_illegal_owner = PL1.EnumValue(name, 'mdc_illegal_owner', -368)
        self.mdcilown = PL1.EnumValue(name, 'mdcilown', -368)
        self.mdc_mdir_registered = PL1.EnumValue(name, 'mdc_mdir_registered', -369)
        self.mdcmdirg = PL1.EnumValue(name, 'mdcmdirg', -369)
        self.mdc_mdirs_registered = PL1.EnumValue(name, 'mdc_mdirs_registered', -370)
        self.mdcmdreg = PL1.EnumValue(name, 'mdcmdreg', -370)
        self.mdc_no_account = PL1.EnumValue(name, 'mdc_no_account', -371)
        self.mdcnoact = PL1.EnumValue(name, 'mdcnoact', -371)
        self.mdc_no_quota = PL1.EnumValue(name, 'mdc_no_quota', -372)
        self.mdcnoq = PL1.EnumValue(name, 'mdcnoq', -372)
        self.mdc_no_quota_account = PL1.EnumValue(name, 'mdc_no_quota_account', -373)
        self.mdcnoqa = PL1.EnumValue(name, 'mdcnoqa', -373)
        self.mdc_not_mdir = PL1.EnumValue(name, 'mdc_not_mdir', -374)
        self.mdcnotmd = PL1.EnumValue(name, 'mdcnotmd', -374)
        self.mdc_path_dup = PL1.EnumValue(name, 'mdc_path_dup', -375)
        self.mdcpathd = PL1.EnumValue(name, 'mdcpathd', -375)
        self.mdc_path_dup_args = PL1.EnumValue(name, 'mdc_path_dup_args', -376)
        self.mdcdparg = PL1.EnumValue(name, 'mdcdparg', -376)
        self.mdc_path_not_found = PL1.EnumValue(name, 'mdc_path_not_found', -377)
        self.mdcpathn = PL1.EnumValue(name, 'mdcpathn', -377)
        self.mdc_path_restrict = PL1.EnumValue(name, 'mdc_path_restrict', -378)
        self.mdcpathr = PL1.EnumValue(name, 'mdcpathr', -378)
        self.mdc_some_error = PL1.EnumValue(name, 'mdc_some_error', -379)
        self.mdcsome = PL1.EnumValue(name, 'mdcsome', -379)
        self.mdc_unregistered_mdir = PL1.EnumValue(name, 'mdc_unregistered_mdir', -380)
        self.mdcunreg = PL1.EnumValue(name, 'mdcunreg', -380)
        self.media_not_removable = PL1.EnumValue(name, 'media_not_removable', -381)
        self.mdntrmvb = PL1.EnumValue(name, 'mdntrmvb', -381)
        self.messages_deferred = PL1.EnumValue(name, 'messages_deferred', -382)
        self.msgdefer = PL1.EnumValue(name, 'msgdefer', -382)
        self.messages_off = PL1.EnumValue(name, 'messages_off', -383)
        self.msgs_off = PL1.EnumValue(name, 'msgs_off', -383)
        self.mismatched_iter = PL1.EnumValue(name, 'mismatched_iter', -384)
        self.mismatit = PL1.EnumValue(name, 'mismatit', -384)
        self.missent = PL1.EnumValue(name, 'missent', -385)
        self.mode_string_truncated = PL1.EnumValue(name, 'mode_string_truncated', -386)
        self.mdetrunc = PL1.EnumValue(name, 'mdetrunc', -386)
        self.moderr = PL1.EnumValue(name, 'moderr', -387)
        self.mount_not_ready = PL1.EnumValue(name, 'mount_not_ready', -388)
        self.mtnotrdy = PL1.EnumValue(name, 'mtnotrdy', -388)
        self.mount_pending = PL1.EnumValue(name, 'mount_pending', -389)
        self.mtpend = PL1.EnumValue(name, 'mtpend', -389)
        self.mpx_down = PL1.EnumValue(name, 'mpx_down', -390)
        self.mpx_down = PL1.EnumValue(name, 'mpx_down', -390)
        self.msf = PL1.EnumValue(name, 'msf', -391)
        self.msf = PL1.EnumValue(name, 'msf', -391)
        self.multiple_io_attachment = PL1.EnumValue(name, 'multiple_io_attachment', -392)
        self.multioat = PL1.EnumValue(name, 'multioat', -392)
        self.mylock = PL1.EnumValue(name, 'mylock', -393)
        self.mylock = PL1.EnumValue(name, 'mylock', -393)
        self.name_not_found = PL1.EnumValue(name, 'name_not_found', -394)
        self.namenfd = PL1.EnumValue(name, 'namenfd', -394)
        self.namedup = PL1.EnumValue(name, 'namedup', -395)
        self.ncp_error = PL1.EnumValue(name, 'ncp_error', -396)
        self.ncperror = PL1.EnumValue(name, 'ncperror', -396)
        self.negative_nelem = PL1.EnumValue(name, 'negative_nelem', -397)
        self.negnelem = PL1.EnumValue(name, 'negnelem', -397)
        self.negative_offset = PL1.EnumValue(name, 'negative_offset', -398)
        self.negofset = PL1.EnumValue(name, 'negofset', -398)
        self.net_already_icp = PL1.EnumValue(name, 'net_already_icp', -399)
        self.sock_icp = PL1.EnumValue(name, 'sock_icp', -399)
        self.net_bad_gender = PL1.EnumValue(name, 'net_bad_gender', -400)
        self.netbgend = PL1.EnumValue(name, 'netbgend', -400)
        self.net_fhost_down = PL1.EnumValue(name, 'net_fhost_down', -401)
        self.fhostdwn = PL1.EnumValue(name, 'fhostdwn', -401)
        self.net_fhost_inactive = PL1.EnumValue(name, 'net_fhost_inactive', -402)
        self.netfhost = PL1.EnumValue(name, 'netfhost', -402)
        self.net_fimp_down = PL1.EnumValue(name, 'net_fimp_down', -403)
        self.fimpdwn = PL1.EnumValue(name, 'fimpdwn', -403)
        self.net_icp_bad_state = PL1.EnumValue(name, 'net_icp_bad_state', -404)
        self.bad_icp = PL1.EnumValue(name, 'bad_icp', -404)
        self.net_icp_error = PL1.EnumValue(name, 'net_icp_error', -405)
        self.icp_err = PL1.EnumValue(name, 'icp_err', -405)
        self.net_icp_not_concluded = PL1.EnumValue(name, 'net_icp_not_concluded', -406)
        self.stillicp = PL1.EnumValue(name, 'stillicp', -406)
        self.net_invalid_state = PL1.EnumValue(name, 'net_invalid_state', -407)
        self.netstate = PL1.EnumValue(name, 'netstate', -407)
        self.net_no_connect_permission = PL1.EnumValue(name, 'net_no_connect_permission', -408)
        self.noconect = PL1.EnumValue(name, 'noconect', -408)
        self.net_no_icp = PL1.EnumValue(name, 'net_no_icp', -409)
        self.no_icp = PL1.EnumValue(name, 'no_icp', -409)
        self.net_not_up = PL1.EnumValue(name, 'net_not_up', -410)
        self.netnotup = PL1.EnumValue(name, 'netnotup', -410)
        self.net_rfc_refused = PL1.EnumValue(name, 'net_rfc_refused', -411)
        self.refused = PL1.EnumValue(name, 'refused', -411)
        self.net_socket_closed = PL1.EnumValue(name, 'net_socket_closed', -412)
        self.netclose = PL1.EnumValue(name, 'netclose', -412)
        self.net_socket_not_found = PL1.EnumValue(name, 'net_socket_not_found', -413)
        self.netsockf = PL1.EnumValue(name, 'netsockf', -413)
        self.net_table_space = PL1.EnumValue(name, 'net_table_space', -414)
        self.nettblsp = PL1.EnumValue(name, 'nettblsp', -414)
        self.net_timeout = PL1.EnumValue(name, 'net_timeout', -415)
        self.nettime = PL1.EnumValue(name, 'nettime', -415)
        self.new_offset_negative = PL1.EnumValue(name, 'new_offset_negative', -416)
        self.newofneg = PL1.EnumValue(name, 'newofneg', -416)
        self.new_search_list = PL1.EnumValue(name, 'new_search_list', -417)
        self.new_sl = PL1.EnumValue(name, 'new_sl', -417)
        self.newnamerr = PL1.EnumValue(name, 'newnamerr', -418)
        self.newname = PL1.EnumValue(name, 'newname', -418)
        self.nine_mode_parity = PL1.EnumValue(name, 'nine_mode_parity', -419)
        self.par9md = PL1.EnumValue(name, 'par9md', -419)
        self.no_a_permission = PL1.EnumValue(name, 'no_a_permission', -420)
        self.no_a = PL1.EnumValue(name, 'no_a', -420)
        self.no_append = PL1.EnumValue(name, 'no_append', -421)
        self.noappend = PL1.EnumValue(name, 'noappend', -421)
        self.no_appropriate_device = PL1.EnumValue(name, 'no_appropriate_device', -422)
        self.noappdev = PL1.EnumValue(name, 'noappdev', -422)
        self.no_archive_for_equal = PL1.EnumValue(name, 'no_archive_for_equal', -423)
        self.noaceql = PL1.EnumValue(name, 'noaceql', -423)
        self.no_backspace = PL1.EnumValue(name, 'no_backspace', -424)
        self.nobacksp = PL1.EnumValue(name, 'nobacksp', -424)
        self.no_base_chnl_active = PL1.EnumValue(name, 'no_base_chnl_active', -425)
        self.nobaschn = PL1.EnumValue(name, 'nobaschn', -425)
        self.no_channel_meters = PL1.EnumValue(name, 'no_channel_meters', -426)
        self.nochanm = PL1.EnumValue(name, 'nochanm', -426)
        self.no_component = PL1.EnumValue(name, 'no_component', -427)
        self.no_comp = PL1.EnumValue(name, 'no_comp', -427)
        self.no_connection = PL1.EnumValue(name, 'no_connection', -428)
        self.noconect = PL1.EnumValue(name, 'noconect', -428)
        self.no_cpus_online = PL1.EnumValue(name, 'no_cpus_online', -429)
        self.nocpus = PL1.EnumValue(name, 'nocpus', -429)
        self.no_create_copy = PL1.EnumValue(name, 'no_create_copy', -430)
        self.nocreate = PL1.EnumValue(name, 'nocreate', -430)
        self.no_current_record = PL1.EnumValue(name, 'no_current_record', -431)
        self.nocurrec = PL1.EnumValue(name, 'nocurrec', -431)
        self.no_defs = PL1.EnumValue(name, 'no_defs', -432)
        self.nolkdefs = PL1.EnumValue(name, 'nolkdefs', -432)
        self.no_delimiter = PL1.EnumValue(name, 'no_delimiter', -433)
        self.nodelim = PL1.EnumValue(name, 'nodelim', -433)
        self.no_device = PL1.EnumValue(name, 'no_device', -434)
        self.nodevice = PL1.EnumValue(name, 'nodevice', -434)
        self.no_dialok = PL1.EnumValue(name, 'no_dialok', -435)
        self.NOTdialok = PL1.EnumValue(name, 'NOTdialok', -435)
        self.no_dir = PL1.EnumValue(name, 'no_dir', -436)
        self.noaccess = PL1.EnumValue(name, 'noaccess', -436)
        self.nodir = PL1.EnumValue(name, 'nodir', -436)
        self.no_disconnected_processes = PL1.EnumValue(name, 'no_disconnected_processes', -437)
        self.nodiscpr = PL1.EnumValue(name, 'nodiscpr', -437)
        self.no_e_permission = PL1.EnumValue(name, 'no_e_permission', -438)
        self.no_e = PL1.EnumValue(name, 'no_e', -438)
        self.no_ext_sym = PL1.EnumValue(name, 'no_ext_sym', -439)
        self.noextsym = PL1.EnumValue(name, 'noextsym', -439)
        self.no_file = PL1.EnumValue(name, 'no_file', -440)
        self.no_file = PL1.EnumValue(name, 'no_file', -440)
        self.no_fim_flag = PL1.EnumValue(name, 'no_fim_flag', -441)
        self.nofmflg = PL1.EnumValue(name, 'nofmflg', -441)
        self.no_handler = PL1.EnumValue(name, 'no_handler', -442)
        self.nohand = PL1.EnumValue(name, 'nohand', -442)
        self.no_heap_defined = PL1.EnumValue(name, 'no_heap_defined', -443)
        self.nohpdef = PL1.EnumValue(name, 'nohpdef', -443)
        self.no_heap_sym = PL1.EnumValue(name, 'no_heap_sym', -444)
        self.nohpsym = PL1.EnumValue(name, 'nohpsym', -444)
        self.no_info = PL1.EnumValue(name, 'no_info', -445)
        self.noinfo = PL1.EnumValue(name, 'noinfo', -445)
        self.no_initial_string = PL1.EnumValue(name, 'no_initial_string', -446)
        self.no_istr = PL1.EnumValue(name, 'no_istr', -446)
        self.no_io_interrupt = PL1.EnumValue(name, 'no_io_interrupt', -447)
        self.noiointr = PL1.EnumValue(name, 'noiointr', -447)
        self.no_io_page_tables = PL1.EnumValue(name, 'no_io_page_tables', -448)
        self.noiopts = PL1.EnumValue(name, 'noiopts', -448)
        self.no_iocb = PL1.EnumValue(name, 'no_iocb', -449)
        self.no_iocb = PL1.EnumValue(name, 'no_iocb', -449)
        self.no_journals_free = PL1.EnumValue(name, 'no_journals_free', -450)
        self.nojrfree = PL1.EnumValue(name, 'nojrfree', -450)
        self.no_key = PL1.EnumValue(name, 'no_key', -451)
        self.no_key = PL1.EnumValue(name, 'no_key', -451)
        self.no_label = PL1.EnumValue(name, 'no_label', -452)
        self.no_label = PL1.EnumValue(name, 'no_label', -452)
        self.no_line_status = PL1.EnumValue(name, 'no_line_status', -453)
        self.nolinstt = PL1.EnumValue(name, 'nolinstt', -453)
        self.no_linkage = PL1.EnumValue(name, 'no_linkage', -454)
        self.nolksect = PL1.EnumValue(name, 'nolksect', -454)
        self.no_log_message = PL1.EnumValue(name, 'no_log_message', -455)
        self.lognomsg = PL1.EnumValue(name, 'lognomsg', -455)
        self.no_m_permission = PL1.EnumValue(name, 'no_m_permission', -456)
        self.no_m = PL1.EnumValue(name, 'no_m', -456)
        self.no_makeknown = PL1.EnumValue(name, 'no_makeknown', -457)
        self.nomkknwn = PL1.EnumValue(name, 'nomkknwn', -457)
        self.no_memory_for_scavenge = PL1.EnumValue(name, 'no_memory_for_scavenge', -458)
        self.nomemsc = PL1.EnumValue(name, 'nomemsc', -458)
        self.no_message = PL1.EnumValue(name, 'no_message', -459)
        self.nomsg = PL1.EnumValue(name, 'nomsg', -459)
        self.no_move = PL1.EnumValue(name, 'no_move', -460)
        self.no_move = PL1.EnumValue(name, 'no_move', -460)
        self.no_next_volume = PL1.EnumValue(name, 'no_next_volume', -461)
        self.nonxtvol = PL1.EnumValue(name, 'nonxtvol', -461)
        self.no_null_refnames = PL1.EnumValue(name, 'no_null_refnames', -462)
        self.nonullrf = PL1.EnumValue(name, 'nonullrf', -462)
        self.no_odd_areas = PL1.EnumValue(name, 'no_odd_areas', -463)
        self.no_odd = PL1.EnumValue(name, 'no_odd', -463)
        self.no_operation = PL1.EnumValue(name, 'no_operation', -464)
        self.no_oper = PL1.EnumValue(name, 'no_oper', -464)
        self.no_r_permission = PL1.EnumValue(name, 'no_r_permission', -465)
        self.no_r = PL1.EnumValue(name, 'no_r', -465)
        self.no_record = PL1.EnumValue(name, 'no_record', -466)
        self.no_rec = PL1.EnumValue(name, 'no_rec', -466)
        self.no_restart = PL1.EnumValue(name, 'no_restart', -467)
        self.norestrt = PL1.EnumValue(name, 'norestrt', -467)
        self.no_room_for_dsb = PL1.EnumValue(name, 'no_room_for_dsb', -468)
        self.nrmdsb = PL1.EnumValue(name, 'nrmdsb', -468)
        self.no_room_for_lock = PL1.EnumValue(name, 'no_room_for_lock', -469)
        self.cantlock = PL1.EnumValue(name, 'cantlock', -469)
        self.no_s_permission = PL1.EnumValue(name, 'no_s_permission', -470)
        self.no_s = PL1.EnumValue(name, 'no_s', -470)
        self.no_search_list = PL1.EnumValue(name, 'no_search_list', -471)
        self.nosrls = PL1.EnumValue(name, 'nosrls', -471)
        self.no_search_list_default = PL1.EnumValue(name, 'no_search_list_default', -472)
        self.no_sldef = PL1.EnumValue(name, 'no_sldef', -472)
        self.no_set_btcnt = PL1.EnumValue(name, 'no_set_btcnt', -473)
        self.nosetbc = PL1.EnumValue(name, 'nosetbc', -473)
        self.no_stmt_delim = PL1.EnumValue(name, 'no_stmt_delim', -474)
        self.no_delim = PL1.EnumValue(name, 'no_delim', -474)
        self.no_table = PL1.EnumValue(name, 'no_table', -475)
        self.no_table = PL1.EnumValue(name, 'no_table', -475)
        self.no_term_type = PL1.EnumValue(name, 'no_term_type', -476)
        self.notrmtyp = PL1.EnumValue(name, 'notrmtyp', -476)
        self.no_terminal_quota = PL1.EnumValue(name, 'no_terminal_quota', -477)
        self.notrmq = PL1.EnumValue(name, 'notrmq', -477)
        self.no_trap_proc = PL1.EnumValue(name, 'no_trap_proc', -478)
        self.notrproc = PL1.EnumValue(name, 'notrproc', -478)
        self.no_vla_support = PL1.EnumValue(name, 'no_vla_support', -479)
        self.novlasup = PL1.EnumValue(name, 'novlasup', -479)
        self.no_w_permission = PL1.EnumValue(name, 'no_w_permission', -480)
        self.no_w = PL1.EnumValue(name, 'no_w', -480)
        self.no_wdir = PL1.EnumValue(name, 'no_wdir', -481)
        self.no_wdir = PL1.EnumValue(name, 'no_wdir', -481)
        self.no_wired_structure = PL1.EnumValue(name, 'no_wired_structure', -482)
        self.nowirebf = PL1.EnumValue(name, 'nowirebf', -482)
        self.noalloc = PL1.EnumValue(name, 'noalloc', -483)
        self.noarg = PL1.EnumValue(name, 'noarg', -484)
        self.nodescr = PL1.EnumValue(name, 'nodescr', -485)
        self.noentry = PL1.EnumValue(name, 'noentry', -486)
        self.nolinkag = PL1.EnumValue(name, 'nolinkag', -487)
        self.nolot = PL1.EnumValue(name, 'nolot', -488)
        self.nomatch = PL1.EnumValue(name, 'nomatch', -489)
        self.non_matching_uid = PL1.EnumValue(name, 'non_matching_uid', -490)
        self.bad_uid = PL1.EnumValue(name, 'bad_uid', -490)
        self.nonamerr = PL1.EnumValue(name, 'nonamerr', -491)
        self.noname = PL1.EnumValue(name, 'noname', -491)
        self.nondirseg = PL1.EnumValue(name, 'nondirseg', -492)
        self.ndirseg = PL1.EnumValue(name, 'ndirseg', -492)
        self.nopart = PL1.EnumValue(name, 'nopart', -493)
        self.nopart = PL1.EnumValue(name, 'nopart', -493)
        self.noprtdmp = PL1.EnumValue(name, 'noprtdmp', -494)
        self.nostars = PL1.EnumValue(name, 'nostars', -495)
        self.nostars = PL1.EnumValue(name, 'nostars', -495)
        self.not_a_branch = PL1.EnumValue(name, 'not_a_branch', -496)
        self.notbrnch = PL1.EnumValue(name, 'notbrnch', -496)
        self.not_a_valid_iocb = PL1.EnumValue(name, 'not_a_valid_iocb', -497)
        self.badiocb = PL1.EnumValue(name, 'badiocb', -497)
        self.not_a_wait_channel = PL1.EnumValue(name, 'not_a_wait_channel', -498)
        self.notwait = PL1.EnumValue(name, 'notwait', -498)
        self.not_abs_path = PL1.EnumValue(name, 'not_abs_path', -499)
        self.NOTabspath = PL1.EnumValue(name, 'NOTabspath', -499)
        self.not_act_fnc = PL1.EnumValue(name, 'not_act_fnc', -500)
        self.not_af = PL1.EnumValue(name, 'not_af', -500)
        self.not_archive = PL1.EnumValue(name, 'not_archive', -501)
        self.not_arch = PL1.EnumValue(name, 'not_arch', -501)
        self.not_attached = PL1.EnumValue(name, 'not_attached', -502)
        self.notattch = PL1.EnumValue(name, 'notattch', -502)
        self.not_base_channel = PL1.EnumValue(name, 'not_base_channel', -503)
        self.not_base = PL1.EnumValue(name, 'not_base', -503)
        self.not_bound = PL1.EnumValue(name, 'not_bound', -504)
        self.notbound = PL1.EnumValue(name, 'notbound', -504)
        self.not_closed = PL1.EnumValue(name, 'not_closed', -505)
        self.not_clsd = PL1.EnumValue(name, 'not_clsd', -505)
        self.not_detached = PL1.EnumValue(name, 'not_detached', -506)
        self.not_det = PL1.EnumValue(name, 'not_det', -506)
        self.not_dm_ring = PL1.EnumValue(name, 'not_dm_ring', -507)
        self.notdmrg = PL1.EnumValue(name, 'notdmrg', -507)
        self.not_done = PL1.EnumValue(name, 'not_done', -508)
        self.not_done = PL1.EnumValue(name, 'not_done', -508)
        self.not_in_trace_table = PL1.EnumValue(name, 'not_in_trace_table', -509)
        self.notintbl = PL1.EnumValue(name, 'notintbl', -509)
        self.not_initialized = PL1.EnumValue(name, 'not_initialized', -510)
        self.notinit = PL1.EnumValue(name, 'notinit', -510)
        self.not_link = PL1.EnumValue(name, 'not_link', -511)
        self.NOTlink = PL1.EnumValue(name, 'NOTlink', -511)
        self.not_open = PL1.EnumValue(name, 'not_open', -512)
        self.not_open = PL1.EnumValue(name, 'not_open', -512)
        self.not_own_message = PL1.EnumValue(name, 'not_own_message', -513)
        self.NOTownmsg = PL1.EnumValue(name, 'NOTownmsg', -513)
        self.not_privileged = PL1.EnumValue(name, 'not_privileged', -514)
        self.not_priv = PL1.EnumValue(name, 'not_priv', -514)
        self.not_ring_0 = PL1.EnumValue(name, 'not_ring_0', -515)
        self.norng0 = PL1.EnumValue(name, 'norng0', -515)
        self.not_seg_type = PL1.EnumValue(name, 'not_seg_type', -516)
        self.notsegt = PL1.EnumValue(name, 'notsegt', -516)
        self.notadir = PL1.EnumValue(name, 'notadir', -517)
        self.notalloc = PL1.EnumValue(name, 'notalloc', -518)
        self.nrmkst = PL1.EnumValue(name, 'nrmkst', -519)
        self.null_brackets = PL1.EnumValue(name, 'null_brackets', -520)
        self.nulbrack = PL1.EnumValue(name, 'nulbrack', -520)
        self.null_dir = PL1.EnumValue(name, 'null_dir', -521)
        self.nulldir = PL1.EnumValue(name, 'nulldir', -521)
        self.null_info_ptr = PL1.EnumValue(name, 'null_info_ptr', -522)
        self.noinfopt = PL1.EnumValue(name, 'noinfopt', -522)
        self.null_name_component = PL1.EnumValue(name, 'null_name_component', -523)
        self.nullcomp = PL1.EnumValue(name, 'nullcomp', -523)
        self.obsolete_function = PL1.EnumValue(name, 'obsolete_function', -524)
        self.obsfnc = PL1.EnumValue(name, 'obsfnc', -524)
        self.odd_no_of_args = PL1.EnumValue(name, 'odd_no_of_args', -525)
        self.odd_arg = PL1.EnumValue(name, 'odd_arg', -525)
        self.old_dim = PL1.EnumValue(name, 'old_dim', -526)
        self.old_dim = PL1.EnumValue(name, 'old_dim', -526)
        self.oldnamerr = PL1.EnumValue(name, 'oldnamerr', -527)
        self.oldname = PL1.EnumValue(name, 'oldname', -527)
        self.oldobj = PL1.EnumValue(name, 'oldobj', -528)
        self.oob_stack = PL1.EnumValue(name, 'oob_stack', -529)
        self.oobstk = PL1.EnumValue(name, 'oobstk', -529)
        self.oob_stack_ref = PL1.EnumValue(name, 'oob_stack_ref', -530)
        self.oobstkrf = PL1.EnumValue(name, 'oobstkrf', -530)
        self.oosw = PL1.EnumValue(name, 'oosw', -531)
        self.oosrv = PL1.EnumValue(name, 'oosrv', -531)
        self.order_error = PL1.EnumValue(name, 'order_error', -532)
        self.ordererr = PL1.EnumValue(name, 'ordererr', -532)
        self.out_of_bounds = PL1.EnumValue(name, 'out_of_bounds', -533)
        self.oob = PL1.EnumValue(name, 'oob', -533)
        self.out_of_main_memory = PL1.EnumValue(name, 'out_of_main_memory', -534)
        self.outofmem = PL1.EnumValue(name, 'outofmem', -534)
        self.out_of_sequence = PL1.EnumValue(name, 'out_of_sequence', -535)
        self.outofseq = PL1.EnumValue(name, 'outofseq', -535)
        self.out_of_window = PL1.EnumValue(name, 'out_of_window', -536)
        self.oowndow = PL1.EnumValue(name, 'oowndow', -536)
        self.outward_call_failed = PL1.EnumValue(name, 'outward_call_failed', -537)
        self.NOToutcall = PL1.EnumValue(name, 'NOToutcall', -537)
        self.overlapping_more_responses = PL1.EnumValue(name, 'overlapping_more_responses', -538)
        self.badmore = PL1.EnumValue(name, 'badmore', -538)
        self.pathlong = PL1.EnumValue(name, 'pathlong', -539)
        self.picture_bad = PL1.EnumValue(name, 'picture_bad', -540)
        self.picbad = PL1.EnumValue(name, 'picbad', -540)
        self.picture_scale = PL1.EnumValue(name, 'picture_scale', -541)
        self.picscl = PL1.EnumValue(name, 'picscl', -541)
        self.picture_too_big = PL1.EnumValue(name, 'picture_too_big', -542)
        self.picbig = PL1.EnumValue(name, 'picbig', -542)
        self.positioned_on_bot = PL1.EnumValue(name, 'positioned_on_bot', -543)
        self.ponbot = PL1.EnumValue(name, 'ponbot', -543)
        self.private_volume = PL1.EnumValue(name, 'private_volume', -544)
        self.lvprivat = PL1.EnumValue(name, 'lvprivat', -544)
        self.process_stopped = PL1.EnumValue(name, 'process_stopped', -545)
        self.procstop = PL1.EnumValue(name, 'procstop', -545)
        self.process_unknown = PL1.EnumValue(name, 'process_unknown', -546)
        self.procunkn = PL1.EnumValue(name, 'procunkn', -546)
        self.proj_not_found = PL1.EnumValue(name, 'proj_not_found', -547)
        self.no_proj = PL1.EnumValue(name, 'no_proj', -547)
        self.pv_is_in_lv = PL1.EnumValue(name, 'pv_is_in_lv', -548)
        self.PV_in_LV = PL1.EnumValue(name, 'PV_in_LV', -548)
        self.pv_no_scavenge = PL1.EnumValue(name, 'pv_no_scavenge', -549)
        self.pvnosc = PL1.EnumValue(name, 'pvnosc', -549)
        self.pvid_not_found = PL1.EnumValue(name, 'pvid_not_found', -550)
        self.pvntfnd = PL1.EnumValue(name, 'pvntfnd', -550)
        self.quit_term_abort = PL1.EnumValue(name, 'quit_term_abort', -551)
        self.qtabt = PL1.EnumValue(name, 'qtabt', -551)
        self.r0_refname = PL1.EnumValue(name, 'r0_refname', -552)
        self.r0refnam = PL1.EnumValue(name, 'r0refnam', -552)
        self.rcp_attr_not_permitted = PL1.EnumValue(name, 'rcp_attr_not_permitted', -553)
        self.attrNOTpmt = PL1.EnumValue(name, 'attrNOTpmt', -553)
        self.rcp_attr_protected = PL1.EnumValue(name, 'rcp_attr_protected', -554)
        self.prot_att = PL1.EnumValue(name, 'prot_att', -554)
        self.rcp_bad_attributes = PL1.EnumValue(name, 'rcp_bad_attributes', -555)
        self.rcpxatts = PL1.EnumValue(name, 'rcpxatts', -555)
        self.rcp_missing_registry_component = PL1.EnumValue(name, 'rcp_missing_registry_component', -556)
        self.rcprgcmp = PL1.EnumValue(name, 'rcprgcmp', -556)
        self.rcp_no_auto_reg = PL1.EnumValue(name, 'rcp_no_auto_reg', -557)
        self.NOTautoreg = PL1.EnumValue(name, 'NOTautoreg', -557)
        self.rcp_no_registry = PL1.EnumValue(name, 'rcp_no_registry', -558)
        self.norgstry = PL1.EnumValue(name, 'norgstry', -558)
        self.record_busy = PL1.EnumValue(name, 'record_busy', -559)
        self.recbusy = PL1.EnumValue(name, 'recbusy', -559)
        self.recoverable_error = PL1.EnumValue(name, 'recoverable_error', -560)
        self.recoverr = PL1.EnumValue(name, 'recoverr', -560)
        self.recursion_error = PL1.EnumValue(name, 'recursion_error', -561)
        self.recurerr = PL1.EnumValue(name, 'recurerr', -561)
        self.refname_count_too_big = PL1.EnumValue(name, 'refname_count_too_big', -562)
        self.rcnt_big = PL1.EnumValue(name, 'rcnt_big', -562)
        self.regexp_invalid_star = PL1.EnumValue(name, 'regexp_invalid_star', -563)
        self.rgxpinvs = PL1.EnumValue(name, 'rgxpinvs', -563)
        self.regexp_too_complex = PL1.EnumValue(name, 'regexp_too_complex', -564)
        self.rgxpcplx = PL1.EnumValue(name, 'rgxpcplx', -564)
        self.regexp_too_long = PL1.EnumValue(name, 'regexp_too_long', -565)
        self.rgxplong = PL1.EnumValue(name, 'rgxplong', -565)
        self.regexp_undefined = PL1.EnumValue(name, 'regexp_undefined', -566)
        self.rgxpundf = PL1.EnumValue(name, 'rgxpundf', -566)
        self.rel_chnl_active = PL1.EnumValue(name, 'rel_chnl_active', -567)
        self.rchnact = PL1.EnumValue(name, 'rchnact', -567)
        self.request_id_ambiguous = PL1.EnumValue(name, 'request_id_ambiguous', -568)
        self.reqidamb = PL1.EnumValue(name, 'reqidamb', -568)
        self.request_not_recognized = PL1.EnumValue(name, 'request_not_recognized', -569)
        self.reqnorec = PL1.EnumValue(name, 'reqnorec', -569)
        self.request_pending = PL1.EnumValue(name, 'request_pending', -570)
        self.reqpend = PL1.EnumValue(name, 'reqpend', -570)
        self.reservation_failed = PL1.EnumValue(name, 'reservation_failed', -571)
        self.resbad = PL1.EnumValue(name, 'resbad', -571)
        self.resource_assigned = PL1.EnumValue(name, 'resource_assigned', -572)
        self.rassnd = PL1.EnumValue(name, 'rassnd', -572)
        self.resource_attached = PL1.EnumValue(name, 'resource_attached', -573)
        self.rattchd = PL1.EnumValue(name, 'rattchd', -573)
        self.resource_awaiting_clear = PL1.EnumValue(name, 'resource_awaiting_clear', -574)
        self.rsawclr = PL1.EnumValue(name, 'rsawclr', -574)
        self.resource_bad_access = PL1.EnumValue(name, 'resource_bad_access', -575)
        self.rbadacc = PL1.EnumValue(name, 'rbadacc', -575)
        self.resource_free = PL1.EnumValue(name, 'resource_free', -576)
        self.rsc_free = PL1.EnumValue(name, 'rsc_free', -576)
        self.resource_locked = PL1.EnumValue(name, 'resource_locked', -577)
        self.rsc_lock = PL1.EnumValue(name, 'rsc_lock', -577)
        self.resource_not_free = PL1.EnumValue(name, 'resource_not_free', -578)
        self.not_free = PL1.EnumValue(name, 'not_free', -578)
        self.resource_not_modified = PL1.EnumValue(name, 'resource_not_modified', -579)
        self.rscNOTmodf = PL1.EnumValue(name, 'rscNOTmodf', -579)
        self.resource_reserved = PL1.EnumValue(name, 'resource_reserved', -580)
        self.rresvd = PL1.EnumValue(name, 'rresvd', -580)
        self.resource_spec_ambiguous = PL1.EnumValue(name, 'resource_spec_ambiguous', -581)
        self.rscambig = PL1.EnumValue(name, 'rscambig', -581)
        self.resource_type_inappropriate = PL1.EnumValue(name, 'resource_type_inappropriate', -582)
        self.rcpinapp = PL1.EnumValue(name, 'rcpinapp', -582)
        self.resource_type_unknown = PL1.EnumValue(name, 'resource_type_unknown', -583)
        self.unkrsctp = PL1.EnumValue(name, 'unkrsctp', -583)
        self.resource_unassigned = PL1.EnumValue(name, 'resource_unassigned', -584)
        self.runasnd = PL1.EnumValue(name, 'runasnd', -584)
        self.resource_unavailable = PL1.EnumValue(name, 'resource_unavailable', -585)
        self.runavail = PL1.EnumValue(name, 'runavail', -585)
        self.resource_unknown = PL1.EnumValue(name, 'resource_unknown', -586)
        self.runknown = PL1.EnumValue(name, 'runknown', -586)
        self.retrieval_trap_on = PL1.EnumValue(name, 'retrieval_trap_on', -587)
        self.retrap = PL1.EnumValue(name, 'retrap', -587)
        self.root = PL1.EnumValue(name, 'root', -588)
        self.rqover = PL1.EnumValue(name, 'rqover', -589)
        self.run_unit_not_recursive = PL1.EnumValue(name, 'run_unit_not_recursive', -590)
        self.norunrec = PL1.EnumValue(name, 'norunrec', -590)
        self.safety_sw_on = PL1.EnumValue(name, 'safety_sw_on', -591)
        self.sson = PL1.EnumValue(name, 'sson', -591)
        self.salv_pdir_procterm = PL1.EnumValue(name, 'salv_pdir_procterm', -592)
        self.salvptrm = PL1.EnumValue(name, 'salvptrm', -592)
        self.sameseg = PL1.EnumValue(name, 'sameseg', -593)
        self.scavenge_aborted = PL1.EnumValue(name, 'scavenge_aborted', -594)
        self.scabrt = PL1.EnumValue(name, 'scabrt', -594)
        self.scavenge_in_progress = PL1.EnumValue(name, 'scavenge_in_progress', -595)
        self.scinprg = PL1.EnumValue(name, 'scinprg', -595)
        self.scavenge_process_limit = PL1.EnumValue(name, 'scavenge_process_limit', -596)
        self.scprlmt = PL1.EnumValue(name, 'scprlmt', -596)
        self.seg_deleted = PL1.EnumValue(name, 'seg_deleted', -597)
        self.segdel = PL1.EnumValue(name, 'segdel', -597)
        self.seg_not_found = PL1.EnumValue(name, 'seg_not_found', -598)
        self.segntfnd = PL1.EnumValue(name, 'segntfnd', -598)
        self.seg_unknown = PL1.EnumValue(name, 'seg_unknown', -599)
        self.notknown = PL1.EnumValue(name, 'notknown', -599)
        self.segfault = PL1.EnumValue(name, 'segfault', -600)
        self.segknown = PL1.EnumValue(name, 'segknown', -601)
        self.seglock = PL1.EnumValue(name, 'seglock', -602)
        self.segnamedup = PL1.EnumValue(name, 'segnamedup', -603)
        self.segnamdp = PL1.EnumValue(name, 'segnamdp', -603)
        self.segno_in_use = PL1.EnumValue(name, 'segno_in_use', -604)
        self.seginuse = PL1.EnumValue(name, 'seginuse', -604)
        self.short_record = PL1.EnumValue(name, 'short_record', -605)
        self.shortrec = PL1.EnumValue(name, 'shortrec', -605)
        self.signaller_fault = PL1.EnumValue(name, 'signaller_fault', -606)
        self.sigflt = PL1.EnumValue(name, 'sigflt', -606)
        self.size_error = PL1.EnumValue(name, 'size_error', -607)
        self.sizeerr = PL1.EnumValue(name, 'sizeerr', -607)
        self.smallarg = PL1.EnumValue(name, 'smallarg', -608)
        self.soos_set = PL1.EnumValue(name, 'soos_set', -609)
        self.special_channel = PL1.EnumValue(name, 'special_channel', -610)
        self.spechan = PL1.EnumValue(name, 'spechan', -610)
        self.special_channels_full = PL1.EnumValue(name, 'special_channels_full', -611)
        self.chnsfull = PL1.EnumValue(name, 'chnsfull', -611)
        self.stack_not_active = PL1.EnumValue(name, 'stack_not_active', -612)
        self.stkinact = PL1.EnumValue(name, 'stkinact', -612)
        self.stack_overflow = PL1.EnumValue(name, 'stack_overflow', -613)
        self.stkovrfl = PL1.EnumValue(name, 'stkovrfl', -613)
        self.strings_not_equal = PL1.EnumValue(name, 'strings_not_equal', -614)
        self.stringNE = PL1.EnumValue(name, 'stringNE', -614)
        self.subvol_needed = PL1.EnumValue(name, 'subvol_needed', -615)
        self.subvn = PL1.EnumValue(name, 'subvn', -615)
        self.subvol_invalid = PL1.EnumValue(name, 'subvol_invalid', -616)
        self.subinv = PL1.EnumValue(name, 'subinv', -616)
        self.synch_seg_limit = PL1.EnumValue(name, 'synch_seg_limit', -617)
        self.synchlim = PL1.EnumValue(name, 'synchlim', -617)
        self.synch_seg_segmove = PL1.EnumValue(name, 'synch_seg_segmove', -618)
        self.synchsgm = PL1.EnumValue(name, 'synchsgm', -618)
        self.tape_error = PL1.EnumValue(name, 'tape_error', -619)
        self.tape_err = PL1.EnumValue(name, 'tape_err', -619)
        self.termination_requested = PL1.EnumValue(name, 'termination_requested', -620)
        self.termrqu = PL1.EnumValue(name, 'termrqu', -620)
        self.time_too_long = PL1.EnumValue(name, 'time_too_long', -621)
        self.timelong = PL1.EnumValue(name, 'timelong', -621)
        self.timeout = PL1.EnumValue(name, 'timeout', -622)
        self.too_many_acl_entries = PL1.EnumValue(name, 'too_many_acl_entries', -623)
        self.manyacle = PL1.EnumValue(name, 'manyacle', -623)
        self.too_many_args = PL1.EnumValue(name, 'too_many_args', -624)
        self.t_m_args = PL1.EnumValue(name, 't_m_args', -624)
        self.too_many_buffers = PL1.EnumValue(name, 'too_many_buffers', -625)
        self.manybufs = PL1.EnumValue(name, 'manybufs', -625)
        self.too_many_names = PL1.EnumValue(name, 'too_many_names', -626)
        self.GTnames = PL1.EnumValue(name, 'GTnames', -626)
        self.too_many_read_delimiters = PL1.EnumValue(name, 'too_many_read_delimiters', -627)
        self.tmrdelim = PL1.EnumValue(name, 'tmrdelim', -627)
        self.too_many_refs = PL1.EnumValue(name, 'too_many_refs', -628)
        self.manyrefs = PL1.EnumValue(name, 'manyrefs', -628)
        self.too_many_sr = PL1.EnumValue(name, 'too_many_sr', -629)
        self.toomnysr = PL1.EnumValue(name, 'toomnysr', -629)
        self.too_many_tokens = PL1.EnumValue(name, 'too_many_tokens', -630)
        self.numtoken = PL1.EnumValue(name, 'numtoken', -630)
        self.toomanylinks = PL1.EnumValue(name, 'toomanylinks', -631)
        self.GTlinks = PL1.EnumValue(name, 'GTlinks', -631)
        self.trace_table_empty = PL1.EnumValue(name, 'trace_table_empty', -632)
        self.emptytbl = PL1.EnumValue(name, 'emptytbl', -632)
        self.trace_table_full = PL1.EnumValue(name, 'trace_table_full', -633)
        self.fulltbl = PL1.EnumValue(name, 'fulltbl', -633)
        self.translation_aborted = PL1.EnumValue(name, 'translation_aborted', -634)
        self.tranabor = PL1.EnumValue(name, 'tranabor', -634)
        self.translation_failed = PL1.EnumValue(name, 'translation_failed', -635)
        self.tranfail = PL1.EnumValue(name, 'tranfail', -635)
        self.typename_not_found = PL1.EnumValue(name, 'typename_not_found', -636)
        self.typenfnd = PL1.EnumValue(name, 'typenfnd', -636)
        self.unable_to_check_access = PL1.EnumValue(name, 'unable_to_check_access', -637)
        self.cantchk = PL1.EnumValue(name, 'cantchk', -637)
        self.unable_to_do_io = PL1.EnumValue(name, 'unable_to_do_io', -638)
        self.no_io = PL1.EnumValue(name, 'no_io', -638)
        self.unbalanced_brackets = PL1.EnumValue(name, 'unbalanced_brackets', -639)
        self.unbalbra = PL1.EnumValue(name, 'unbalbra', -639)
        self.unbalanced_parentheses = PL1.EnumValue(name, 'unbalanced_parentheses', -640)
        self.unbalpar = PL1.EnumValue(name, 'unbalpar', -640)
        self.unbalanced_quotes = PL1.EnumValue(name, 'unbalanced_quotes', -641)
        self.unbalquo = PL1.EnumValue(name, 'unbalquo', -641)
        self.undefined_mode = PL1.EnumValue(name, 'undefined_mode', -642)
        self.undefmod = PL1.EnumValue(name, 'undefmod', -642)
        self.undefined_order_request = PL1.EnumValue(name, 'undefined_order_request', -643)
        self.undorder = PL1.EnumValue(name, 'undorder', -643)
        self.undefined_ptrname = PL1.EnumValue(name, 'undefined_ptrname', -644)
        self.undptnam = PL1.EnumValue(name, 'undptnam', -644)
        self.undeleted_device = PL1.EnumValue(name, 'undeleted_device', -645)
        self.undeldev = PL1.EnumValue(name, 'undeldev', -645)
        self.unexpected_condition = PL1.EnumValue(name, 'unexpected_condition', -646)
        self.exexpcon = PL1.EnumValue(name, 'exexpcon', -646)
        self.unexpected_device_status = PL1.EnumValue(name, 'unexpected_device_status', -647)
        self.unxpstat = PL1.EnumValue(name, 'unxpstat', -647)
        self.unexpected_ft2 = PL1.EnumValue(name, 'unexpected_ft2', -648)
        self.unexpft2 = PL1.EnumValue(name, 'unexpft2', -648)
        self.unexpired_file = PL1.EnumValue(name, 'unexpired_file', -649)
        self.unexpfl = PL1.EnumValue(name, 'unexpfl', -649)
        self.unexpired_volume = PL1.EnumValue(name, 'unexpired_volume', -650)
        self.unexpvl = PL1.EnumValue(name, 'unexpvl', -650)
        self.unimplemented_ptrname = PL1.EnumValue(name, 'unimplemented_ptrname', -651)
        self.unimptnm = PL1.EnumValue(name, 'unimptnm', -651)
        self.unimplemented_version = PL1.EnumValue(name, 'unimplemented_version', -652)
        self.not_imp = PL1.EnumValue(name, 'not_imp', -652)
        self.uninitialized_volume = PL1.EnumValue(name, 'uninitialized_volume', -653)
        self.uninitvl = PL1.EnumValue(name, 'uninitvl', -653)
        self.unknown_tp = PL1.EnumValue(name, 'unknown_tp', -654)
        self.bad_tp = PL1.EnumValue(name, 'bad_tp', -654)
        self.unknown_zone = PL1.EnumValue(name, 'unknown_zone', -655)
        self.bad_zone = PL1.EnumValue(name, 'bad_zone', -655)
        self.unrecognized_char_code = PL1.EnumValue(name, 'unrecognized_char_code', -656)
        self.urecgcc = PL1.EnumValue(name, 'urecgcc', -656)
        self.unregistered_volume = PL1.EnumValue(name, 'unregistered_volume', -657)
        self.unregvol = PL1.EnumValue(name, 'unregvol', -657)
        self.unsupported_multi_class_volume = PL1.EnumValue(name, 'unsupported_multi_class_volume', -658)
        self.unsupvol = PL1.EnumValue(name, 'unsupvol', -658)
        self.unsupported_operation = PL1.EnumValue(name, 'unsupported_operation', -659)
        self.unsupop = PL1.EnumValue(name, 'unsupop', -659)
        self.unsupported_terminal = PL1.EnumValue(name, 'unsupported_terminal', -660)
        self.bad_term = PL1.EnumValue(name, 'bad_term', -660)
        self.user_not_found = PL1.EnumValue(name, 'user_not_found', -661)
        self.usernfd = PL1.EnumValue(name, 'usernfd', -661)
        self.user_requested_logout = PL1.EnumValue(name, 'user_requested_logout', -662)
        self.userlogo = PL1.EnumValue(name, 'userlogo', -662)
        self.user_requested_hangup = PL1.EnumValue(name, 'user_requested_hangup', -663)
        self.userhngp = PL1.EnumValue(name, 'userhngp', -663)
        self.vchn_active = PL1.EnumValue(name, 'vchn_active', -664)
        self.vchnact = PL1.EnumValue(name, 'vchnact', -664)
        self.vchn_not_found = PL1.EnumValue(name, 'vchn_not_found', -665)
        self.vchnnfnd = PL1.EnumValue(name, 'vchnnfnd', -665)
        self.vol_in_use = PL1.EnumValue(name, 'vol_in_use', -666)
        self.volinuse = PL1.EnumValue(name, 'volinuse', -666)
        self.volume_busy = PL1.EnumValue(name, 'volume_busy', -667)
        self.volbusy = PL1.EnumValue(name, 'volbusy', -667)
        self.volume_not_loaded = PL1.EnumValue(name, 'volume_not_loaded', -668)
        self.volntld = PL1.EnumValue(name, 'volntld', -668)
        self.volume_type_unknown = PL1.EnumValue(name, 'volume_type_unknown', -669)
        self.vtNOTknown = PL1.EnumValue(name, 'vtNOTknown', -669)
        self.vtoc_io_err = PL1.EnumValue(name, 'vtoc_io_err', -670)
        self.vtocioer = PL1.EnumValue(name, 'vtocioer', -670)
        self.vtoce_connection_fail = PL1.EnumValue(name, 'vtoce_connection_fail', -671)
        self.vtocecnf = PL1.EnumValue(name, 'vtocecnf', -671)
        self.vtoce_free = PL1.EnumValue(name, 'vtoce_free', -672)
        self.vtocefr = PL1.EnumValue(name, 'vtocefr', -672)
        self.wakeup_denied = PL1.EnumValue(name, 'wakeup_denied', -673)
        self.nowakeup = PL1.EnumValue(name, 'nowakeup', -673)
        self.wrong_channel_ring = PL1.EnumValue(name, 'wrong_channel_ring', -674)
        self.wrchring = PL1.EnumValue(name, 'wrchring', -674)
        self.wrong_no_of_args = PL1.EnumValue(name, 'wrong_no_of_args', -675)
        self.badargno = PL1.EnumValue(name, 'badargno', -675)
        self.zero_length_seg = PL1.EnumValue(name, 'zero_length_seg', -676)
        self.zerosegl = PL1.EnumValue(name, 'zerosegl', -676)
        self.no_forms_table_defined = PL1.EnumValue(name, 'no_forms_table_defined', -677)
        self.notabdef = PL1.EnumValue(name, 'notabdef', -677)
        self.bad_forms_option = PL1.EnumValue(name, 'bad_forms_option', -678)
        self.badfrmop = PL1.EnumValue(name, 'badfrmop', -678)
