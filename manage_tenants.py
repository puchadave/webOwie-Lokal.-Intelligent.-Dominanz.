#!/usr/bin/env python3
import argparse
import shutil
import os
from tenants import add_tenant, list_tenants


def create_tenant(name, slug, copy_env=True):
    tenant = add_tenant(name, slug)
    print(f"Created tenant: {tenant}")
    if copy_env and os.path.exists('config.example.env'):
        target = f'.env.{slug}'
        shutil.copyfile('config.example.env', target)
        print(f'Copied config.example.env to {target}')
    print('\nNext steps:')
    print(f'  - Edit .env.{slug} with tenant credentials (if needed)')
    print(f'  - Run tenant instance: TENANT={slug} python app.py')
    # Attempt to create an initial admin user for the tenant.
    # We temporarily set TENANT so the app uses tenant-specific DB/storage.
    os.environ['TENANT'] = slug
    try:
        from app import app
        from accounting import db
        # import User model locally to avoid circular imports at module load
        from users import User
        with app.app_context():
            try:
                db.init_app(app)
            except Exception:
                # already initialized in this process/app - ignore
                pass
            db.create_all()
            # create admin user if not exists
            if not User.query.filter_by(username='admin').first():
                import secrets
                pwd = secrets.token_urlsafe(12)
                admin = User(username='admin', email=None, role='admin')
                admin.set_password(pwd)
                db.session.add(admin)
                db.session.commit()
                # append admin credentials to env file for operator
                if os.path.exists(target):
                    with open(target, 'a') as f:
                        f.write(f"\nADMIN_USER=admin\nADMIN_PASSWORD={pwd}\n")
                print(f"Initialized admin user: admin (password written to {target})")
            # create default permissions
            try:
                from users import Permission
                default_perms = ['use_ai', 'run_automation', 'manage_products', 'manage_dms']
                for pn in default_perms:
                    if not Permission.query.filter_by(name=pn).first():
                        p = Permission(name=pn, description='Auto-created default permission')
                        db.session.add(p)
                db.session.commit()
                print('Created default permissions for tenant')
            except Exception as e:
                print('Warning: could not create default permissions:', e)
    except Exception as e:
        print('Warning: could not create admin user automatically:', e)



def list_cmd():
    tenants = list_tenants()
    if not tenants:
        print('No tenants')
        return
    for slug, info in tenants.items():
        print(f"{slug}: {info.get('name')} (storage: {info.get('storage')})")


def main():
    p = argparse.ArgumentParser(description='Manage tenants for Agenturmodus')
    sub = p.add_subparsers(dest='cmd')

    create = sub.add_parser('create')
    create.add_argument('name')
    create.add_argument('slug')

    ls = sub.add_parser('list')

    args = p.parse_args()
    if args.cmd == 'create':
        create_tenant(args.name, args.slug)
    elif args.cmd == 'list':
        list_cmd()
    else:
        p.print_help()


if __name__ == '__main__':
    main()
