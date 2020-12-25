import argparse
from deflate.compressor import Compressor
from deflate.decompressor import Decompressor


def parse_args():
    parser = argparse.ArgumentParser(description='Deflate archiver')
    subparsers = parser.add_subparsers()

    compress = subparsers.add_parser('compress', help='compress file')
    compress.set_defaults(command='cmopress')
    compress.add_argument('file', help='File you want to archive', nargs='?')
    compress.add_argument('archivename', help='Archive name', nargs='?')

    decompress = subparsers.add_parser('decompress', help='Decompress archive')
    decompress.set_defaults(command='decompress')
    decompress.add_argument('archive', help='Archive to decompress')
    return parser.parse_args().__dict__


if __name__ == '__main__':
    args = parse_args()
    if 'command' not in args:
        print('Usage: deflate [-h] {compress, decompress}')
        exit(1)
    command = args.pop('command')
    if command == 'compress':
        compressor = Compressor()
    else:
        decompressor = Decompressor()
