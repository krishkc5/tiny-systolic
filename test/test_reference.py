import unittest
from model.reference import matmul_int4

class ReferenceTest(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(matmul_int4([[1,0],[0,1]], [[-8,7],[3,-2]]), [[-8,7],[3,-2]])
    def test_extremes(self):
        self.assertEqual(matmul_int4([[-8]*16]*2, [[-8,-8]]*16), [[1024,1024]]*2)
    def test_reject_invalid(self):
        for a,b in [([[8],[0]],[[1,1]]), ([[1],[1]],[[1]]), ([[],[]],[])]:
            with self.assertRaises(ValueError): matmul_int4(a,b)
