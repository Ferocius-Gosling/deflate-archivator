class BaseDeflateError(BaseException):
    message: str


class WrongChecksumError(BaseDeflateError):
    message = 'wrong chesksum, cannot be decompressed'


class CodewordNotInWindowError(BaseDeflateError):
    message = 'Codeword not in window, cannot be decompressed'


class CodewordOffsetNegativeError(BaseDeflateError):
    message = 'Codeword offset negative, cannot be decompressed'


class NotArchiveError(BaseDeflateError):
    message = 'File extension is not .dfa'


class BrokenArchiveError(BaseDeflateError):
    message = 'Unable to decode data'


class EmptyFilesError(BaseDeflateError):
    message = 'Empty files error'
