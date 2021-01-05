import dataclasses
import json
import queue
import struct
import time
from datetime import datetime
from pathlib import Path
from typing import List

from bitarray import bitarray

from deflate import errors
from deflate.huffman import HuffmanCodec
from deflate.lz77 import LZ77Codec


@dataclasses.dataclass()
class Statistic:
    time: float = 0
    compression_ratio: float = 0


class Compressor:
    def __init__(self):
        self.statistics = {}

    def compress(self, archive_name: str, files: List[str]):
        files = self.collect_files(files)
        if not files:
            raise errors.EmptyFilesError()
        for file_to_archive in files:
            print(file_to_archive)
            start = time.perf_counter()
            name_data = bytearray()
            name_data.extend(struct.pack('H', len(str(file_to_archive))))
            name_data.extend(str(file_to_archive).encode())
            self.write_archive(archive_name, name_data)
            original_size, encoded_size = \
                self._encode_file(file_to_archive, archive_name)
            end = time.perf_counter()
            self.statistics[file_to_archive.name] \
                = Statistic(end - start,
                            self.calculate_compress_ratio(original_size,
                                                          encoded_size))
        return self.statistics

    def _encode_file(self, file_to_archive: Path, archive_name: str):
        size = 32768
        file_size = file_to_archive.stat().st_size
        summary_encoded_length = 0
        with open(str(file_to_archive), 'rb+') as file:
            while size <= file_size:
                data = file.read(32768)
                packed_data = self.__compress_and_pack(data)
                packed_data.extend(struct.pack('B', 1))
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
                packed_data.extend(struct.pack('B', 2))
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
        return packed_data

    @staticmethod
    def write_archive(archive_name: str, encoded_data: bytes):
        if not archive_name:
            archive_name = 'archive' + datetime.today().strftime('%Y-%m-%d') \
                           + '.dfa'
        else:
            archive_name += '.dfa'
        data_to_archive = bytearray(encoded_data)
        with open(archive_name, 'ab+') as archive:
            archive.write(data_to_archive)

    @staticmethod
    def collect_files(file_names: List[str]):
        files = set()
        cwd = Path.cwd()
        dirs = queue.Queue()
        for filename in file_names:
            path = cwd / filename
            if path.is_dir():
                dirs.put(path)
            elif path.exists() and path.stat().st_size != 0:
                files.add(path)
        while not dirs.empty():
            directory = dirs.get()
            for direct in directory.glob('*'):
                if direct.is_dir():
                    dirs.put(direct)
                elif direct.exists() and direct.stat().st_size != 0:
                    files.add(direct)
        return sorted(files, key=lambda file: file.parent)
