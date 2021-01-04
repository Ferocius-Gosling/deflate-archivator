import json
import struct
from datetime import datetime
from pathlib import Path
from bitarray import bitarray
from deflate.huffman import HuffmanCodec
from deflate.lz77 import LZ77Codec


class Compressor:
    def compress(self, archive_name: str, pathname: str):
        compressed_data = bytearray()
        compressed_data.extend(struct.pack('H', len(pathname)))
        compressed_data.extend(pathname.encode())
        self.write_archive(archive_name, compressed_data)
        # todo сделай длину блока в compress_and_pack
        size = 32768
        file_size = Path(pathname).stat().st_size
        summary_encoded_length = 0
        with open(pathname, 'rb+') as file:
            while size <= file_size:
                data = file.read(32768)
                print(size, 'first lap')
                packed_data = self.__compress_and_pack(data)
                summary_encoded_length += len(packed_data)
                size += 32768
                with open(archive_name + '.dfa', 'ab+') as archive:
                    archive.write(packed_data)
            else:
                data = bytes()
                if file_size < size:
                    data = file.read(file_size)
                else:
                    data = file.read(file_size - size)
                packed_data = self.__compress_and_pack(data)
                summary_encoded_length += len(packed_data)
                with open(archive_name + '.dfa', 'ab+') as archive:
                    archive.write(packed_data)
        return file_size, summary_encoded_length

    def __compress_and_pack(self, data: bytes):
        lz77_codec = LZ77Codec(256)
        huffman_codec = HuffmanCodec()
        checksum = huffman_codec.count_checksum(data)
        codewords = lz77_codec.encode(data)
        codewords_bytes = bytearray()
        for codeword in codewords:
            codewords_bytes.append(codeword.offset)
            codewords_bytes.append(codeword.length)
            codewords_bytes.append(codeword.char)
        encoded_data, codes_table = \
            huffman_codec.encode(bytes(codewords_bytes))
        packed_data = self._pack_data(encoded_data, checksum, codes_table)
        return packed_data

    @staticmethod
    def calculate_compress_ratio(original_size, compressed_size):
        return (1 - compressed_size / original_size) * 100

    @staticmethod
    def _pack_data(encoded_data: bitarray, checksum: bytes,
                   codes_table: dict):
        packed_data = bytearray()
        packed_data.extend(checksum)
        serialized_table = json.dumps({int(i): codes_table[i].to01()
                                       for i in codes_table}).encode()
        packed_data.extend(struct.pack('I', len(serialized_table)))
        packed_data.extend(serialized_table)
        # это и есть по сути длина блока
        packed_data.extend(struct.pack('I', len(encoded_data)))
        packed_data.extend(encoded_data.tobytes())
        return bytes(packed_data)

    # @staticmethod
    # def read_from_file(filename: str):
    #     file = Path.cwd() / filename
    #     return file.read_bytes()

    @staticmethod
    def write_archive(archive_name: str, encoded_data: bytes):
        if not archive_name:
            archive_name = 'archive' + datetime.today().strftime('%Y-%m-%d') \
                           + '.dfa'
        else:
            archive_name += '.dfa'
        archive_path = Path.cwd() / archive_name
        data_to_archive = bytearray(encoded_data)
        archive_path.write_bytes(data_to_archive)
