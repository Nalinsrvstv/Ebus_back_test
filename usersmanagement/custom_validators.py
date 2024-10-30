# custom_validators.py (within your Django app)

import re
from django.core.exceptions import ValidationError

class UppercaseAndSpecialCharacterValidator:
    def __init__(self, min_uppercase_chars=1, min_special_chars=1, min_numeric_chars=1):
        self.min_uppercase_chars = min_uppercase_chars
        self.min_special_chars = min_special_chars
        self.min_numeric_chars = min_numeric_chars

    def validate(self, password, user=None):
        # Check if the password contains at least the specified number of uppercase letters
        if sum(1 for char in password if char.isupper()) < self.min_uppercase_chars:
            raise ValidationError(f"The password must contain at least {self.min_uppercase_chars} uppercase letter(s).")

        # Define a regular expression pattern to match special characters
        special_characters_pattern = r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]'

        # Check if the password contains at least the specified number of special characters
        if len(re.findall(special_characters_pattern, password)) < self.min_special_chars:
            raise ValidationError(f"The password must contain at least {self.min_special_chars} special character(s).")

        # Check if the password contains at least the specified number of numeric characters
        if sum(1 for char in password if char.isdigit()) < self.min_numeric_chars:
            raise ValidationError(f"The password must contain at least {self.min_numeric_chars} numeric character(s).")

    def get_help_text(self):
        return f"Password must contain at least {self.min_uppercase_chars} uppercase letter(s), {self.min_special_chars} special character(s), and {self.min_numeric_chars} numeric character(s)."
