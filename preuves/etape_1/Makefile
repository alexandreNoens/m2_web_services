BASE_URL := http://localhost:8000

ORDER_ID := 4c637586-ea95-55b6-8910-b6254e8b2b8c
RESTAURANT_ID := abedf6ef-f9d1-5e09-a215-9b8530374385
USER_ID := c0717134-f8ba-57b2-a72a-2ea5ea7b14f3
MENU_ITEM_ID := b7138268-6bcf-5175-804d-c83bd11cf13c

.PHONY: help check list-orders get-order create-order pay-order get-profile

help:
	@echo "Commandes disponibles :"
	@echo "  make check         - Verifier que l'API repond"
	@echo "  make list-orders   - Lister les commandes"
	@echo "  make get-order     - Consulter une commande"
	@echo "  make create-order  - Creer une commande"
	@echo "  make pay-order     - Payer une commande"
	@echo "  make get-profile   - Consulter un profil"

check:
	@curl --fail-with-body -sS -i "$(BASE_URL)/v1/orders?limit=1"

list-orders:
	@curl -sS -D /tmp/api-headers.txt "$(BASE_URL)/v1/orders?limit=2" -o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json

get-order:
	@curl -sS -D /tmp/api-headers.txt "$(BASE_URL)/v1/orders/$(ORDER_ID)" -o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json

create-order:
	@curl -sS -D /tmp/api-headers.txt -X POST "$(BASE_URL)/v1/restaurants/$(RESTAURANT_ID)/orders" \
		-H "Content-Type: application/json" \
		-d '{"userId":"$(USER_ID)","items":[{"menuItemId":"$(MENU_ITEM_ID)","quantity":2}]}' \
		-o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json

pay-order:
	@curl -sS -D /tmp/api-headers.txt -X POST "$(BASE_URL)/v1/orders/$(ORDER_ID)/payments" \
		-H "Content-Type: application/json" \
		-H "Idempotency-Key: paiement-demo-1" \
		-d '{"method":"card","cardToken":"tok_test"}' \
		-o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json

get-profile:
	@curl -sS -D /tmp/api-headers.txt "$(BASE_URL)/v1/users/$(USER_ID)/profile" -o /tmp/api-response.json
	@echo "========== HEADERS HTTP =========="
	@cat /tmp/api-headers.txt
	@echo "========== RESPONSE JSON =========="
	@jq . /tmp/api-response.json
