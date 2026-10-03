import numpy as np

DIMS = ["PDI", "IDV", "MAS", "UAI", "LTO", "IVR"]

REFERENCE = {
    "KSA": np.array([95, 25, 60, 80, 36, 52], dtype=float),
    "USA": np.array([40, 91, 62, 46, 26, 68], dtype=float),
    "KSA_almutairi": np.array([72, 48, 43, 64, 27, 14], dtype=float),
}


def indices(m, c=50.0):
    return {
        "PDI": 35 * (m[7] - m[2]) + 25 * (m[20] - m[23]) + c,
        "IDV": 35 * (m[4] - m[1]) + 35 * (m[9] - m[6]) + c,
        "MAS": 35 * (m[5] - m[3]) + 35 * (m[8] - m[10]) + c,
        "UAI": 40 * (m[18] - m[15]) + 25 * (m[21] - m[24]) + c,
        "LTO": 40 * (m[13] - m[14]) + 25 * (m[19] - m[22]) + c,
        "IVR": 35 * (m[12] - m[11]) + 40 * (m[17] - m[16]) + c,
    }
