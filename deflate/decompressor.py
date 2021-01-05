import json
import struct
from pathlib import Path
from deflate import const
from deflate.huffman import HuffmanCodec
from deflate.lz77 import LZ77Codec, Codeword
from deflate import errors


class Decompressor:
    def decompress(self, archive_name: str):
        archive_path = Path.cwd() / archive_name
        if archive_path.suffix != '.dfa' or not archive_path.exists():
            raise errors.NotArchiveError()
        offset = 0
        with open(archive_path.name, 'rb+') as archive:
            while offset < Path(archive_name).stat().st_size:
                name_length_data = archive.read(const.unsigned_short)
                name_length = struct.unpack('H', name_length_data)[0]
                name_data = archive.read(name_length)
                filename = name_data.decode()
                filepath = Path(filename)
                while True:
                    checksum = archive.read(const.checksum)
                    code_table_length_data = archive.read(const.unsigned_int)
                    code_table_length = \
                        struct.unpack('I', code_table_length_data)[0]
                    code_table_data = archive.read(code_table_length)
                    code_table = json.loads(code_table_data.decode())
                    skip_length_data = archive.read(const.unsigned_int)
                    skip_length = struct.unpack('I', skip_length_data)[0]
                    if not skip_length % 8:
                        data_length = skip_length // 8
                    else:
                        data_length = (skip_length + (8 - (skip_length % 8)))\
                                      // 8
                    data = archive.read(data_length)
                    decoded_data = \
                        self._decompress_block(code_table, data,
                                               checksum, skip_length)
                    is_last_block_file_data = \
                        archive.read(const.unsigned_char)
                    is_last_block = struct.unpack('B',
                                                  is_last_block_file_data)[0]
                    offset = archive.tell()
                    if not filepath.parent.exists():
                        filepath.parent.mkdir()
                    with open(filename, 'ab+') as file:
                        file.write(decoded_data)
                        if is_last_block == 2:
                            break

    def _decompress_block(self, code_table: dict, data: bytes,
                          checksum: bytes, skip_length: int):
        huffman_codec = HuffmanCodec()
        lz77_codec = LZ77Codec(256)
        decoded_huffman = huffman_codec.decode(code_table, data,
                                               checksum, skip_length)
        decoded = lz77_codec.decode(self._get_codewords_from_bytes
                                    (decoded_huffman))
        if huffman_codec.count_checksum(decoded) != checksum:
            raise errors.WrongChecksumError()
        return decoded

    @staticmethod
    def _get_codewords_from_bytes(data: bytes):
        if len(data) % 3 != 0:
            raise errors.BrokenArchiveError()
        codewords = []
        for i in range(len(data) // 3):
            offset = data[3 * i]
            length = data[3 * i + 1]
            char = data[3 * i + 2]
            codewords.append(Codeword(offset, length, char))
        return codewords
