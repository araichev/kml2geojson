import json
import pathlib as pl

import click

import kml2geojson.main as m


@click.command(short_help="Convert KML to GeoJSON")
@click.argument("kml_path_or_buffer", type=click.Path(exists=True))
@click.argument("output_dir")
@click.option("-fcn", "--feature-collection-name", default="main")
@click.option("-st", "--style-type", type=click.Choice(m.STYLE_TYPES), default=None)
@click.option("-sf", "--style-filename", default="style.json")
@click.option("-f", "--separate-folders", is_flag=True, default=False)
def k2g(
    kml_path_or_buffer,
    output_dir,
    feature_collection_name,
    style_type,
    style_filename,
    separate_folders,
):
    """
    Given a path to a KML file or given a KML file, convert it to a a GeoJSON
    FeatureCollection with name = ``--feature_collection_name`` (which defaults
    to 'main') and save the GeoJSON to the file '.geojson' in the given output
    directory.

    If ``--separate_folders``, then create several GeoJSON files, one for each
    folder in the KML file that contains geodata or that has a descendant node
    that contains geodata. Warning: this can produce GeoJSON files with the
    same geodata in case the KML file has nested folders with geodata.

    If ``--style_type`` is specified, then also build a JSON style file of the
    given style type and save it to the output directory under the file name
    given by ``--style_filename`` which defaults to "style.json".
    """
    result = m.convert(
        kml_path_or_buffer,
        style_type=style_type,
        separate_folders=separate_folders,
        feature_collection_name=feature_collection_name,
    )

    output_dir = pl.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir = output_dir.resolve()

    if style_type is not None:
        style, *layers = result
        with (output_dir / style_filename).open("w") as tgt:
            json.dump(style, tgt)
    else:
        layers = list(result)

    stems = m.disambiguate(m.to_filename(layer["name"]) for layer in layers)
    filenames = [f"{stem}.geojson" for stem in stems]

    for layer, filename in zip(layers, filenames):
        with (output_dir / filename).open("w") as tgt:
            json.dump(layer, tgt)
