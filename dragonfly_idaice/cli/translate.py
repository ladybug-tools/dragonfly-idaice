"""honeybee idaice translation commands."""
import click
import sys
import os
import logging
import base64
import tempfile
import uuid

from honeybee.units import parse_distance_string
from dragonfly.model import Model

from dragonfly_idaice.writer import model_to_idm as writer_model_to_idm

_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Dragonfly JSON files to IES files.')
def translate():
    pass


@translate.command('model-to-idm')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--project-info', '-pi', help='Full path to a ladybug ProjectInfo JSON that '
    'describes criteria about the project site. When specified, this will result in '
    'the location and north_angle written into the IDM. If a weather file has been '
    'associated with the project_info, a .PRN file will be written from the EPW and '
    'will be referenced within the IDM.', default=None, show_default=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option(
    '--multiplier/--full-geometry', ' /-fg', help='Flag to note if the '
    'multipliers on each Building story will be passed along to the '
    'generated Room objects or if full geometry objects should be '
    'written for each story in the building.', default=True, show_default=True)
@click.option(
    '--plenum/--no-plenum', '-p/-np', help='Flag to indicate whether '
    'ceiling/floor plenum depths assigned to Room2Ds should generate '
    'distinct 3D Rooms in the translation.', default=True, show_default=True)
@click.option(
    '--wall-thickness', '-t', help='Maximum thickness of the interior walls. This '
    'can include the units of the distance (eg. 1.5ft) or, if no units are provided, '
    'the value will be assumed to be in meters (the native units of IDA-ICE). '
    'This value will be used to generate the IDA-ICE building body, which dictates '
    'which Room Faces are exterior vs. interior. This is necessary because IDA-ICE '
    'expects the input model to have gaps between the rooms that represent '
    'the wall thickness. This value input here must be smaller than the smallest Room '
    'that is expected in resulting IDA-ICE model and it should never be greater '
    'than 0.5m in order to avoid creating invalid building bodies for IDA-ICE. '
    'For models where the walls are touching each other, use a value of 0.',
    type=str, default='0.4m', show_default=True
)
@click.option(
    '--adjacency-distance', '-a', help='Maximum distance between interior Apertures '
    'and Doors at which they are considered adjacent. This can include the units '
    'of the distance (eg. 1.5ft) or, if no units are provided, the value will be '
    'assumed to be in meters (the native units of IDA-ICE). This is used to ensure '
    'that only one interior Aperture of an adjacent pair is written into the '
    'IDM. This value should typically be around the --wall-thickness and should '
    'ideally not be thicker than 0.5m. But it may be undesirable to set this to '
    'zero (like some cases of --wall-thickness), particularly when the adjacent '
    'interior geometries are not perfectly matching one another.',
    type=str, default='0.4m', show_default=True
)
@click.option(
    '--face-rename-format', '-fn', help='Optional text for the pattern '
    'with which faces will be renamed. Any property on the honeybee Face class '
    'may be used (eg. gbxml_str) and each property should be put in curly '
    'brackets. Nested properties can be specified by using "." to denote '
    'nesting levels (eg. properties.energy.construction.display_name). '
    'Functions that return string outputs can also be passed here as long '
    'as these functions defaults specified for all arguments.',
    type=str, show_default=True,
    default="{parent.display_name} - {type} - {cardinal_abbrev}")
@click.option(
    '--subface-rename-format', '-sfn', help='Optional text for the pattern '
    'with which apertures and doors will be renamed. Any property that exists '
    'on both the honeybee Aperture and honeybee Door class may be used '
    '(eg. type) and each property should be put in curly brackets. Nested '
    'properties can be specified by using "." to denote nesting levels '
    '(eg. properties.energy.construction.display_name). Functions that '
    'return string outputs can also be passed here as long as these '
    'functions defaults specified for all arguments.',
    type=str, show_default=True, default="{type}")
@click.option(
    '--name-decimal-count', '-dc', help='An integer to set the number of '
    'decimal places that appear in face and sub-face names for all numerical '
    'properties. If None, the number of decimal places are determined by the '
    'model tolerance.', type=int, default=None, show_default=True)
@click.option(
    '--include-units-in-name/--exclude-units-in-name', ' /-xu', help='Flag '
    'to note whether the units should be excluded from all length, area '
    'and volume attributes.', default=True, show_default=True)
@click.option(
    '--output-file', '-o', help='Optional IDM file path to output the IDM string '
    'of the translation. By default this will be printed out to stdout.',
    type=click.File('w'), default='-', show_default=True)
def model_to_idm_cli(
    model_file, project_info,
    multiplier, plenum, wall_thickness, adjacency_distance,
    face_rename_format, subface_rename_format, name_decimal_count,
    include_units_in_name, output_file
):
    """Translate a Dragonfly Model JSON file to an IES-VE IDM file.

    \b
    Args:
        model_json: Full path to a Model JSON file (DFJSON) or a Model pkl (DFpkl) file.
    """
    try:
        full_geometry = not multiplier
        no_plenum = not plenum
        exclude_units_in_name = not include_units_in_name
        model_to_idm(
            model_file, project_info, full_geometry, no_plenum,
            wall_thickness, adjacency_distance,
            face_rename_format, subface_rename_format, name_decimal_count,
            exclude_units_in_name, output_file
        )
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_idm(
    model_file, project_info=None, full_geometry=False, no_plenum=False,
    wall_thickness='0.4m', adjacency_distance='0.4m',
    face_rename_format='{parent.display_name} - {type} - {cardinal_abbrev}',
    subface_rename_format='{type}', name_decimal_count=None, exclude_units_in_name=False,
    output_file=None,
    multiplier=True, plenum=True,  include_units_in_name=True
):
    """Translate a Model file to an IES-VE IDM string.

    Args:
        model_file: Full path to a Model JSON file (DFJSON) or a Model pkl (DFpkl) file.
        project_info: Full path to a ladybug ProjectInfo JSON that describes
            criteria about the project site. When specified, this will result in
            the location and north_angle written into the IDM. If a weather file
            has been associated with the project_info, a .PRN file will be written
            from the EPW and will be referenced within the IDM.
        full_geometry: Boolean to note if the multipliers on each Building story
            will be passed along to the generated Honeybee Room objects or if
            full geometry objects should be written for each story in the
            building. (Default: False).
        no_plenum: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should generate distinct 3D Rooms in the
            translation. (Default: False).
        face_rename_format: An optional text string for the pattern with which
            faces will be renamed. Any property on the honeybee Face class may be
            used (eg. gbxml_str) and each property should be put in curly brackets.
            Nested properties can be specified by using "." to denote nesting levels
            (eg. properties.energy.construction.display_name). Functions that return
            string outputs can also be passed here as long as these functions
            defaults specified for all arguments. If None, the names will match the
            identifiers. (Default: "{parent.display_name} - {type} - {cardinal_abbrev}").
        subface_rename_format: An optional text string for the pattern with which
            apertures and doors will be renamed. Bear in mind that IDA ICE automatically
            concatenates the name of the parent Face to the opening and so the
            format string input here should only be for after the parent Face name.
            Any property that exists on both the honeybee Aperture and honeybee
            Door class may be used (eg. type) and each property should be put in curly
            brackets. Nested properties can be specified by using "." to denote nesting
            levels (eg. properties.energy.construction.display_name). Functions that
            return string outputs can also be passed here as long as these
            functions defaults specified for all arguments. If None, the names
            will match the identifiers. (Default: "{type}").
        name_decimal_count: An integer to set the number of decimal places that
            appear in face and opening names for all numerical properties.
            If None, the number of decimal places are determined by the
            model tolerance. (Default: None).
        exclude_units_in_name: Boolean for wether the units should be
            excluded from all length, area and volume attributes. (Default: False).
        output_file: Optional IDM file to output the IDM string of the translation.
            If None, the string will be returned from this method. (Default: None).
    """
    # convert distance strings to floats
    wall_thickness = parse_distance_string(str(wall_thickness), 'Meters')
    adjacency_distance = parse_distance_string(str(adjacency_distance), 'Meters')
    north_angle = 0 if project_info is None else project_info.north_angle

    # translate the Model to IDM
    model = Model.from_file(model_file)
    multiplier = not full_geometry
    if isinstance(output_file, str):
        folder, name = os.path.dirname(output_file), os.path.basename(output_file)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        writer_model_to_idm(
            model, folder=folder, name=name, project_info=project_info,
            use_multiplier=multiplier, exclude_plenums=no_plenum,
            max_int_wall_thickness=wall_thickness,
            max_adjacent_sub_face_dist=adjacency_distance,
            face_rename_format=face_rename_format, subface_rename_format=subface_rename_format,
            name_decimal_count=name_decimal_count, exclude_units_in_name=exclude_units_in_name
        )
    else:
        if output_file is None or output_file.name == '<stdout>':  # get a temporary file
            out_file = str(uuid.uuid4())[:6]
            out_folder = tempfile.gettempdir()
        else:
            out_folder, out_file = os.path.split(output_file.name)
        idm_file = writer_model_to_idm(
            model, folder=out_folder, name=out_file, project_info=project_info,
            use_multiplier=multiplier, exclude_plenums=no_plenum,
            max_int_wall_thickness=wall_thickness,
            max_adjacent_sub_face_dist=adjacency_distance,
            face_rename_format=face_rename_format, subface_rename_format=subface_rename_format,
            name_decimal_count=name_decimal_count, exclude_units_in_name=exclude_units_in_name
        )
        if output_file is None or output_file.name == '<stdout>':  # load file contents
            with open(idm_file, 'rb') as of:  # IDM can only be read as binary
                f_contents = of.read()
            b = base64.b64encode(f_contents)
            base64_string = b.decode('utf-8')
            if output_file is None:
                return base64_string
            else:
                output_file.write(base64_string)
