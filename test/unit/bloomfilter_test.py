#! /usr/bin/env python
'''Bloom filter test'''

# pylint: disable=invalid-name

import binascii
import unittest
import zlib
from bloomfilter import BloomFilter


class TestBloomFilterCreate(unittest.TestCase):
    '''Bloom filter object creation test'''

    def test_raises_error_on_invalid_capacity(self):
        '''BloomFilter() raises on invalid capacity'''
        with self.assertRaises(ValueError):
            BloomFilter(None, 0.5)

    def test_raises_error_on_non_positive_capacity(self):
        '''BloomFilter() raises on non-positive capacity'''
        with self.assertRaises(ValueError):
            BloomFilter(-1, 0.5)

    def test_raises_error_on_invalid_error_rate(self):
        '''BloomFilter() raises on invalid error rate'''
        with self.assertRaises(ValueError):
            BloomFilter(5, None)

    def test_raises_error_on_out_of_range_error_rate(self):
        '''BloomFilter() raises on out-of-range error rate'''
        with self.assertRaises(ValueError):
            BloomFilter(5, -1)

        with self.assertRaises(ValueError):
            BloomFilter(5, 2)

    def test_raises_error_when_allocation_failes(self):
        '''BloomFilter() raises on invalid error rate'''
        with self.assertRaises(ValueError):
            BloomFilter(10000000000, 1e-100)

    def test_creates_filter(self):
        '''BloomFilter() creates filter with required parameters'''
        BloomFilter(5, 0.5)

    def test_creates_filter_with_non_integral_capacity(self):
        '''BloomFilter() creates filter with non-integral capacity'''
        float_filter = BloomFilter(capacity=1000.2, error_rate=1e-3)
        int_filter = BloomFilter(capacity=1000, error_rate=1e-3)

        bit_count = int_filter.bit_count
        self.assertGreaterEqual(float_filter.bit_count, bit_count)
        self.assertLess(float_filter.bit_count, bit_count + 10)
        self.assertEqual(int_filter.hash_count, float_filter.hash_count)

    def test_always_creates_filter_with_odd_bit_count(self):
        '''BloomFilter() creates filter with non-integral capacity'''
        bloom_filter = BloomFilter(capacity=1000, error_rate=1e-3)

        self.assertEqual(bloom_filter.bit_count & 1, 1)

    def test_creates_filter_with_randomized_hash_seeds(self):
        '''BloomFilter() creates filter with randomized hash seeds'''
        filter_1 = BloomFilter(5, 0.5)
        filter_2 = BloomFilter(5, 0.5)
        self.assertNotEqual(filter_1.raw_data(), filter_2.raw_data())


class TestBloomFilterByteSize(unittest.TestCase):
    '''Bloom filter byte size test'''

    def test_byte_size_is_in_expected_range(self):
        '''BloomFilter.byte_size returns expected value'''
        bloom_filter = BloomFilter(1000000, 1e-3)
        size = bloom_filter.byte_size
        # 14377640 bits, 10 hashes
        self.assertLess(1797208, size)
        self.assertGreater(1800000, size)


class TestBloomFilterHashCount(unittest.TestCase):
    '''Bloom filter hash count test'''

    def test_hash_count_expected(self):
        '''BloomFilter.hash_count returns expected value'''
        bloom_filter = BloomFilter(1000000, 1e-3)
        # 14377640 bits, 10 hashes
        self.assertEqual(bloom_filter.hash_count, 10)


class TestBloomFilterBitCount(unittest.TestCase):
    '''Bloom filter bit count test'''

    def test_hash_count_expected(self):
        '''BloomFilter.bit_count returns expected value'''
        bloom_filter = BloomFilter(1000000, 1e-3)
        # 14377640 bits, 10 hashes
        # added 1, since we want it always odd
        self.assertEqual(bloom_filter.bit_count, 14377641)


class TestBloomFilterAddAndTest(unittest.TestCase):
    '''Bloom filter add / test test'''

    def test_all_test_negative_when_filter_empty(self):
        '''BloomFilter.test_hash() returns False when filter is empty'''
        bloom_filter = BloomFilter(1000000, 1e-3)

        self.assertEqual(bloom_filter.test_hash('abc'), False)

    def test_returns_true_positive_when_value_had_been_added(self):
        '''BloomFilter.test_hash() returns True after the item added'''
        bloom_filter = BloomFilter(1000000, 1e-3)

        bloom_filter.add_hash('abc')

        self.assertEqual(bloom_filter.test_hash('abc'), True)

    def test_returns_positive_when_hashes_collide(self):
        '''BloomFilter.test_hash() returns True when hashes collide'''
        bloom_filter = BloomFilter(1000000, 1e-3)

        bloom_filter.add_hash('abc')

        self.assertEqual(bloom_filter.test_hash(u'abc'), True)

    def test_all_test_positive_when_hashes_collide(self):
        '''BloomFilter.test_hash() returns False when filter is empty'''
        bloom_filter = BloomFilter(1000000, 1e-3)

        bloom_filter.add_hash('abc')

        self.assertEqual(bloom_filter.test_hash('def'), False)


class TestBloomFilterToAndFromBase64(unittest.TestCase):
    '''Bloom filter to_base64 / from_base64 test'''

    def test_serializes_filter_to_base64(self):
        '''BloomFilter can round trip to_base64() -> from_base64()'''
        bloom_filter = BloomFilter(100, 0.1)
        bloom_filter.add_hash('abcdef')

        serialized_filter = bloom_filter.to_base64()

        restored_filter = BloomFilter.from_base64(serialized_filter)
        self.assertEqual(bloom_filter.raw_data(), restored_filter.raw_data())

    def test_raises_error_on_invalid_input(self):
        '''from_base64() raises on invalid input'''
        with self.assertRaises(binascii.Error):
            BloomFilter.from_base64('abc')

        with self.assertRaises(zlib.error):
            BloomFilter.from_base64('abc'.encode('base64'))

        with self.assertRaises(ValueError):
            BloomFilter.from_base64(zlib.compress('abc').encode('base64'))


if __name__ == '__main__':
    unittest.main()