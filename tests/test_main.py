import xml.dom.minidom as md

import pytest

from .context import DATA_DIR
import kml2geojson.main as m


def _parse(xml: str):
    return md.parseString(xml)


def _read_kml(path):
    with open(path, encoding="utf-8", errors="ignore") as src:
        return md.parseString(src.read())


def test_get():
    # section: returns all matching nodes
    root = _parse(
        """
        <Document>
          <Placemark id="a" />
          <Placemark id="b" />
          <Folder />
        </Document>
        """
    )
    placemarks = m.get(root, "Placemark")
    assert len(placemarks) == 2
    assert placemarks[0].getAttribute("id") == "a"
    assert placemarks[1].getAttribute("id") == "b"

    # section: returns empty list when tag is missing
    assert list(m.get(root, "Missing")) == []


def test_get1():
    # section: returns first matching node
    root = _parse(
        """
        <Document>
          <Placemark id="a" />
          <Placemark id="b" />
        </Document>
        """
    )
    first = m.get1(root, "Placemark")
    assert first is not None
    assert first.getAttribute("id") == "a"

    # section: returns None when tag is missing
    assert m.get1(root, "Missing") is None


def test_attr():
    # section: returns attribute value
    root = _parse('<Placemark id="abc" />')
    node = m.get1(root, "Placemark")
    assert node is not None
    assert m.attr(node, "id") == "abc"

    # section: returns empty string when attribute is missing
    assert m.attr(node, "name") == ""


def test_val():
    # section: strips surrounding whitespace
    root = _parse("<name>  Hello world  </name>")
    assert m.val(root.documentElement) == "Hello world"

    # section: handles cdata content
    root = _parse("<description><![CDATA[ hello ]]></description>")
    assert m.val(root.documentElement) == "hello"

    # section: returns empty string when no text content exists
    root = _parse("<name></name>")
    assert m.val(root.documentElement) == ""


def test_valf():
    # section: parses float text
    root = _parse("<width>2.5</width>")
    assert m.valf(root.documentElement) == 2.5

    # section: returns None for non-float text
    root = _parse("<width>abc</width>")
    assert m.valf(root.documentElement) is None


def test_numarray():
    # section: converts numeric strings to floats
    assert m.numarray(["1", "2.5", "-3"]) == [1.0, 2.5, -3.0]


def test_coords1():
    # section: parses one kml coordinate tuple
    assert m.coords1(" -112.2,36.0,2357 ") == [-112.2, 36.0, 2357.0]


def test_coords():
    # section: parses multiple kml coordinate tuples
    actual = m.coords(
        """
        -112.0,36.1,0
        -113.0,36.0,0
        """
    )
    assert actual == [[-112.0, 36.1, 0.0], [-113.0, 36.0, 0.0]]


def test_gx_coords1():
    # section: parses one gx coordinate tuple
    assert m.gx_coords1("-113.0 36.0 0") == [-113.0, 36.0, 0.0]


def test_gx_coords():
    # section: extracts gx track coordinates and timestamps
    root = _parse(
        """
        <gx:Track xmlns:gx="http://www.google.com/kml/ext/2.2">
          <when>2020-01-01T00:00:00Z</when>
          <when>2020-01-01T00:01:00Z</when>
          <gx:coord>-113.0 36.0 0</gx:coord>
          <gx:coord>-113.1 36.1 1</gx:coord>
        </gx:Track>
        """
    )
    actual = m.gx_coords(root.documentElement)
    assert actual == {
        "coordinates": [[-113.0, 36.0, 0.0], [-113.1, 36.1, 1.0]],
        "times": ["2020-01-01T00:00:00Z", "2020-01-01T00:01:00Z"],
    }


def test_disambiguate():
    # section: leaves unique names unchanged
    assert m.disambiguate(["a", "b"]) == ["a", "b"]

    # section: appends mark repeatedly to duplicates
    assert m.disambiguate(["sing", "song", "sing", "sing"]) == [
        "sing",
        "song",
        "sing1",
        "sing11",
    ]

    # section: supports custom mark
    assert m.disambiguate(["x", "x"], mark="_") == ["x", "x_"]


def test_to_filename():
    # section: strips unsafe characters and normalizes spaces
    assert m.to_filename("% A dbla'{-+)(ç? ") == "A_dbla-ç"

    # section: keeps dots dashes and underscores
    assert m.to_filename("a b-c_d.txt") == "a_b-c_d.txt"


def test_build_rgb_and_opacity():
    # section: parses 8-char kml color
    assert m.build_rgb_and_opacity("ee001122") == ("#221100", 0.93)

    # section: parses 6-char color
    assert m.build_rgb_and_opacity("001122") == ("#221100", 1)

    # section: parses 3-char color
    assert m.build_rgb_and_opacity("abc") == ("#cba", 1)

    # section: ignores leading hash
    assert m.build_rgb_and_opacity("#ee001122") == ("#221100", 0.93)


def test_build_svg_style():
    # section: maps polygon and line style fields
    root = _parse(
        """
        <Document>
          <Style id="poly">
            <PolyStyle>
              <color>ee001122</color>
              <fill>1</fill>
              <outline>0</outline>
            </PolyStyle>
            <LineStyle>
              <color>ff334455</color>
              <width>2</width>
            </LineStyle>
          </Style>
          <Style id="icon">
            <IconStyle>
              <Icon><href>https://example.com/pin.png</href></Icon>
            </IconStyle>
          </Style>
        </Document>
        """
    )
    actual = m.build_svg_style(root)
    assert actual["#poly"]["fill"] == "#221100"
    assert actual["#poly"]["fill-opacity"] == 0.93
    assert actual["#poly"]["stroke"] == "#554433"
    assert actual["#poly"]["stroke-opacity"] == 1.0
    assert actual["#poly"]["stroke-width"] == 2.0
    assert actual["#icon"] == {"iconUrl": "https://example.com/pin.png"}


def test_build_leaflet_style():
    # section: maps polygon and line style fields
    root = _parse(
        """
        <Document>
          <Style id="poly">
            <PolyStyle>
              <color>ee001122</color>
              <fill>1</fill>
              <outline>0</outline>
            </PolyStyle>
            <LineStyle>
              <color>ff334455</color>
              <width>2</width>
            </LineStyle>
          </Style>
          <Style id="icon">
            <IconStyle>
              <Icon><href>https://example.com/pin.png</href></Icon>
            </IconStyle>
          </Style>
        </Document>
        """
    )
    actual = m.build_leaflet_style(root)
    assert actual["#poly"]["fillColor"] == "#221100"
    assert actual["#poly"]["fillOpacity"] == 0.93
    assert actual["#poly"]["color"] == "#554433"
    assert actual["#poly"]["opacity"] == 1.0
    assert actual["#poly"]["weight"] == 2.0
    assert actual["#icon"] == {"iconUrl": "https://example.com/pin.png"}


def test_build_geometry():
    # section: builds point geometry
    root = _parse(
        """
        <Placemark>
          <Point><coordinates>-113.0,36.0,0</coordinates></Point>
        </Placemark>
        """
    )
    actual = m.build_geometry(root.documentElement)
    assert actual["geoms"] == [{"type": "Point", "coordinates": [-113.0, 36.0, 0.0]}]
    assert actual["times"] == []

    # section: builds polygon geometry
    root = _parse(
        """
        <Placemark>
          <Polygon>
            <outerBoundaryIs>
              <LinearRing>
                <coordinates>
                  -1,1,0 -2,2,0 -3,3,0 -1,1,0
                </coordinates>
              </LinearRing>
            </outerBoundaryIs>
          </Polygon>
        </Placemark>
        """
    )
    actual = m.build_geometry(root.documentElement)
    assert actual["geoms"][0]["type"] == "Polygon"
    assert actual["geoms"][0]["coordinates"] == [
        [[-1.0, 1.0, 0.0], [-2.0, 2.0, 0.0], [-3.0, 3.0, 0.0], [-1.0, 1.0, 0.0]]
    ]

    # section: gx track becomes linestring and captures times
    root = _parse(
        """
        <Placemark xmlns:gx="http://www.google.com/kml/ext/2.2">
          <gx:Track>
            <when>2020-01-01T00:00:00Z</when>
            <gx:coord>-113.0 36.0 0</gx:coord>
          </gx:Track>
        </Placemark>
        """
    )
    actual = m.build_geometry(root.documentElement)
    assert actual["geoms"][0]["type"] == "LineString"
    assert actual["geoms"][0]["coordinates"] == [[-113.0, 36.0, 0.0]]
    assert actual["times"] == [["2020-01-01T00:00:00Z"]]

    # section: multigeometry recurses to child container
    root = _parse(
        """
        <Placemark>
          <MultiGeometry>
            <Point><coordinates>-113.0,36.0,0</coordinates></Point>
            <LineString><coordinates>-113.0,36.0,0 -114.0,37.0,0</coordinates></LineString>
          </MultiGeometry>
        </Placemark>
        """
    )
    actual = m.build_geometry(root.documentElement)
    assert sorted(geom["type"] for geom in actual["geoms"]) == ["LineString", "Point"]


def test_build_feature():
    # section: returns none when there is no geometry
    root = _parse("<Placemark><name>Empty</name></Placemark>")
    assert m.build_feature(root.documentElement) is None

    # section: builds feature with properties styles extended data timespan and id
    root = _parse(
        """
        <Placemark id="pm1">
          <name>Example</name>
          <description>Desc</description>
          <styleUrl>style-1</styleUrl>
          <ExtendedData>
            <Data name="foo"><value>bar</value></Data>
            <SimpleData name="baz">qux</SimpleData>
          </ExtendedData>
          <TimeSpan>
            <begin>2020-01-01</begin>
            <end>2020-01-02</end>
          </TimeSpan>
          <LineStyle>
            <color>ff334455</color>
            <width>2</width>
          </LineStyle>
          <PolyStyle>
            <color>ee001122</color>
            <fill>1</fill>
            <outline>0</outline>
          </PolyStyle>
          <Point><coordinates>-113.0,36.0,0</coordinates></Point>
        </Placemark>
        """
    )
    actual = m.build_feature(root.documentElement)
    assert actual is not None
    assert actual["id"] == "pm1"
    assert actual["geometry"]["type"] == "Point"
    assert actual["properties"]["name"] == "Example"
    assert actual["properties"]["description"] == "Desc"
    assert actual["properties"]["styleUrl"] == "#style-1"
    assert actual["properties"]["foo"] == "bar"
    assert actual["properties"]["baz"] == "qux"
    assert actual["properties"]["timeSpan"] == {
        "begin": "2020-01-01",
        "end": "2020-01-02",
    }
    assert actual["properties"]["fill"] == "#221100"
    assert actual["properties"]["fill-opacity"] == 0.93
    assert actual["properties"]["stroke"] == "#554433"
    assert actual["properties"]["stroke-opacity"] == 1.0
    assert actual["properties"]["stroke-width"] == 2.0

    # section: builds geometrycollection for multiple geometries
    root = _parse(
        """
        <Placemark>
          <Point><coordinates>-113.0,36.0,0</coordinates></Point>
          <LineString><coordinates>-113.0,36.0,0 -114.0,37.0,0</coordinates></LineString>
        </Placemark>
        """
    )
    actual = m.build_feature(root.documentElement)
    assert actual is not None
    assert actual["geometry"]["type"] == "GeometryCollection"
    assert len(actual["geometry"]["geometries"]) == 2

    # section: flattens one track time list into properties.times
    root = _parse(
        """
        <Placemark xmlns:gx="http://www.google.com/kml/ext/2.2">
          <gx:Track>
            <when>2020-01-01T00:00:00Z</when>
            <when>2020-01-01T00:01:00Z</when>
            <gx:coord>-113.0 36.0 0</gx:coord>
            <gx:coord>-113.1 36.1 1</gx:coord>
          </gx:Track>
        </Placemark>
        """
    )
    actual = m.build_feature(root.documentElement)
    assert actual is not None
    assert actual["properties"]["times"] == [
        "2020-01-01T00:00:00Z",
        "2020-01-01T00:01:00Z",
    ]


def test_build_feature_collection():
    # section: includes only placemarks that produce features
    root = _parse(
        """
        <Folder>
          <Placemark><name>Empty</name></Placemark>
          <Placemark>
            <name>Point A</name>
            <Point><coordinates>-113.0,36.0,0</coordinates></Point>
          </Placemark>
        </Folder>
        """
    )
    actual = m.build_feature_collection(root.documentElement, name="layer-a")
    assert actual["type"] == "FeatureCollection"
    assert actual["name"] == "layer-a"
    assert len(actual["features"]) == 1
    assert actual["features"][0]["properties"]["name"] == "Point A"


def test_build_layers():
    # section: builds one layer per folder with geodata
    root = _read_kml(DATA_DIR / "two_layers" / "two_layers.kml")
    actual = m.build_layers(root)
    assert [layer["name"] for layer in actual] == ["%Bingo", "#Bingo"]

    # section: raw layer names can be sanitized and disambiguated for filenames
    stems = m.disambiguate(m.to_filename(layer["name"]) for layer in actual)
    assert stems == ["Bingo", "Bingo1"]

    # section: falls back to root when no folders exist
    root = _parse(
        """
        <kml>
          <Document>
            <name>root-layer</name>
            <Placemark>
              <Point><coordinates>-113.0,36.0,0</coordinates></Point>
            </Placemark>
          </Document>
        </kml>
        """
    )
    actual = m.build_layers(root)
    assert len(actual) == 1
    assert actual[0]["name"] == "root-layer"

    # section: can skip disambiguation
    root = _parse(
        """
        <Document>
          <Folder>
            <name>A</name>
            <Placemark><Point><coordinates>-1,1,0</coordinates></Point></Placemark>
          </Folder>
          <Folder>
            <name>A</name>
            <Placemark><Point><coordinates>-2,2,0</coordinates></Point></Placemark>
          </Folder>
        </Document>
        """
    )
    actual = m.build_layers(root, disambiguate_names=False)
    assert [layer["name"] for layer in actual] == ["A", "A"]


def test_convert():
    kml_path = DATA_DIR / "two_layers" / "two_layers.kml"

    # section: converts from path into one named feature collection
    actual = m.convert(kml_path, feature_collection_name="main")
    assert len(actual) == 1
    assert actual[0]["type"] == "FeatureCollection"
    assert actual[0]["name"] == "main"

    # section: returns separate folder layers with raw folder names
    actual = m.convert(kml_path, separate_folders=True)
    assert [layer["name"] for layer in actual] == ["%Bingo", "#Bingo"]

    # section: raw layer names can later be sanitized and disambiguated for filenames
    stems = m.disambiguate(m.to_filename(layer["name"]) for layer in actual)
    assert stems == ["Bingo", "Bingo1"]

    # section: prepends svg style dict when requested
    actual = m.convert(kml_path, style_type="svg", separate_folders=True)
    style, *layers = actual
    assert isinstance(style, dict)
    assert [layer["name"] for layer in layers] == ["%Bingo", "#Bingo"]

    # section: prepends leaflet style dict when requested
    actual = m.convert(kml_path, style_type="leaflet")
    style, *layers = actual
    assert isinstance(style, dict)
    assert len(layers) == 1

    # section: rejects unsupported style type
    with pytest.raises(ValueError, match="style type must be one of"):
        m.convert(kml_path, style_type="not-a-style")
