import json
import struct
from pathlib import Path
from deflate import const
from deflate.huffman import HuffmanCodec
from deflate.lz77 import LZ77Codec, Codeword
from deflate import errors


class Decompressor:

    @staticmethod
    def read_from_archive(archive_name):
        archive = Path.cwd() / archive_name
        if archive.suffix != '.dfa' or not archive.exists():
            raise errors.NotArchiveError()
        with open(archive, 'rb+') as file:
            name_length_data = file.read(const.unsigned_short)
            name_length = struct.unpack('H', name_length_data)[0]
            name_data = file.read(name_length)
            name = name_data.decode()
            return const.unsigned_short + name_length, name

    def decompress(self, filename: str, archive_name: str, offset: int):
        with open(archive_name, 'rb+') as archive:
            while offset < Path(archive_name).stat().st_size:
                archive.seek(offset, 0)
                checksum = archive.read(const.checksum)
                print(checksum, 'archived checksum', offset)
                code_table_length_data = archive.read(const.unsigned_int)
                code_table_length = struct.unpack('I', code_table_length_data)[0]
                code_table_data = archive.read(code_table_length)
                code_table = json.loads(code_table_data.decode())
                skip_length_data = archive.read(const.unsigned_int)
                skip_length = struct.unpack('I', skip_length_data)[0]
                data_length = (skip_length + (8 - (skip_length % 8))) // 8
                data = archive.read(data_length)
                decoded_data = self._decompress_block(code_table, data, checksum, skip_length)
                offset = archive.tell()
                with open(filename, 'ab+') as file:
                    file.write(decoded_data)

    def _decompress_block(self, code_table: dict, data: bytes,
                          checksum: bytes, skip_length: int):
        huffman_codec = HuffmanCodec()
        lz77_codec = LZ77Codec(256)
        decoded_huffman = huffman_codec.decode(code_table, data,
                                               checksum, skip_length)
        decoded = lz77_codec.decode(self._get_codewords_from_bytes
                                    (decoded_huffman))
        print(decoded, 'decoded data')
        print(len(decoded))
        print(huffman_codec.count_checksum(decoded), 'counted checksum decoded')
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
