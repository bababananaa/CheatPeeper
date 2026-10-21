import pytest

from pipeline import calibrate, detect_eyes, estimate_gaze, extract_pupil, smooth

# synthetic inputs for each test
FRAME = [[0] * 8 for _ in range(6)]
EYE_CROP = [[0] * 4 for _ in range(4)]
CALIBRATION = {"scale": 1.0}
FEATURES = {"pupil": (2, 3)}
POINTS = [(0, 0), (100, 100), (200, 50)]
HISTORY = [(10, 10), (11, 12), (9, 11)]


# the tests just have stub data for now since the methods are not implemented
def test_detect_eyes():
    with pytest.raises(NotImplementedError):
        detect_eyes(FRAME)


def test_extract_pupil():
    with pytest.raises(NotImplementedError):
        extract_pupil(EYE_CROP)


def test_calibrate():
    with pytest.raises(NotImplementedError):
        calibrate(POINTS)


def test_estimate_gaze():
    with pytest.raises(NotImplementedError):
        estimate_gaze(FEATURES, CALIBRATION)


def test_smooth():
    with pytest.raises(NotImplementedError):
        smooth(HISTORY)
