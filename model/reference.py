"""Exact integer arithmetic reference; no ML dependencies required."""
def matmul_int4(a, b):
    if len(a) != 2 or not a[0] or len(a[0]) > 16:
        raise ValueError("A must be 2 x K, 1 <= K <= 16")
    k = len(a[0])
    if any(len(row) != k for row in a) or len(b) != k or any(len(row) != 2 for row in b):
        raise ValueError("Expected A[2,K] and B[K,2]")
    if any(type(v) is not int or not -8 <= v <= 7 for m in (a,b) for row in m for v in row):
        raise ValueError("Operands must be signed INT4 integers")
    return [[sum(a[i][t]*b[t][j] for t in range(k)) for j in range(2)] for i in range(2)]
