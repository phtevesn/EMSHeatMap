import pandas as pd
import numpy as np
from bisect import bisect_right

def old_create_grid_axes(min_lat, max_lat, min_lon, max_lon, levels):
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
    #return lat_idx, lon_idx, cell_id
    return cell_id


def test():
    min_in = [37.695916, -122.532444]
    max_in = [37.837044, -122.358207]
    lats, lons = create_grid_axes(min_in[0], max_in[0], min_in[1], max_in[1], 4)
    print(lats)
    print(lons)
    cell = which_grid(lats, lons, (min_in[0]+max_in[0])/2, (min_in[1]+max_in[1])/2)
    print(cell)
    cell = which_grid(lats, lons, (min_in[0]+min_in[0])/2, (min_in[1]+min_in[1])/2)
    print(cell)
    cell = which_grid(lats, lons, (max_in[0]+max_in[0])/2, (max_in[1]+max_in[1])/2)
    print(cell)
    cell = which_grid(lats, lons, (max_in[0]+max_in[0]+1)/2, (max_in[1]+max_in[1]+1)/2)
    print(cell)


def find_cells(df: pd.DataFrame, num_cols, num_rows):
    min_in = [min(df['latitude'].unique().tolist()), min(df['longitude'].unique().tolist())]
    max_in = [max(df['latitude'].unique().tolist()), max(df['longitude'].unique().tolist())]

    lats, lons = create_grid_axes(min_in[0], max_in[0], min_in[1], max_in[1], num_cols, num_rows)

    df['cell'] = df.apply(
        lambda row: which_grid(lats, lons, row['latitude'], row['longitude']),
        axis=1
    )

    return df, lats, lons


def grid_to_coords(cell_id, lats, lons):
    """
    Given a 1-based grid cell ID (as returned by which_grid),
    return the bottom-left coordinate (lat, lon).
    """
    n_lat_cells = len(lats) - 1
    n_lon_cells = len(lons) - 1

    # convert 1-based cell_id back to 0-based grid indices
    cell_id -= 1
    lat_bin0 = cell_id // n_lon_cells  # row index (0-based)
    lon_bin0 = cell_id %  n_lon_cells  # col index (0-based)

    # bottom-left corner
    lat_bl = lats[lat_bin0]
    lon_bl = lons[lon_bin0]

    '''
    df["latitude"] = df.apply(
    lambda r: grid_to_coords(r["cell_id"], lats, lons)[0],
    axis=1
    )
    df["longitude"] = df.apply(
        lambda r: grid_to_coords(r["cell_id"], lats, lons)[1],
        axis=1
    )
    '''
    return lat_bl, lon_bl
