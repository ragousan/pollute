from matplotlib import Path
import pandas as pd
import numpy as np
import seaborn as sns
import folium
from folium.plugins import TimestampedGeoJson
import zipfile
import os


#create dir for flask app
flask_dir = 'templates'
# set the working directory in the container
# project_dir = Path("/code/src")
project_dir = Path("./src")


print("> Unzipping data...")
with zipfile.ZipFile(project_dir / "air_pollute.zip","r") as zip_ref:
    zip_ref.extractall(project_dir)

print("> Unzip done.")

pollutants = {
    7: {
        "notation": "O3",
        "name": "Ozone",
        "limits": np.array([30, 50, 70, 90, 110, 145, 180, 240, 360]),
    },
}


meta = pd.read_csv(project_dir / "GR_2013-2015_metadata.csv", sep="\t")


color_scale = np.array(
    [
        "#053061",
        "#2166ac",
        "#4393c3",
        "#92c5de",
        "#d1e5f0",
        "#fddbc7",
        "#f4a582",
        "#d6604d",
        "#b2182b",
        "#67001f",
    ]
)
sns.palplot(sns.color_palette(color_scale))


#convert date variables to datetime
def load_data(pollutant_ID):
    print("> Loading data...")
    date_vars = ["DatetimeBegin", "DatetimeEnd"]
    filename = "GR_" + str(pollutant_ID) + "_2013-2015_aggregated_timeseries.csv"
    agg_ts = pd.read_csv(
        project_dir / filename,
        sep="\t",
        parse_dates=date_vars,
        date_parser=pd.to_datetime,
    )
    return agg_ts


def clean_data(df):
    print("> Cleaning data...")
    df = df.loc[df.DataAggregationProcess == "P1D", :]
    df = df.loc[df.UnitOfAirPollutionLevel != "count", :]
    ser_avail_days = df.groupby("SamplingPoint").nunique()["DatetimeBegin"]
    df = df.loc[
        df.SamplingPoint.isin(ser_avail_days[ser_avail_days.values >= 1000].index), :
    ]
    vars_to_drop = [
        "AirPollutant",
        "AirPollutantCode",
        "Countrycode",
        "Namespace",
        "TimeCoverage",
        "Validity",
        "Verification",
        "AirQualityStation",
        "AirQualityStationEoICode",
        "DataAggregationProcess",
        "UnitOfAirPollutionLevel",
        "DatetimeEnd",
        "AirQualityNetwork",
        "DataCapture",
        "DataCoverage",
    ]
    df.drop(columns=vars_to_drop, axis="columns", inplace=True)

    dates = list(
        pd.period_range(min(df.DatetimeBegin), max(df.DatetimeBegin), freq="D").values
    )
    samplingpoints = list(df.SamplingPoint.unique())
    new_idx = []
    for sp in samplingpoints:
        for d in dates:
            new_idx.append((sp, np.datetime64(d)))

    df.set_index(keys=["SamplingPoint", "DatetimeBegin"], inplace=True)
    df.sort_index(inplace=True)
    df = df.reindex(new_idx)
    df["AirPollutionLevel"] = df.groupby(level=0).AirPollutionLevel.bfill().fillna(0)
    return df


def color_coding(poll, limits):
    idx = np.digitize(poll, limits, right=True)
    return color_scale[idx]


def prepare_data(df, pollutant_ID):
    print("> Preparing data...")
    df = (
        df.reset_index()
        .merge(meta, how="inner", on="SamplingPoint")
        .set_index("DatetimeBegin")
    )
    df = df.loc[:, ["SamplingPoint", "Latitude", "Longitude", "AirPollutionLevel"]]
    df = (
        df.groupby("SamplingPoint", group_keys=False)
        .resample(rule="M")
        .last()
        .reset_index()
    )
    df["color"] = df.AirPollutionLevel.apply(
        color_coding, limits=pollutants[pollutant_ID]["limits"]
    )
    return df

#convert data to geojson format
def create_geojson_features(df):
    print("> Creating GeoJSON features...")
    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["Longitude"], row["Latitude"]],
            },
            "properties": {
                "time": row["DatetimeBegin"].date().__str__(),
                "style": {"color": row["color"]},
                "icon": "circle",
                "iconstyle": {
                    "fillColor": row["color"],
                    "fillOpacity": 0.8,
                    "stroke": "true",
                    "radius": 7,
                },
            },
        }
        features.append(feature)
    return features


def make_map(features):
    print("> Making map...")
    coords_athens = [37.9838, 23.7275]
    pollution_map = folium.Map(location=coords_athens, control_scale=True, zoom_start=10)

    TimestampedGeoJson(
        {"type": "FeatureCollection", "features": features},
        period="P1M",
        add_last_point=True,
        auto_play=False,
        loop=True,
        max_speed=1,
        loop_button=True,
        date_options="YYYY/MM",
        time_slider_drag_update=True,
    ).add_to(pollution_map)
    print("> Done.")
    return pollution_map


def plot_pollutant(pollutant_ID):
    print(
        "Mapping {} pollution in Greece in 2013-2015".format(
            pollutants[pollutant_ID]["name"]
        )
    )
    df = load_data(pollutant_ID)
    df = clean_data(df)
    df = prepare_data(df, pollutant_ID)
    features = create_geojson_features(df)
    return make_map(features), df


if not os.path.exists(flask_dir):
    os.makedirs(flask_dir)

pollution_map, df = plot_pollutant(7)
pollution_map.save(flask_dir + "/pollution_oz.html")
# pollution_map.save("pollution_oz.html")
pollution_map

#Remove created csv files
csv_removal = os.listdir(project_dir)
for csv_files in csv_removal:
    if csv_files.endswith(".csv"):
        os.remove(os.path.join(project_dir, csv_files))