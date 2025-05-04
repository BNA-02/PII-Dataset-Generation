from faker import Faker

fake = Faker('fr_FR')

def sample_pii():
    """
    Returns a dict mapping each label to a French-formatted fake value.
    """
    return {
        "PERSON":        fake.name(),
        "PHONE_NUMBER":  fake.phone_number(),
        "EMAIL_ADDRESS": fake.email(),
        "CREDIT_CARD":   fake.credit_card_number(),
        "IBAN_CODE":     fake.iban(),
        "IP_ADDRESS":    fake.ipv4(),
        "LOCATION":      fake.address().replace("\n", ", "),
        "DATE_TIME":     fake.date_time_between(start_date='-1y', end_date='now')
                              .strftime("%d/%m/%Y %H:%M:%S"),
    }

def mask_entities(raw_text: str, pii_values: dict):
    """
    Given raw_text where placeholders [LABEL] have been replaced by real values,
    returns (masked_text, mappings) where masked_text has <LABEL> tags and
    mappings is a list of {type, span, raw}.
    """
    masked = raw_text
    mappings = []
    for label, val in pii_values.items():
        start = raw_text.find(val)
        if start == -1:
            continue
        end = start + len(val)
        mappings.append({
            "type":  label,
            "span":  (start, end),
            "raw":   val
        })
        masked = masked.replace(val, f"<{label}>")
    return masked, mappings
