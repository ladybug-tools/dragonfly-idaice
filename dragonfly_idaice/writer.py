# coding: utf-8
"""Write a IDM file from a Dragonfly model."""
from __future__ import division

from honeybee.config import folders
from honeybee_idaice.writer import model_to_idm as hb_model_to_idm


def model_to_idm(model, name=None, folder=None,
                 use_multiplier=True, exclude_plenums=False,
                 max_int_wall_thickness=0.4, max_adjacent_sub_face_dist=0.4):
    """Generate an IDA-ICE IDM string from a Dragonfly Model.

    Args:
        model: A dragonfly Model.
        name: Output IDM file name. If None, the Model display name will be used.
        folder: A text string for the directory where the DFJSON will be written.
            If unspecified, the default simulation folder will be used. This
            is usually at "C:\\Users\\USERNAME\\simulation" on Windows.
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

    Returns:
        Path to exported IDM file.
    """
    hb_model = model.to_honeybee(
        'District', use_multiplier=use_multiplier, exclude_plenums=exclude_plenums,
        solve_ceiling_adjacencies=False, enforce_adj=False, enforce_solid=True)[0]
    folder = folder if folder is not None else folders.default_simulation_folder
    return hb_model_to_idm(
        hb_model, folder, name,
        max_int_wall_thickness=max_int_wall_thickness,
        max_adjacent_sub_face_dist=max_adjacent_sub_face_dist
    )
