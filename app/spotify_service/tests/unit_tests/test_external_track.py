import pytest

from app.spotify_service.models.external_track import ExternalTrack


def test_external_track_equality():
    # Create two ExternalTrack instances with the same attributes
    track1 = ExternalTrack(track_name="track_a", artist="artist_a")
    track2 = ExternalTrack(track_name="track_a", artist="artist_a")

    # Assert that they are equal
    assert track1 == track2

def test_external_track_inequality():
    # Create two ExternalTrack instances with different attributes
    track1 = ExternalTrack(track_name="track_a", artist="artist_a")
    track2 = ExternalTrack(track_name="track_b", artist="artist_b")

    # Assert that they are not equal
    assert track1 != track2

def test_external_track_hashing():
    # Create two ExternalTrack instances with the same attributes
    track1 = ExternalTrack(track_name="track_a", artist="artist_a")
    track2 = ExternalTrack(track_name="track_a", artist="artist_a")

    # Create a set and add the tracks
    track_set = {track1}

    # Assert that the second track can be added and is recognized as equal
    assert track2 in track_set

def test_external_track_raises_value_error_on_non_external_track():
    # Create an ExternalTrack instance
    track = ExternalTrack(track_name="track_a", artist="artist_a")

    # Attempt to compare it with a non-ExternalTrack instance
    with pytest.raises(ValueError, match=r"not an instance of ExternalTrack"):
        _ = track == "not a track"
