import pytest
import argparse
from dlt.cli import slugify, semitones_type


class TestSlugify:
    def test_basic_title_positive_semitones(self):
        assert slugify("Bohemian Rhapsody", 5) == "bohemian-rhapsody-+5st.mp3"

    def test_basic_title_negative_semitones(self):
        assert slugify("Bohemian Rhapsody", -3) == "bohemian-rhapsody--3st.mp3"

    def test_zero_semitones(self):
        assert slugify("My Song", 0) == "my-song-0st.mp3"

    def test_special_chars_stripped(self):
        assert slugify("Hey Jude!", 2) == "hey-jude-+2st.mp3"

    def test_slashes_stripped(self):
        assert slugify("AC/DC", 1) == "acdc-+1st.mp3"

    def test_multiple_spaces_collapsed_to_single_hyphen(self):
        assert slugify("Hello   World", 1) == "hello-world-+1st.mp3"


class TestSemitonesType:
    def test_accepts_positive_integer_string(self):
        assert semitones_type("5") == 5

    def test_accepts_negative_integer_string(self):
        assert semitones_type("-3") == -3

    def test_accepts_plus_prefix(self):
        assert semitones_type("+5") == 5

    def test_accepts_boundary_values(self):
        assert semitones_type("-12") == -12
        assert semitones_type("12") == 12

    def test_rejects_out_of_range(self):
        with pytest.raises(argparse.ArgumentTypeError, match="-12 and \\+12"):
            semitones_type("13")

    def test_rejects_float_string(self):
        with pytest.raises(argparse.ArgumentTypeError):
            semitones_type("2.5")
