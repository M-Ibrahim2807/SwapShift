def build_whatsapp_link(contact_number: str) -> str:
    compact = contact_number.replace(" ", "")
    return f"https://wa.me/{compact}"
