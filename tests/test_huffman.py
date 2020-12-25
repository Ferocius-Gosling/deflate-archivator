import pytest
from bitarray import bitarray
from deflate.huffman import HuffmanCodec, Node


@pytest.fixture()
def huffman_codec():
    return HuffmanCodec()


@pytest.mark.parametrize('data, expected', [(b'teeeestt', bitarray([1, 1, 0,
                                                                    0, 0, 0,
                                                                    1, 0, 1,
                                                                    1, 1, 1]
                                                                   )),
                                            (b'aaaaa', bitarray([1, 1, 1,
                                                                 1, 1])),
                                            (b'ABCDE', bitarray([1, 1, 0,
                                                                 1, 0, 1,
                                                                 1, 1, 0,
                                                                 1, 0, 0]))])
def test_encode(huffman_codec: HuffmanCodec, data, expected):
    encoded_data = huffman_codec.encode(data)
    assert encoded_data[0] == expected


@pytest.mark.parametrize('data, expected', [(b'teeeestt',
                                             {116: bitarray([1, 1]),
                                              101: bitarray([0]),
                                              115: bitarray([1, 0])}),
                                            (b'aaaaa', {97: bitarray([1])}),
                                            (b'ABCDE', {65: bitarray([1, 1,
                                                                      0]),
                                                        66: bitarray([1, 0]),
                                                        67: bitarray([1, 1,
                                                                      1]),
                                                        68: bitarray([0, 1]),
                                                        69: bitarray([0, 0])})])
def test_collect_codes(huffman_codec: HuffmanCodec, data, expected):
    weights = huffman_codec.count_weights(data)
    tree = huffman_codec.create_tree(weights)
    codes = huffman_codec.collect_codes_from_tree(tree)
    assert codes == expected


@pytest.mark.parametrize('data, expected', [(b'teeeestt', Node(332, 8)),
                                            (b'aaaaa', Node(97, 5)),
                                            (b'ABCDE', Node(335, 5))])
def test_create_tree(huffman_codec, data, expected):
    weights = huffman_codec.count_weights(data)
    tree = huffman_codec.create_tree(weights)
    assert tree == expected


@pytest.mark.parametrize('data, expected', [(b'teeeestt',
                                             {116: 3, 101: 4, 115: 1}),
                                            (b'aaaaa', {97: 5}),
                                            (b'ABCDE', {65: 1, 66: 1, 67: 1,
                                                        68: 1, 69: 1})])
def test_count_weights(huffman_codec, data, expected):
    weights = huffman_codec.count_weights(data)
    assert weights == expected


@pytest.mark.parametrize('data, codes, checksum, skip, expected',
                         [(bytes(bitarray([1, 1, 0, 0, 0, 0,
                                           1, 0, 1, 1, 1, 1])),
                           {116: '11', 101: '0', 115: '10'},
                           b"(\x88d^\xd9'@J\xa7+\xb6\x0c\x0c\xe7\x0e\x80", 12,
                           b'teeeestt'),
                          (bytes(bitarray([1, 1, 1, 1, 1])),
                           {97: '1'}, b'YO\x80;8\nA9n\xd6=\xca9P5B', 5,
                           b'aaaaa'),
                          (bytes(bitarray([1, 1, 0, 1, 0, 1,
                                           1, 1, 0, 1, 0, 0])),
                           {65: '110', 66: '10', 67: '111',
                            68: '01', 69: '00'},
                           b'.\xcd\xde9Y\x05\x1d\x91?a\xb1Ey\xea\x13m', 12,
                           b'ABCDE')
                          ])
def test_decode(huffman_codec: HuffmanCodec, data, codes, checksum, skip,
                expected):
    decoded_data = huffman_codec.decode(codes, data, checksum, skip)
    assert decoded_data == expected

