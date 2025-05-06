from faker import Faker
from datetime import datetime
from dateparser.search import search_dates

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
        if label == "DATE_TIME":
            # Handle flexible matching for date reformulations
            try:
                date_matches = match_datetime_in_text(val, raw_text)
            except Exception as e:
                print(f"⚠️ Error in match_datetime_in_text for value '{val}': {e}")
                date_matches = []
            if date_matches:
                phrase, _ = date_matches[0]
                start = raw_text.find(phrase)
                if start != -1:
                    end = start + len(phrase)
                    mappings.append({
                        "type": label,
                        "span": (start, end),
                        "raw": phrase
                    })
                    masked = masked.replace(phrase, f"<{label}>")
            continue  # Skip standard matching for DATE_TIME (already handled)
        
        if label == "LOCATION":
            # Try full location first
            if val in raw_text:
                start = raw_text.find(val)
                end = start + len(val)
                mappings.append({
                    "type": label,
                    "span": (start, end),
                    "raw": val
                })
                masked = masked.replace(val, f"<{label}>")
                continue

            # Try alternate form with "à"
            parts = val.split(',')
            #print(parts)
            if len(parts) >= 2:
                location_wo_postcode = ','.join(parts[:-1]).strip()
                #print(location_wo_postcode)
                city_part = parts[-1].split()[-1]
                #print(city_part)
                alt_form = f"{location_wo_postcode} à {city_part}"
                #print(alt_form)
                if alt_form in raw_text:
                    start = raw_text.find(alt_form)
                    end = start + len(alt_form)
                    mappings.append({
                        "type": label,
                        "span": (start, end),
                        "raw": alt_form
                    })
                    masked = masked.replace(alt_form, f"<{label}>")
                    continue

                # Fallback: Try just city name
                if city_part in raw_text:
                    start = raw_text.find(city_part)
                    end = start + len(city_part)
                    mappings.append({
                        "type": label,
                        "span": (start, end),
                        "raw": city_part
                    })
                    masked = masked.replace(city_part, f"<{label}>")
                    continue

            #print(f"⚠️ LOCATION '{val}' not found in raw_text.")
            continue
        start = raw_text.find(val)
        if start == -1:
            continue
        end = start + len(val)
        mappings.append({
            "type": label,
            "span": (start, end),
            "raw": val
        })
        masked = masked.replace(val, f"<{label}>")

    return masked, mappings


def match_datetime_in_text(pii_dt: str, text: str):
    """Find reformulated date/time in French text matching the given PII date within a short delta."""

    # Parse the known PII datetime into a datetime object
    target = datetime.strptime(pii_dt, "%d/%m/%Y %H:%M:%S")
    found = []

    # Use dateparser to extract date expressions from the text (supports French)
    results = search_dates(text, languages=["fr"])

    # If search_dates finds nothing, fall back to direct string match
    if not results:
        # Fallback: direct string match
        if pii_dt in text:
            found.append((pii_dt, target))
        return found

    # For each date expression detected
    for phrase, parsed_dt in results:
        if parsed_dt is None:
            continue

        # Compute the difference in seconds between the parsed date and the PII date
        try:
            delta = abs((parsed_dt - target).total_seconds())
        except TypeError:
            # Handle naive/aware datetime mismatch
            if parsed_dt.tzinfo is not None and target.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=None)
            elif parsed_dt.tzinfo is None and target.tzinfo is not None:
                target = target.replace(tzinfo=None)
            delta = abs((parsed_dt - target).total_seconds())
        # If within a day, consider it a match
        if delta < 86400:
            found.append((phrase, parsed_dt))

    # Fallback: if still nothing found, check for direct string match
    if not found and pii_dt in text:
        found.append((pii_dt, target))

    return found


