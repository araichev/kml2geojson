import json

from click.testing import CliRunner

from .context import DATA_DIR
from kml2geojson.cli import k2g


runner = CliRunner()


def test_k2g(tmp_path):
    kml_path = DATA_DIR / "two_layers" / "two_layers.kml"

    # section: writes only geojson when no style type is requested
    out_dir = tmp_path / "no_style"
    result = runner.invoke(
        k2g,
        [
            str(kml_path),
            str(out_dir),
            "--feature-collection-name=main",
        ],
    )

    assert result.exit_code == 0
    assert out_dir.exists()
    assert (out_dir / "main.geojson").exists()
    assert not (out_dir / "style.json").exists()

    with (out_dir / "main.geojson").open() as src:
        geojson = json.load(src)

    assert geojson["type"] == "FeatureCollection"
    assert geojson["name"] == "main"

    # section: writes style file and disambiguated layer filenames
    out_dir = tmp_path / "with_style"
    result = runner.invoke(
        k2g,
        [
            str(kml_path),
            str(out_dir),
            "--style-type=svg",
            "--style-filename=wakawakawaka.json",
            "--separate-folders",
        ],
    )

    assert result.exit_code == 0
    assert out_dir.exists()
    assert (out_dir / "wakawakawaka.json").exists()
    assert (out_dir / "Bingo.geojson").exists()
    assert (out_dir / "Bingo1.geojson").exists()

    with (out_dir / "wakawakawaka.json").open() as src:
        style = json.load(src)

    with (out_dir / "Bingo.geojson").open() as src:
        bingo = json.load(src)

    with (out_dir / "Bingo1.geojson").open() as src:
        bingo1 = json.load(src)

    assert isinstance(style, dict)
    assert bingo["type"] == "FeatureCollection"
    assert bingo["name"] == "%Bingo"
    assert bingo1["type"] == "FeatureCollection"
    assert bingo1["name"] == "#Bingo"
