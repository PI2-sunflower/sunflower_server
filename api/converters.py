class FourDigitYearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value

class TwoDigitYearConverter:
    regex = '[0-9]{2}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%02d' % value

class FloarConverter:
    regex = r'[-+]?[0-9]*\.?[0-9]+'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return '{}'.format(value)
