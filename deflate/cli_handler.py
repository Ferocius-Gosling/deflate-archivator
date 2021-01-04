from deflate.compressor import Compressor
from deflate.decompressor import Decompressor
import time


class CLIHandler:

    @staticmethod
    def compress(archive_name: str, filename: str):
        compressor = Compressor()
        start = time.perf_counter()
        source_length, encoded_length = \
            compressor.compress(archive_name, filename)
        end = time.perf_counter()
        time_duration = end - start
        print('Compress ratio is',
              compressor.calculate_compress_ratio(source_length,
                                                  encoded_length), '%')
        print('Time for compress is ', time_duration)
        print('Archive created successfully')

    @staticmethod
    def decompress(archive_name: str):
        decompressor = Decompressor()
        offset, filename = decompressor.read_from_archive(archive_name)
        decompressor.decompress(filename, archive_name, offset)
        print('Archive successfully decompressed')
