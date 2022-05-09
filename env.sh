export DEBUG="true"
export GITHUB_PAT_TEST=${GITHUB_PAT_TEST:-"$(vault read -field="value" secret/dev-ops/github-proxy/GITHUB_PAT_TEST)"}
export GITHUB_APP_TEST_PEM=${GITHUB_APP_TEST_PEM:-"$(vault read -field="value" secret/dev-ops/github-proxy/GITHUB_APP_TEST_PEM)"}
export GITHUB_APP_TEST_ID=178519
export GITHUB_APP_TEST_INSTALLATION_ID=23919646
export CACHE_BACKEND_URL=redis://0.0.0.0:6379
export TOKEN_TEST=${TOKEN_TEST:-"$(openssl rand -base64 32)"}
export TOKEN_READ_ONLY=${TOKEN_READ_ONLY:-"$(openssl rand -base64 32)"}
export CLIENT_REGISTRY_FILE_PATH=$(pwd)/tests/integration/fixtures/clients.example.yml.j2
