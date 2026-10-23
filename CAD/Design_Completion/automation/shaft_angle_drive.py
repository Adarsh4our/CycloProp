def drive_shaft_angle(d, shaft, hold, target, c, NULL):
    import math
    target %= 2 * math.pi
    for flip in [False, True]:
        fd = c(hold, 'GetDefinition')
        fd.ReferenceEntity = c(c(d, 'FeatureByName', 'Front Plane'), 'GetSpecificFeature2')
        fd.Angle = target
        fd.FlipDimension = flip
        assert c(hold, 'ModifyDefinition', fd, d, NULL)
        assert c(d, 'ForceRebuild3', False)
        t = list(c(shaft, 'GetTotalTransform', True).ArrayData)
        actual = math.atan2(t[1], t[0])
        error = (actual - target + math.pi) % (2 * math.pi) - math.pi
        if abs(error) < math.radians(.001):
            return flip
    raise AssertionError(('Shaft angle mate could not reach commanded direction', math.degrees(target), math.degrees(actual)))
