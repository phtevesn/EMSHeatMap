import unittest
import numpy as np
from bisect import bisect_right


def create_grid_axes(min_lat, max_lat, min_lon, max_lon, num_lon_cells, num_lat_cells):
    """
    Creates grid axes with a custom number of cells for each dimension.
    """
    # For N cells, you need N+1 boundary lines.
    # np.linspace creates evenly spaced numbers over a specified interval.
    latitudes = np.linspace(min_lat, max_lat, num_lat_cells + 1)
    longitudes = np.linspace(min_lon, max_lon, num_lon_cells + 1)

    # Convert numpy arrays to lists to match the input type for which_grid
    return latitudes.tolist(), longitudes.tolist()


def which_grid(lats, lons, lat_in, lon_in):
    # ensure ascending (in case you built them descending)
    if lats[0] > lats[-1]:
        lats = list(reversed(lats))
    if lons[0] > lons[-1]:
        lons = list(reversed(lons))

    n_lat_cells = len(lats) - 1
    n_lon_cells = len(lons) - 1

    # (optional) bounds check
    if not (lats[0] <= lat_in <= lats[-1]) or not (lons[0] <= lon_in <= lons[-1]):
        print(lats[0], "<=", lat_in, "\n", lons[0], "<=", lon_in, "<=", lons[-1])
        raise ValueError("Point is outside the grid bounds.")

    # 0-based bin index = rightmost breakpoint ≤ value
    lat_bin0 = min(max(bisect_right(lats, lat_in) - 1, 0), n_lat_cells - 1)
    lon_bin0 = min(max(bisect_right(lons, lon_in) - 1, 0), n_lon_cells - 1)

    # make them 1-based
    lat_idx = lat_bin0 + 1
    lon_idx = lon_bin0 + 1

    # single id (row-major)
    cell_id = (lat_idx - 1) * n_lon_cells + lon_idx
    # return lat_idx, lon_idx, cell_id
    return cell_id


# --- Test Class ---
class TestGridFunctions(unittest.TestCase):

    def setUp(self):
        """Set up a common grid for all tests."""
        # This creates a 4x4 grid around Sacramento, CA
        self.min_lat, self.max_lat = 38.0, 39.0
        self.min_lon, self.max_lon = -122.0, -121.0
        self.num_lat_cells = 4
        self.num_lon_cells = 4

        self.lats, self.lons = create_grid_axes(
            self.min_lat, self.max_lat,
            self.min_lon, self.max_lon,
            self.num_lon_cells, self.num_lat_cells
        )
        # Expected latitudes: [38.0, 38.25, 38.5, 38.75, 39.0]
        # Expected longitudes: [-122.0, -121.75, -121.5, -121.25, -121.0]

    def test_create_grid_axes(self):
        """Test the grid axis creation."""
        self.assertEqual(len(self.lats), self.num_lat_cells + 1)
        self.assertEqual(len(self.lons), self.num_lon_cells + 1)
        self.assertAlmostEqual(self.lats[0], self.min_lat)
        self.assertAlmostEqual(self.lats[-1], self.max_lat)
        self.assertIsInstance(self.lats, list)
        self.assertIsInstance(self.lons, list)

    def test_which_grid_center(self):
        """Test a point in the center of cell #10."""
        # This point is in the 3rd latitude bin (index 2) and 2nd longitude bin (index 1)
        # Lat Idx = 3, Lon Idx = 2
        # Cell ID = (3-1) * 4 + 2 = 10
        lat_in, lon_in = 38.6, -121.6
        self.assertEqual(which_grid(self.lats, self.lons, lat_in, lon_in), 10)

    def test_which_grid_on_boundary(self):
        """Test a point exactly on a boundary."""
        # A point on the boundary is placed in the cell to its "upper-right"
        # based on bisect_right's behavior.
        # This point is on the lower-left corner of cell 11.
        lat_in, lon_in = 38.5, -121.5
        self.assertEqual(which_grid(self.lats, self.lons, lat_in, lon_in), 11)  # Corrected expectation

    def test_which_grid_corners(self):
        """Test points in the first and last cells."""
        # First cell (ID 1)
        lat_in_first, lon_in_first = 38.1, -121.9
        self.assertEqual(which_grid(self.lats, self.lons, lat_in_first, lon_in_first), 1)

        # Last cell (ID 16)
        lat_in_last, lon_in_last = 38.9, -121.1
        self.assertEqual(which_grid(self.lats, self.lons, lat_in_last, lon_in_last), 16)

    def test_which_grid_out_of_bounds(self):
        """Test that points outside the grid raise a ValueError."""
        with self.assertRaises(ValueError):
            # Latitude too low
            which_grid(self.lats, self.lons, 37.0, -121.5)
        with self.assertRaises(ValueError):
            # Longitude too high
            which_grid(self.lats, self.lons, 38.5, -120.0)

    def test_which_grid_reversed_axes(self):
        """Test that the function works with descending axis lists."""
        lats_rev = list(reversed(self.lats))
        lons_rev = list(reversed(self.lons))
        lat_in, lon_in = 38.6, -121.6
        # Should still be cell #10
        self.assertEqual(which_grid(lats_rev, lons_rev, lat_in, lon_in), 10)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)