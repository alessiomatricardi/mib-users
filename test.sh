#!/usr/bin/bash
export FLASK_ENV=development

echo 'Actual db will be renamed to old_users_ms.db'
echo 'Remember to rename it if you want to use'
mv -f users_ms.db old_users_ms.db || echo 'users_ms.db not exists... continue with tests'

pytest -s --cov mib

mv -f users_ms.db users_ms_test.db
( mv -f old_users_ms.db users_ms.db && rm -f users_ms_test.db ) || ( echo 'old_users_ms.db not exists... users_ms.db from test will be held' && mv -f users_ms_test.db users_ms.db )

echo 'Test done!'