"""
CORE: messages
PURPOSE: Language-aware response messages
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Dict


***REMOVED*** Language-aware message dictionaries
MESSAGES: Dict[str, Dict[str, str]] = {
    "onboarding_received": {
        "en": "Your request has been received. A SOAR strategist will activate your plan.",
        "tr": "Talebiniz alındı. Bir SOAR stratejisti planınızı aktifleştirecektir.",
        "de": "Ihre Anfrage wurde erhalten. Ein SOAR-Strategist wird Ihren Plan aktivieren.",
        "es": "Su solicitud ha sido recibida. Un estratega SOAR activará su plan.",
        "fr": "Votre demande a été reçue. Un stratège SOAR activera votre plan.",
        "ar": "تم استلام طلبك. سيقوم استراتيجي SOAR بتنشيط خطتك."
    },
    "support_received": {
        "en": "Your message has been received. We'll get back to you soon!",
        "tr": "Mesajınız alındı. En kısa sürede size dönüş yapacağız!",
        "de": "Ihre Nachricht wurde empfangen. Wir werden Ihnen bald antworten!",
        "es": "Su mensaje ha sido recibido. ¡Nos pondremos en contacto pronto!",
        "fr": "Votre message a été reçu. Nous vous répondrons bientôt!",
        "ar": "تم استلام رسالتك. سنعود إليك قريباً!"
    },
    "lead_received": {
        "en": "Lead received and appointment scheduled",
        "tr": "Potansiyel müşteri alındı ve randevu planlandı",
        "de": "Lead erhalten und Termin geplant",
        "es": "Lead recibido y cita programada",
        "fr": "Prospect reçu et rendez-vous programmé",
        "ar": "تم استلام العميل المحتمل وتم جدولة الموعد"
    }
}


def get_message(message_key: str, locale: str = "en") -> str:
    """
    Get language-aware message.
    
    Args:
        message_key: Key from MESSAGES dictionary
        locale: Language code (tr, en, de, es, fr, ar)
    
    Returns:
        Localized message string
    """
    messages = MESSAGES.get(message_key, {})
    return messages.get(locale, messages.get("en", ""))


def get_onboarding_received_message(locale: str = "en") -> str:
    """Get onboarding received message in specified locale."""
    return get_message("onboarding_received", locale)


def get_support_received_message(locale: str = "en") -> str:
    """Get support received message in specified locale."""
    return get_message("support_received", locale)


def get_lead_received_message(locale: str = "en") -> str:
    """Get lead received message in specified locale."""
    return get_message("lead_received", locale)
