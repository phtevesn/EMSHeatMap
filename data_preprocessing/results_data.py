import pandas as pd
from add_non_emergency import add_non_emergency
from grid import create_grid_axes, which_grid, other_create_grid_axes

def get_output(path):

    max_in =[37.875808, -122.326536]
    min_in =[37.680158, -122.560339]

    lats, lons = create_grid_axes(min_in[0], max_in[0], min_in[1], max_in[0], 4)

    df = pd.read_parquet(path)
    df = df[
        (df["latitude"] >= min_in[0]) & (df["latitude"] <= max_in[0]) &
        (df["longitude"] >= min_in[1]) & (df["longitude"] <= max_in[1])
    ]

    df["cell"] = df.apply(
        lambda r: which_grid(lats, lons, r["latitude"], r["longitude"]),
        axis = 1
    )

    df = add_non_emergency(df)

    df.to_csv("parsed_emt_data.csv", index=False)