# this is just scaffolding for now
# every method raises NotImplementedError for now; test_pipeline.py pins the API


def detect_eyes(frame):
    #finds eyes in frame. returns [(x, y, w, h), (x, y, w, h)]
    raise NotImplementedError


def extract_pupil(eye_crop):
    #find the pupil center in an eye picture. returns (x, y) in crop coords
    raise NotImplementedError


def calibrate(reference_points):
    #maps eye features to screen coords
    raise NotImplementedError


def estimate_gaze(eye_features, calibration):
    #predict where the user is looking. returns (x, y) screen coords
    raise NotImplementedError


def smooth(history):
    # filter recent predictions to reduce jitter. returns (x, y)
    raise NotImplementedError
