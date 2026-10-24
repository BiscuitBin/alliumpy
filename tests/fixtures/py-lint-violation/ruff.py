# Positive control: this file must keep failing F401 and E501.
import os

LONG = "This positive control deliberately exceeds one hundred characters so E501 must report it on every lint gate run."
