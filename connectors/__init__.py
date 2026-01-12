"""Connectors package: payments and advertising connectors."""
from .bank_connector import BankConnector
from .paypal_connector import PaypalConnector
from .sumup_connector import SumUpConnector
from .revolut_connector import RevolutConnector
from .sepa_direct_debit import SepaDirectDebitConnector
from .openbanking import OpenBankingConnector

# advertising connectors (optional)
try:
    from .google_ads import GoogleAdsConnector
    from .facebook_ads import FacebookAdsConnector
    from .instagram_ads import InstagramAdsConnector
    from .linkedin_marketing import LinkedInMarketingConnector
except Exception:
    GoogleAdsConnector = None
    FacebookAdsConnector = None
    InstagramAdsConnector = None
    LinkedInMarketingConnector = None

__all__ = [
    'BankConnector', 'PaypalConnector', 'SumUpConnector', 'RevolutConnector', 'SepaDirectDebitConnector',
    'GoogleAdsConnector', 'FacebookAdsConnector', 'InstagramAdsConnector', 'LinkedInMarketingConnector'
]


def get_payment_connector(provider=None, config=None):
    provider = provider or __import__('os').environ.get('PAYMENT_PROVIDER', 'paypal')
    provider = provider.lower()
    if provider == 'paypal':
        return PaypalConnector(config or PaypalConnector.configure_from_env())
    if provider == 'sumup':
        return SumUpConnector(config or SumUpConnector.configure_from_env())
    if provider == 'revolut':
        return RevolutConnector(config or RevolutConnector.configure_from_env())
    if provider in ('openbanking', 'open_bank', 'open-bank'):
        return OpenBankingConnector(config or OpenBankingConnector.configure_from_env())
    if provider in ('bank', 'onlinebanking'):
        return BankConnector(config or BankConnector.configure_from_env())
    return PaypalConnector(config or PaypalConnector.configure_from_env())


def get_ads_connector(provider=None, config=None):
    provider = provider or __import__('os').environ.get('ADS_PROVIDER')
    provider = (provider or '').lower()
    if provider == 'google_ads' and GoogleAdsConnector:
        return GoogleAdsConnector(config or GoogleAdsConnector.configure_from_env())
    if provider == 'facebook_ads' and FacebookAdsConnector:
        return FacebookAdsConnector(config or FacebookAdsConnector.configure_from_env())
    if provider == 'instagram_ads' and InstagramAdsConnector:
        return InstagramAdsConnector(config or InstagramAdsConnector.configure_from_env())
    if provider in ('linkedin', 'linkedin_marketing') and LinkedInMarketingConnector:
        return LinkedInMarketingConnector(config or LinkedInMarketingConnector.configure_from_env())
    raise RuntimeError('No ads connector available for provider: %s' % provider)
