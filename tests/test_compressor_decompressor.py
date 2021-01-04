import pytest
from deflate.compressor import Compressor
from deflate.decompressor import Decompressor
from pathlib import Path


def create_file(filename, data):
    cwd = Path.cwd() / filename
    cwd.write_bytes(data)


def delete_file(filename):
    cwd = Path.cwd() / filename
    cwd.unlink()


@pytest.fixture()
def compressor():
    return Compressor()


@pytest.fixture()
def decompressor():
    return Decompressor()


@pytest.mark.parametrize('archive_name, filename, data, expected',
                         [('archive1', 'test_compress1.txt',
                           b'test test test test', b'test test test test'),
                          ('archive2', 'test_compress2.js',
                           b'console.log("hello hello log            ")',
                           b'console.log("hello hello log            ")'),
                          ('archive3', 'test_compress3.png', bytes(1024),
                           bytes(1024))])
def test_compress_and_decompress_file(compressor, decompressor, archive_name,
                                      filename, data, expected):
    create_file(filename, data)
    # data_from_file = compressor.read_from_file(filename)
    # assert data_from_file is not None
    # assert isinstance(data_from_file, bytes)
    compressor.compress(archive_name, filename)
    # compressor.write_archive(archive_name, encoded_data)
    assert (Path.cwd() / (archive_name + '.dfa')).exists()
    delete_file(filename)
    offset, decoded_file = decompressor.read_from_archive(archive_name + '.dfa')
    decompressor.decompress(decoded_file, archive_name + '.dfa', offset)
    assert Path(decoded_file).read_bytes() == data
    # decompressor.write_file(file, decoded_data)
    assert (Path.cwd() / filename).exists()
    delete_file(filename)
    delete_file(archive_name + '.dfa')
