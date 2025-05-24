# coding=utf-8
"""Model IDA ICE Properties."""


class ModelIdaiceProperties(object):
    """IDA ICE Properties for Dragonfly Model.

    Args:
        host: A dragonfly_core Model object that hosts these properties.

    Properties:
        * host
    """

    def __init__(self, host):
        """Initialize ModelIdaiceProperties."""
        self._host = host

    @property
    def host(self):
        """Get the Model object hosting these properties."""
        return self._host

    def check_for_extension(self, raise_exception=True, detailed=False):
        """Check that the Model is valid for IDA ICE simulation.

        This process includes all relevant dragonfly-core checks as well as checks
        that apply only for IDA ICE.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if any errors are found. If False, this method will simply
                return a text string with all errors that were found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A text string with all errors that were found or a list if detailed is True.
            This string (or list) will be empty if no errors were found.
        """
        # set up defaults to ensure the method runs correctly
        detailed = False if raise_exception else detailed
        msgs = []
        tol = self.host.tolerance
        ang_tol = self.host.angle_tolerance

        # perform checks for duplicate identifiers, which might mess with other checks
        msgs.append(self.host.check_all_duplicate_identifiers(False, detailed))

        # perform checks for key dragonfly model schema rules
        msgs.append(self.host.check_degenerate_room_2ds(tol, False, detailed))
        msgs.append(self.host.check_self_intersecting_room_2ds(tol, False, detailed))
        msgs.append(self.host.check_plenum_depths(tol, False, detailed))
        msgs.append(self.host.check_window_parameters_valid(tol, False, detailed))
        msgs.append(self.host.check_no_room2d_overlaps(tol, False, detailed))
        msgs.append(self.host.check_collisions_between_stories(tol, False, detailed))
        msgs.append(self.host.check_roofs_above_rooms(tol, False, detailed))
        msgs.append(self.host.check_room2d_floor_heights_valid(False, detailed))
        msgs.append(self.host.check_all_room3d(tol, ang_tol, False, detailed))

        # output a final report of errors or raise an exception
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def to_dict(self):
        """Return Model IDA ICE properties as a dictionary."""
        return {'idaice': {'type': 'ModelIdaiceProperties'}}

    def apply_properties_from_dict(self, data):
        """Apply the IDA ICE properties of a dictionary to the host Model of this object.

        Args:
            data: A dictionary representation of an entire dragonfly-core Model.
                Note that this dictionary must have ModelIdaiceProperties in order
                for this method to successfully apply the IDA ICE properties.
        """
        assert 'idaice' in data['properties'], \
            'Dictionary possesses no ModelIdaiceProperties.'

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Model IDA ICE Properties: [host: {}]'.format(self.host.display_name)
