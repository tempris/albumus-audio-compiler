import os
import re
import sys
import json
from datetime import datetime, UTC
from pathlib import Path
from cure_ansi import ANSI

LOG_LEVEL = {
    'NONE': 0,
    'ERROR': 1,
    'WARN': 2,
    'INFO': 3,
    'DETAIL': 4,
    'DEBUG': 5,
    'ALL': 6
}

LOG_TAG_LOG = '[📜 Log]'
ansi = ANSI()

class CureLog:
    def __init__(self, logFilePath, logLevelConsole=LOG_LEVEL['DETAIL'], logLevelFile=LOG_LEVEL['ALL']):
        self.logFilePath = logFilePath
        self.isDebugSelf = False

        logDir = Path(logFilePath).parent
        logDir.mkdir(parents=True, exist_ok=True)
        Path(logFilePath).write_text('', encoding='utf-8')

        self.currentLogLevelConsole = logLevelConsole
        self.currentLogLevelFile = logLevelFile

        self.logLevels = {
            'info':     {'symbol': '[ℹ️ Info]',       'level': LOG_LEVEL['INFO']},
            'warn':     {'symbol': '[⚠️ Warning]',  'level': LOG_LEVEL['WARN']},
            'error':    {'symbol': '[❌ Error]',    'level': LOG_LEVEL['ERROR']},
            'debug':    {'symbol': '[🐛 Debug]',    'level': LOG_LEVEL['DEBUG']},
            'detail':   {'symbol': '[🔍 Detail]',   'level': LOG_LEVEL['DETAIL']},
            'notice':   {'symbol': '[📢 Notice]',   'level': LOG_LEVEL['INFO']},
            'success':  {'symbol': '[✅ Success]',  'level': LOG_LEVEL['INFO']},
            'begin':    {'symbol': '[🚦 Begin]',    'level': LOG_LEVEL['INFO']},
            'end':      {'symbol': '[🏁 End]',      'level': LOG_LEVEL['INFO']},
            'init':     {'symbol': '[🚀 Init]',     'level': LOG_LEVEL['INFO']},
            'shutdown': {'symbol': '[🛑 Shutdown]', 'level': LOG_LEVEL['INFO']}
        }

        self.ansiCodes = lambda level: {
            'info': ansi.bc['fg']['cyan'],
            'detail': ansi.bc['fg']['blue'],
            'notice': ansi.bc['fg']['yellow'],
            'success': ansi.bc['fg']['green'],
            'warn': ansi.bc['fg']['yellow'],
            'error': ansi.bc['fg']['red'],
            'debug': ansi.bc['fg']['green'] + ansi.style['underline'],
            'begin': ansi.bc['bg']['magenta'] + ansi.fg['white'],
            'end': ansi.bc['bg']['magenta'] + ansi.fg['white'],
            'init': ansi.bc['bg']['blue'] + ansi.fg['white'],
            'shutdown': ansi.bc['bg']['blue'] + ansi.fg['white']
        }.get(level, None)

        self.ansiCodesFollow = lambda level: {
            'begin': ansi.bc['fg']['magenta'],
            'end': ansi.bc['fg']['magenta'],
            'init': ansi.bc['fg']['blue'],
            'shutdown': ansi.bc['fg']['blue']
        }.get(level, None)

        self.consoleMethod = lambda level: print
        
        self.use_unicode = self.terminal_supports_unicode()

    def terminal_supports_unicode(self):
        try:
            return sys.stdout.encoding.lower().startswith('utf')
        except Exception:
            return False

    def print_safe(self, text):
        if not self.use_unicode:
            emoji_pattern = re.compile(
                "["                     # wide unicode ranges
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map
                "\U0001F1E0-\U0001F1FF"  # flags
                "\U00002500-\U00002BEF"  # chinese characters
                "\U00002702-\U000027B0"
                "\U000024C2-\U0001F251"
                "]+",
                flags=re.UNICODE
            )
            print(emoji_pattern.sub('', text))
            return
        
        print(text)

    def ansiRemove(self, input_):
        return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', input_)

    def getLogFile(self):
        return self.logFilePath

    def debugSelf(self, *args):
        if not self.isDebugSelf:
            return
        self.print_safe(f"{ansi.bc['bg']['green']}{ansi.fg['black']}📜🐛 [Log Debug] {args}{ansi.reset}")

    def isPath(self, input_):
        if not isinstance(input_, str) or not input_.strip():
            return False
        clean = input_.split('?')[0].split('#')[0].strip()
        if os.path.isabs(clean):
            return True
        if clean.startswith('./') or clean.startswith('../'):
            return True
        has_ext = re.search(r'\.[a-z0-9]+$', clean, re.I)
        has_sep = '/' in clean or '\\' in clean
        return has_sep and (has_ext or clean.endswith('/'))

    def normalizePath(self, filePath):
        return os.path.normpath(filePath).replace(os.sep, '/')

    def formatArg(self, arg, indentLevel=0, tagParent='', maxDepth=16):
        if indentLevel > maxDepth:
            return '<[[ANSI_OFF]]Max Depth Reached[[ANSI_ON]]>'
        indent = '  ' * indentLevel

        if isinstance(arg, list):
            if isinstance(arg[0], str) and arg[0].startswith('[[') and arg[0].endswith(']]'):
                tag = arg[0][2:-2]
                rest = arg[1:]
                if tag == 'NEWLINES':
                    return '\n'.join(self.formatArg(item, indentLevel, tag, maxDepth) for item in rest)
                if tag == 'LIST':
                    return '\n'.join(f"{indent}{'' if isinstance(item, list) and isinstance(item[0], str) and item[0][2:-2] == 'LIST' else '> '}{self.formatArg(item, indentLevel + 1, tag, maxDepth)}" for item in rest)
                if tag == 'NORMAL':
                    return ''.join(f"{self.formatArg(item, indentLevel, '', maxDepth)}{' ' if i != len(rest) - 1 else ''}" for i, item in enumerate(rest))
                self.error(LOG_TAG_LOG, 'Unknown tag in next log:', tag)
            return f"Array ({len(arg)} Entr{'ies' if len(arg) != 1 else 'y'}): [\n" + ',\n'.join(f"{indent}  {self.formatArg(item, indentLevel + 1, 'ARRAY', maxDepth)}" for item in arg) + f"\n{indent}]"
        elif isinstance(arg, dict):
            return f"Object ({len(arg)} Entr{'ies' if len(arg) != 1 else 'y'}): {{\n" + ',\n'.join(f"{indent}  [[ANSI_OFF]]{k}[[ANSI_ON]]: {self.formatArg(v, indentLevel + 1, 'OBJECT', maxDepth)}" for k, v in arg.items()) + f"\n{indent}}}"
        elif isinstance(arg, set):
            return f"Set ({len(arg)} Entr{'ies' if len(arg) != 1 else 'y'}): {{\n" + ',\n'.join(
                f"{indent}  {self.formatArg(item, indentLevel + 1, 'SET', maxDepth)}" for item in sorted(arg, key=str)
            ) + f"\n{indent}}}"
        elif arg is None:
            return '`[[ANSI_OFF]]null[[ANSI_ON]]`'
        elif callable(arg):
            return f"[Function: [[ANSI_OFF]]{arg.__name__ if hasattr(arg, '__name__') else 'anonymous'}[[ANSI_ON]]]"
        elif isinstance(arg, (int, float, bool)):
            return f"`[[ANSI_OFF]]{arg}[[ANSI_ON]]`"
        elif self.isPath(arg):
            return f'"[[ANSI_OFF]]{self.normalizePath(arg)}[[ANSI_ON]]"'
        elif isinstance(arg, str) and tagParent not in ('ARRAY', 'OBJECT', 'SET'):
            return arg
        else:
            # return json.dumps(arg).replace('"', '"[[ANSI_OFF]]').replace('[[ANSI_OFF]]', '[[ANSI_OFF]]', 1) + '[[ANSI_ON]]'
            escaped = json.dumps(arg)[1:-1]  # remove leading/trailing quotes
            return f'"[[ANSI_OFF]]{escaped}[[ANSI_ON]]"'

    def setLogLevel(self, level):
        if level in LOG_LEVEL:
            self.currentLogLevel = level
        else:
            raise ValueError(f"Invalid debug level: {level}")

    def writeToLogFile(self, logMessage):
        with open(self.logFilePath, "a", encoding="utf-8") as f:
            f.write(self.ansiRemove(logMessage).replace('[[ANSI_OFF]]', '').replace('[[ANSI_ON]]', '') + '\n')

    def prefixTimestamp(self, *args):
        timestamp = datetime.now(UTC).isoformat()
        return f"[{timestamp}] {' '.join(str(arg) for arg in args)}"

    def joinArgs(self, *args):
        result = []
        for i, arg in enumerate(args):
            prev = result[-1] if result else ''
            join_char = '' if isinstance(prev, str) and prev.endswith('\n') else ' '
            result.append(join_char + self.formatArg(arg) if i else self.formatArg(arg))
        return ''.join(result)

    def file(self, *args):
        self.writeToLogFile(self.joinArgs(*args))

    def console(self, *args):
        self.print_safe(self.joinArgs(*args))

    def log(self, level, *args):
        logLevel = self.logLevels.get(level)
        if not logLevel:
            raise ValueError(f"Invalid log level: {level}")

        if logLevel["level"] > self.currentLogLevelConsole and logLevel["level"] > self.currentLogLevelFile:
            return

        initialNewline = ''
        if isinstance(args[0], str) and args[0].startswith('\n'):
            initialNewline = '\n'
            args = (args[0][1:],) + args[1:]

        formattedArgs = self.joinArgs(*args)
        logMessage = self.prefixTimestamp(f"{logLevel['symbol']} {formattedArgs}")
        logMessage = initialNewline + logMessage

        if logLevel["level"] <= self.currentLogLevelFile:
            self.writeToLogFile(logMessage)

        if logLevel["level"] > self.currentLogLevelConsole:
            return

        lines = logMessage.split('\n')
        if len(lines) > 1 and self.ansiCodesFollow(level):
            formatted = [ansi.format(self.ansiCodes(level), lines[0])]
            formatted += [ansi.format(self.ansiCodesFollow(level), ln) for ln in lines[1:]]
            logMessage = '\n'.join(formatted)
        else:
            logMessage = ansi.format(self.ansiCodes(level), logMessage)

        self.consoleMethod(level)(logMessage)

    def custom(self, ansiCode, *args):
        msg = self.prefixTimestamp("[Custom] " + self.joinArgs(*args))
        self.writeToLogFile(msg)
        self.print_safe(ansi.format(ansiCode, msg))

    def plain(self, *args):
        msg = self.joinArgs(*args)
        self.writeToLogFile(self.ansiRemove(msg))
        self.print_safe(msg)

    # def bridge(self, *args):
    #     msg = self.joinArgs(*args)
    #     self.writeToLogFile(self.ansiRemove(msg).rstrip())
    #     self.print_safe(msg.rstrip())

    def info(self, *args):
        self.log('info', *args)

    def warn(self, *args):
        self.log('warn', *args)

    def error(self, *args):
        self.log('error', *args)

    def debug(self, *args):
        self.log('debug', *args)

    def detail(self, *args):
        self.log('detail', *args)

    def notice(self, *args):
        self.log('notice', *args)

    def success(self, *args):
        self.log('success', *args)

    def begin(self, *args):
        self.log('begin', *args)

    def end(self, *args):
        self.log('end', *args)

    def init(self, *args):
        self.log('init', *args)

    def shutdown(self, *args):
        self.log('shutdown', *args)

    def setDebug(self, value):
        self.isDebugSelf = value

    def logTest(self):
        logTagTest = '[🧪 Test]'

        self.begin(logTagTest, LOG_TAG_LOG, 'Running...')
        self.begin(logTagTest, LOG_TAG_LOG, 'Simple Test Running...')

        self.info(logTagTest, LOG_TAG_LOG, 'This is an info log.')
        self.warn(logTagTest, LOG_TAG_LOG, 'This is a warning log.')
        self.error(logTagTest, LOG_TAG_LOG, 'This is an error log.')
        self.detail(logTagTest, LOG_TAG_LOG, 'This is a detail log. The following debug log should appear in the log file but not console with default levels.')
        self.debug(logTagTest, LOG_TAG_LOG, 'This is a debug log (should appear in the log file but not console with default levels).')
        self.custom(ansi.bc['bg']['yellow'] + ansi.fg['black'] + ansi.style['underline'] + ansi.style['italic'],
                    logTagTest, LOG_TAG_LOG, 'This is a custom log.')
        self.shutdown('This is a shutdown log.')

        self.end(logTagTest, LOG_TAG_LOG, 'Simple Test Complete.')
        self.begin(logTagTest, LOG_TAG_LOG, 'Data Type Test Running...')

        dataSamples = {
            "string": "This is a string.",
            "number": 42,
            "boolean": True,
            "array": ["Array item 1", "Array item 2"],
            "nestedArray": [["Nested Array 1"], ["Nested Array 2"]],
            "object": {"key1": "value1", "key2": "value2"},
            "nestedObject": {"outerKey": {"innerKey": "innerValue"}},
            "set": {"apple", "banana", "cherry"},
            "null": None,
            "undefined": None,
            "function": lambda: "Hello",
            "path": "./relative/path/to/file.txt"
        }

        for dtype, value in dataSamples.items():
            self.info(logTagTest, LOG_TAG_LOG, f"Testing type '{dtype}':", value)

        self.end(logTagTest, LOG_TAG_LOG, 'Data Type Test Complete.')
        self.begin(logTagTest, LOG_TAG_LOG, 'Mixed Variable Type Test Running...')

        self.info('Mixed:', 123, None, None, 'Mixed End.')

        self.info(
            'Extreme Mixed:',
            ['input1.txt', 'input2.txt'],
            {'stage': 'initialization', 'config': {'retry': True, 'timeout': '30s'}},
            123,
            None,
            ['nestedArray', {'key': 'value'}],
            None,
            'Intermediate log message',
            {'errors': None, 'warnings': ['Low memory', 'Disk space low']},
            [42, 'randomValue', {'inner': 'object'}],
            'Extreme Mixed End.'
        )

        self.end(logTagTest, LOG_TAG_LOG, 'Mixed Variable Type Test Complete.')
        self.begin(logTagTest, LOG_TAG_LOG, 'Array Tag Test Running...')

        self.info([
            '[[NEWLINES]]',
            'Example:',
            'This string is on a new line.',
            [
                '[[LIST]]',
                'This string is in a list.',
                ['This string is in an array in a list.', 123],
                ['[[NORMAL]]', 'This string is in a list with a variable after it:', 123],
                [
                    '[[LIST]]',
                    'This string is in a list in a list.',
                    123
                ],
                'This string is also in a list.'
            ]
        ])

        self.end(logTagTest, LOG_TAG_LOG, 'Array Tag Test Complete.')
        self.end(logTagTest, LOG_TAG_LOG, 'Complete.')

if __name__ == "__main__":
    LOCATION_SCRIPT = os.path.dirname(os.path.abspath(__file__))
    log = CureLog(os.path.join(LOCATION_SCRIPT, "_log/cure_log.log"))
    log.setDebug(True)
    log.logTest()
