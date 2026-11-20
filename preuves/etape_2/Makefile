BASE_URL := http://localhost:8000

MISSING_ORDER_ID := 00000000-0000-0000-0000-000000000000
RESTAURANT_ID := abedf6ef-f9d1-5e09-a215-9b8530374385
USER_ID := c0717134-f8ba-57b2-a72a-2ea5ea7b14f3

.PHONY: help check missing-order empty-cart invalid-json

help:
	@echo "Commandes disponibles :"
	@echo "  make check          - Verifier automatiquement les trois erreurs"
	@echo "  make missing-order  - Commande inexistante (404)"
	@echo "  make empty-cart     - Panier vide (422)"
	@echo "  make invalid-json   - Corps JSON illisible (422)"

check:
	@result=$$(curl -sS -o /tmp/missing-order.json -w "%{http_code} %{content_type}" "$(BASE_URL)/v1/orders/$(MISSING_ORDER_ID)"); \
		test "$$result" = "404 application/problem+json"; \
		jq -e 'keys == ["detail", "instance", "status", "title", "type"] and .status == 404 and .type != null' /tmp/missing-order.json >/dev/null
	@result=$$(curl -sS -o /tmp/empty-cart.json -w "%{http_code} %{content_type}" -X POST "$(BASE_URL)/v1/restaurants/$(RESTAURANT_ID)/orders" \
		-H "Content-Type: application/json" \
		-d '{"userId":"$(USER_ID)","items":[]}'); \
		test "$$result" = "422 application/problem+json"; \
		jq -e 'keys == ["detail", "instance", "status", "title", "type"] and .status == 422 and .type != null' /tmp/empty-cart.json >/dev/null
	@result=$$(curl -sS -o /tmp/invalid-json.json -w "%{http_code} %{content_type}" -X POST "$(BASE_URL)/v1/restaurants/$(RESTAURANT_ID)/orders" \
		-H "Content-Type: application/json" \
		-d '{"userId":'); \
		test "$$result" = "422 application/problem+json"; \
		jq -e 'keys == ["detail", "instance", "status", "title", "type"] and .status == 422 and .type != null' /tmp/invalid-json.json >/dev/null
	@echo "Etape 2 validee : statuts et formats conformes."

missing-order:
	@curl -sS -D /tmp/api-headers.txt "$(BASE_URL)/v1/orders/$(MISSING_ORDER_ID)" -o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json

empty-cart:
	@curl -sS -D /tmp/api-headers.txt -X POST "$(BASE_URL)/v1/restaurants/$(RESTAURANT_ID)/orders" \
		-H "Content-Type: application/json" \
		-d '{"userId":"$(USER_ID)","items":[]}' \
		-o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json

invalid-json:
	@curl -sS -D /tmp/api-headers.txt -X POST "$(BASE_URL)/v1/restaurants/$(RESTAURANT_ID)/orders" \
		-H "Content-Type: application/json" \
		-d '{"userId":' \
		-o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json
