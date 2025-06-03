# time_utils.py
from constants import SEGMENT_DURATION_HOURS, NUM_TIME_SEGMENTS

def time_to_segment(timestamp, segment_duration=SEGMENT_DURATION_HOURS):
    return (timestamp // (segment_duration * 3600)) % NUM_TIME_SEGMENTS
