BASE_URL := http://localhost:8000
COMPOSE_FILE := ../../docker-compose.yml

.PHONY: help check default-page next-page oversized-page explain

help:
	@echo "Commandes disponibles :"
	@echo "  make check           - Verifier automatiquement toute la pagination"
	@echo "  make default-page    - Afficher la page par defaut (20 commandes)"
	@echo "  make next-page       - Afficher deux pages successives"
	@echo "  make oversized-page  - Afficher le refus de 100 000 elements"
	@echo "  make explain         - Afficher le plan de la requete PostgreSQL"

check:
	@curl --fail-with-body -sS "$(BASE_URL)/v1/orders" -o /tmp/orders-page-1.json
	@jq -e '.data | length == 20' /tmp/orders-page-1.json >/dev/null
	@cursor=$$(jq -er '.nextCursor' /tmp/orders-page-1.json); \
		curl --fail-with-body -sS --get --data-urlencode "cursor=$$cursor" "$(BASE_URL)/v1/orders" -o /tmp/orders-page-2.json
	@jq -e '.data | length == 20' /tmp/orders-page-2.json >/dev/null
	@jq -n -e --slurpfile first /tmp/orders-page-1.json --slurpfile second /tmp/orders-page-2.json \
		'[$$first[0].data[].id] as $$a | [$$second[0].data[].id] as $$b | all($$a[]; IN($$b[]) | not)' >/dev/null
	@curl --fail-with-body -sS "$(BASE_URL)/v1/orders?limit=100" -o /tmp/orders-page-100.json
	@jq -e '.data | length <= 100' /tmp/orders-page-100.json >/dev/null
	@result=$$(curl -sS -o /tmp/orders-oversized.json -w "%{http_code} %{content_type}" "$(BASE_URL)/v1/orders?limit=100000"); \
		test "$$result" = "422 application/problem+json"
	@jq -e '.status == 422 and .instance == "/v1/orders"' /tmp/orders-oversized.json >/dev/null
	@echo "Etape 3 validee : pages bornees, page suivante distincte et limite refusee."

default-page:
	@curl -sS -D /tmp/api-headers.txt "$(BASE_URL)/v1/orders" -o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== NOMBRE DE COMMANDES =========="
	@jq '.data | length' /tmp/api-response.json
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json

next-page:
	@curl --fail-with-body -sS "$(BASE_URL)/v1/orders" -o /tmp/orders-page-1.json
	@cursor=$$(jq -er '.nextCursor' /tmp/orders-page-1.json); \
		curl --fail-with-body -sS --get --data-urlencode "cursor=$$cursor" "$(BASE_URL)/v1/orders" -o /tmp/orders-page-2.json
	@echo "========== PAGE 1 =========="
	@jq '{count: (.data | length), firstId: .data[0].id, nextCursor}' /tmp/orders-page-1.json
	@echo "========== PAGE 2 =========="
	@jq '{count: (.data | length), firstId: .data[0].id, nextCursor}' /tmp/orders-page-2.json

oversized-page:
	@curl -sS -D /tmp/api-headers.txt "$(BASE_URL)/v1/orders?limit=100000" -o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json

explain:
	@docker compose -f "$(COMPOSE_FILE)" exec -T postgres psql -U miamzy -d miamzy -c \
		'EXPLAIN (ANALYZE, BUFFERS) SELECT id, restaurant_id, user_id, status, total_amount_cents, currency, created_at, updated_at FROM orders ORDER BY created_at DESC, id DESC LIMIT 21;'
