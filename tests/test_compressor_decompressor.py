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


@pytest.mark.parametrize('archive_name, filenames, data, expected',
                         [('archive1', ['test_compress1.txt'],
                           b'test test test test', b'test test test test'),
                          ('archive2', ['test_compress2.js'],
                           b'console.log("hello hello log            ")',
                           b'console.log("hello hello log            ")'),
                          ('archive3', ['test_compress3.png'], bytes(1024),
                           bytes(1024)),
                          ('archive4', ['test_compress4_1.txt',
                                        'test_compress4_2.txt'],
                           b'abracadabra abracadabra abracadabra',
                           b'abracadabra abracadabra abracadabra')])
def test_compress_and_decompress_file(compressor, decompressor, archive_name,
                                      filenames, data, expected):
    for filename in filenames:
        create_file(filename, data)
    # data_from_file = compressor.read_from_file(filename)
    # assert data_from_file is not None
    # assert isinstance(data_from_file, bytes)
    compressor.compress(archive_name, filenames)
    # compressor.write_archive(archive_name, encoded_data)
    assert (Path.cwd() / (archive_name + '.dfa')).exists()
    for filename in filenames:
        delete_file(filename)
    decompressor.decompress(archive_name + '.dfa')
    for filename in filenames:
        assert Path(filename).read_bytes() == expected
    # decompressor.write_file(file, decoded_data)
    for filename in filenames:
        assert (Path.cwd() / filename).exists()
    for filename in filenames:
        delete_file(filename)
    delete_file(archive_name + '.dfa')
