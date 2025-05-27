def fa_to_en_digits(s):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translation_table = str.maketrans("".join(persian_digits), "".join(english_digits))
    return str(s).translate(translation_table)
