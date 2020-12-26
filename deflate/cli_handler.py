from deflate.compressor import Compressor
from deflate.decompressor import Decompressor


class CLIHandler:

    @staticmethod
    def compress(archive_name: str, filename: str):
        compressor = Compressor()
        data = compressor.read_from_file(filename)
        encoded_data, time = compressor.compress(data, filename)
        compressor.write_archive(archive_name, encoded_data)
        print('Compress ratio is',
              compressor.calculate_compress_ratio(len(data),
                                                  len(encoded_data)),
              '%')
        print('Time for compress is ', time)
        print('Archive created successfully')

    @staticmethod
    def decompress(archive_name: str):
        decompressor = Decompressor()
        data = decompressor.read_from_archive(archive_name)
        file, decoded_data = decompressor.decompress(data)
        decompressor.write_file(file, decoded_data)
        print('Archive successfully decompressed')
