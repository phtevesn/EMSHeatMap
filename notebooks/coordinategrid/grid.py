
from bisect import bisect_right

def create_grid_axes(min_lat, max_lat, min_lon, max_lon, levels):
    def split_range(min_val, max_val, levels):
        if levels == 0:
            return [min_val, max_val]
        mid = (min_val + max_val) / 2
        left = split_range(min_val, mid, levels - 1)
        right = split_range(mid, max_val, levels - 1)
        return left[:-1] + right

    latitudes = split_range(min_lat, max_lat, levels)
    longitudes = split_range(min_lon, max_lon, levels)
    return latitudes, longitudes
    

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
        raise ValueError("Point is outside the grid bounds.")

    # 0-based bin index = rightmost breakpoint ≤ value
    lat_bin0 = min(max(bisect_right(lats, lat_in) - 1, 0), n_lat_cells - 1)
    lon_bin0 = min(max(bisect_right(lons, lon_in) - 1, 0), n_lon_cells - 1)

    # make them 1-based
    lat_idx = lat_bin0 + 1
    lon_idx = lon_bin0 + 1

    # single id (row-major)
    cell_id = (lat_idx - 1) * n_lon_cells + lon_idx
    return lat_idx, lon_idx, cell_id


'''
lats, lons = create_grid_axes(0, 10, 0, 10, 2)
print(lats)
print(lons)

lat_in = 0  # → between 2 and 3 → lat_idx = 2
lon_in = 2.5  # → between 1 and 2 → lon_idx = 1

print(which_grid(lats, lons, lat_in, lon_in))
'''