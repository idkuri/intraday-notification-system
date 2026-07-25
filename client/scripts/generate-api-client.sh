#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bunx openapi-typescript src/lib/api-client/openapi.json -o src/lib/api-client/schema.ts
echo "Generated src/lib/api-client/schema.ts"
