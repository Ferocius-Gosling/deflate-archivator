import json
import struct
from datetime import datetime
from pathlib import Path
from deflate import const
from bitarray import bitarray
from deflate.huffman import HuffmanCodec
from deflate.lz77 import LZ77Codec, Codeword
from deflate import errors


class Decompressor:

    @staticmethod
    def read_from_archive(archive_name):
        archive = Path.cwd() / archive_name
        if archive.suffix != '.dfa' or not archive.exists():
            raise errors.NotArchiveError()
        return archive.read_bytes()

    def decompress(self, data: bytes):
        huffman_codec = HuffmanCodec()
        lz77_codec = LZ77Codec(256)
        offset = const.offsets['unsigned_short']
        filename_length = struct.unpack('H', data[:offset])[0]
        filename = data[offset:offset + filename_length].decode()
        offset += filename_length
        checksum = data[offset:offset + const.offsets['checksum']]
        offset += const.offsets['checksum']
        code_table_length = struct.unpack('I',
                                          data[offset:
                                               offset +
                                               const.offsets['unsigned_int']])[0]
        offset += const.offsets['unsigned_int']
        code_table = json.loads(data[offset: offset +
                                     code_table_length].decode())
        offset += code_table_length
        skip_length = struct.unpack('I', data[offset: offset +
                                              const.offsets['unsigned_int']])
        skip_length = skip_length[0]
        data_to_decode = data[offset + const.offsets['unsigned_int']:]
        decoded_huffman = huffman_codec.decode(code_table, data_to_decode,
                                               checksum, skip_length)
        decoded = lz77_codec.decode(self._get_codewords_from_bytes
                                    (decoded_huffman))
        if huffman_codec.count_checksum(decoded) != checksum:
            raise errors.WrongChecksumError()
        return Path(filename), decoded

    @staticmethod
    def _get_codewords_from_bytes(data: bytes):
        print(len(data))
        if len(data) % 3 != 0:
            raise errors.BrokenArchiveError()
        codewords = []
        for i in range(len(data) // 3):
            offset = data[3 * i]
            length = data[3 * i + 1]
            char = data[3 * i + 2]
            codewords.append(Codeword(offset, length, char))
        return codewords

    @staticmethod
    def write_file(file: Path, data: bytes):
        file = Path.cwd() / file
        file.write_bytes(data)

