from typing import List

from deflate.compressor import Compressor
from deflate.decompressor import Decompressor
import time


class CLIHandler:

    @staticmethod
    def compress(archive_name: str, files: List[str]):
        compressor = Compressor()
        start = time.perf_counter()
        statistic = \
            compressor.compress(archive_name, files)
        end = time.perf_counter()
        time_duration = end - start
        for file in statistic:
            print('Compress ratio for ', file, ' is',
                  statistic[file].compression_ratio, '%')
            print('Time duration for ', file, ' is', statistic[file].time)
        print('Time for full compress is ', time_duration)
        print('Archive created successfully')

    @staticmethod
    def decompress(archive_name: str):
        decompressor = Decompressor()
        decompressor.decompress(archive_name)
        print('Archive successfully decompressed')
