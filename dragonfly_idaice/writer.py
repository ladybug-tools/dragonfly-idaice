# coding: utf-8
"""Write a IDM file from a Dragonfly model."""
from __future__ import division

from honeybee.config import folders
from honeybee.typing import readable_short_name
from honeybee_idaice.writer import model_to_idm as hb_model_to_idm


def model_to_idm(
    model, name=None, folder=None, project_info=None,
    use_multiplier=True, exclude_plenums=False,
    max_int_wall_thickness=0.4, max_adjacent_sub_face_dist=0.4,
    face_rename_format='{parent.display_name} - {type} - {cardinal_abbrev}',
    subface_rename_format='{type}', name_decimal_count=None, exclude_units_in_name=False
):
    """Generate an IDA-ICE IDM string from a Dragonfly Model.

    Args:
        model: A dragonfly Model.
        name: Output IDM file name. If None, the Model display name will be used.
        folder: A text string for the directory where the DFJSON will be written.
            If unspecified, the default simulation folder will be used. This
            is usually at "C:\\Users\\USERNAME\\simulation" on Windows.
        project_info: An optional ladybug ProjectInfo object that describes criteria
            about the project site. When specified, this will result in the location
            and north_angle written into the IDM. If a weather file has been associated
            with the project_info, a .PRN file will be written from the EPW and
            will be referenced within the IDM. (Default: None).
        use_multiplier: Boolean to note whether the multipliers on each Building
            story will be passed along to the Room objects or if full geometry
            objects should be written for each repeated story in the
            building. (Default: True).
        exclude_plenums: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should generate distinct 3D Rooms in the
            translation. (Default: False).
        max_int_wall_thickness: Maximum thickness of the interior wall in meters. IDA-ICE
            expects the input model to have a gap between the rooms that represents
            the wall thickness. This value must be smaller than the smallest Room
            that is expected in resulting IDA-ICE model and it should never be greater
            than 0.5 in order to avoid creating invalid building bodies for IDA-ICE.
            For models where the walls are touching each other, use a value
            of 0. (Default: 0.40).
        max_adjacent_sub_face_dist: The maximum distance in meters between interior
            Apertures and Doors at which they are considered adjacent. This is used to
            ensure that only one interior Aperture of an adjacent pair is written into
            the IDM. This value should typically be around the max_int_wall_thickness
            and should ideally not be thicker than 0.5. But it may be undesirable to
            set this to zero (like some cases of max_int_wall_thickness),
            particularly when the adjacent interior geometries are not matching
            one another. (Default: 0.40).
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

    Returns:
        Path to exported IDM file.
    """
    # ensure the model is in meters and no room names are longer than 30 characters
    model = model.duplicate()
    if model.units != 'Meters':
        model.convert_to_units('Meters')
    for room in model.room_2ds:
        room.display_name = readable_short_name(room.display_name)
    north_angle = project_info.north_angle if project_info else 0
    # translate to honeybee using appropriate renaming conventions
    hb_model = model.to_honeybee(
        'District', use_multiplier=use_multiplier, exclude_plenums=exclude_plenums,
        solve_ceiling_adjacencies=False, enforce_adj=False, enforce_solid=True,
        face_rename_format=face_rename_format, subface_rename_format=subface_rename_format,
        name_decimal_count=name_decimal_count, exclude_units_in_name=exclude_units_in_name,
        north_angle=north_angle
    )[0]
    folder = folder if folder is not None else folders.default_simulation_folder
    return hb_model_to_idm(
        hb_model, folder, name, project_info=project_info,
        max_int_wall_thickness=max_int_wall_thickness,
        max_adjacent_sub_face_dist=max_adjacent_sub_face_dist
    )
