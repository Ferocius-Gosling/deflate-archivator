import pytest
from deflate.lz77 import LZ77Codec, Codeword


@pytest.mark.parametrize('data, expected',
                         [(b'abracadabra',
                          [Codeword(0, 0, 97), Codeword(0, 0, 98),
                           Codeword(0, 0, 114), Codeword(3, 1, 99),
                           Codeword(2, 1, 100), Codeword(7, 3, 97)]),
                         (b'ababababababab',
                          [Codeword(0, 0, 97), Codeword(0, 0, 98),
                           Codeword(2, 11, 98)]),
                         (b'wo dwore trawa na trawe drowa ne rubi'
                          b'dwora na trawe dwora',
                          [Codeword(0, 0, 119), Codeword(0, 0, 111),
                           Codeword(0, 0, 32), Codeword(0, 0, 100),
                           Codeword(4, 2, 114), Codeword(0, 0, 101),
                           Codeword(6, 1, 116), Codeword(4, 1, 97),
                           Codeword(8, 1, 97), Codeword(6, 1, 110),
                           Codeword(3, 2, 116), Codeword(9, 3, 101),
                           Codeword(21, 2, 114), Codeword(21, 1, 119),
                           Codeword(15, 3, 101), Codeword(3, 1, 114),
                           Codeword(0, 0, 117), Codeword(0, 0, 98),
                           Codeword(0, 0, 105), Codeword(34, 4, 97),
                           Codeword(28, 11, 119), Codeword(15, 2, 97)]),
                          (b'test test test',
                           [Codeword(0, 0, 116), Codeword(0, 0, 101),
                            Codeword(0, 0, 115), Codeword(3, 1, 32),
                            Codeword(5, 8, 116)])])
def test_encode(data, expected):
    lz77_codec = LZ77Codec(len(data))
    encoded = lz77_codec.encode(data)
    assert encoded == expected


@pytest.mark.parametrize('data, expected',
                         [([Codeword(0, 0, 97), Codeword(0, 0, 98),
                           Codeword(0, 0, 114), Codeword(3, 1, 99),
                           Codeword(2, 1, 100), Codeword(7, 3, 97)],
                           b'abracadabra'),
                          ([Codeword(0, 0, 97), Codeword(0, 0, 98),
                           Codeword(2, 11, 98)], b'ababababababab'),
                          ([Codeword(0, 0, 119), Codeword(0, 0, 111),
                           Codeword(0, 0, 32), Codeword(0, 0, 100),
                           Codeword(4, 2, 114), Codeword(0, 0, 101),
                           Codeword(6, 1, 116), Codeword(4, 1, 97),
                           Codeword(8, 1, 97), Codeword(6, 1, 110),
                           Codeword(3, 2, 116), Codeword(9, 3, 101),
                           Codeword(21, 2, 114), Codeword(21, 1, 119),
                           Codeword(15, 3, 101), Codeword(3, 1, 114),
                           Codeword(0, 0, 117), Codeword(0, 0, 98),
                           Codeword(0, 0, 105), Codeword(34, 4, 97),
                           Codeword(28, 11, 119), Codeword(15, 2, 97)],
                           b'wo dwore trawa na trawe drowa ne rubi'
                           b'dwora na trawe dwora'),
                          ([Codeword(0, 0, 116), Codeword(0, 0, 101),
                            Codeword(0, 0, 115), Codeword(3, 1, 32),
                            Codeword(5, 8, 116)], b'test test test')
                          ])
def test_decode(data, expected):
    lz77_codec = LZ77Codec(len(data))
    decoded = lz77_codec.decode(data)
    assert decoded == expected
