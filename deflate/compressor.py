import json
import struct
from datetime import datetime
from pathlib import Path
from bitarray import bitarray
from deflate.huffman import HuffmanCodec
from deflate.lz77 import LZ77Codec


class Compressor:

    def compress(self, data: bytes, filename: str):
        compressed_data = bytearray()
        lz77_codec = LZ77Codec(256)
        huffman_codec = HuffmanCodec()
        checksum = huffman_codec.count_checksum(data)
        codewords = lz77_codec.encode(data)
        codewords_bytes = b''
        for codeword in codewords:
            codewords_bytes += bytes([codeword.offset])
            codewords_bytes += bytes([codeword.length])
            codewords_bytes += bytes([codeword.char])
        encoded_data, codes_table = huffman_codec.encode(codewords_bytes)
        packed_data = self._pack_data(encoded_data, checksum, codes_table)
        compressed_data.extend(struct.pack('H', len(filename)))
        compressed_data.extend(filename.encode())
        compressed_data.extend(packed_data)
        return compressed_data

    @staticmethod
    def _pack_data(encoded_data: bitarray, checksum: bytes,
                   codes_table: dict):
        packed_data = bytearray()
        packed_data.extend(checksum)
        serialized_table = json.dumps({int(i): codes_table[i].to01()
                                       for i in codes_table}).encode()
        # пока пусть так, можно будет сохранять сразу просто
        # длины кодов и потом декодить по длинам
        packed_data.extend(struct.pack('I', len(serialized_table)))
        packed_data.extend(serialized_table)
        packed_data.extend(struct.pack('I', len(encoded_data)))
        packed_data.extend(encoded_data.tobytes())
        return bytes(packed_data)

    @staticmethod
    def read_from_file(filename: str):
        file = Path.cwd() / filename
        return file.read_bytes()

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
