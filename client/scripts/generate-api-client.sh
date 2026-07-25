#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf src/api-client
bunx openapi-typescript-codegen \
	--input src/generated/openapi.json \
	--output src/api-client \
	--client fetch \
	--useOptions \
	--indent 2
echo "Generated src/api-client (openapi-typescript-codegen)"
