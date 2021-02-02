import re
from django.core.exceptions import ValidationError

rules = ['A-Z', 'a-z', '0-9', '!@#$%^&*()_-']

class MinimumDiversityValidator(object):
    def validate(self, password, user=None):
        for r in rules:
            if re.search('[%s]' % r, password) is None:
                raise ValidationError("Please include characters in [%s]" % r)

    def get_help_text(self):
        return "Please include at least one character from each of the four categories: %s" % '; '.join(['%d, %s' % (i, r) for i, r in enumerate(rules)])
