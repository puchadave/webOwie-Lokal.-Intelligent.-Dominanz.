import json
import os
from pathlib import Path

TENANTS_FILE = Path('tenants.json')


def _load_registry():
    if not TENANTS_FILE.exists():
        return {}
    try:
        return json.loads(TENANTS_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _save_registry(data):
    TENANTS_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')


def list_tenants():
    return _load_registry()


def add_tenant(name, slug):
    data = _load_registry()
    if slug in data:
        raise ValueError('Tenant slug already exists')
    tenant_dir = os.path.join('storage', 'tenants', slug)
    os.makedirs(tenant_dir, exist_ok=True)
    data[slug] = {
        'name': name,
        'slug': slug,
        'storage': tenant_dir
    }
    _save_registry(data)
    return data[slug]
