SHELL := /bin/bash

BASE_URL := http://localhost:8000
COMPOSE_FILE := ../../docker-compose.yml
ORDER_ID := 4c637586-ea95-55b6-8910-b6254e8b2b8c
PAYLOAD := {"method":"card","cardToken":"tok_etape_4"}
RUN_ID := $(shell date +%s%N)
REPLAY_KEY := etape-4-replay-$(RUN_ID)
DIFFERENT_KEY := etape-4-different-$(RUN_ID)
TMP_PREFIX := /tmp/miamzy-etape-4-$(RUN_ID)

.PHONY: help check replay-payment different-key missing-key

help:
	@echo "Commandes disponibles :"
	@echo "  make check              - Verifier automatiquement toute l'idempotence"
	@echo "  make replay-payment     - Afficher trois reponses et la ligne en base"
	@echo "  make different-key      - Payer avec deux cles differentes"
	@echo "  make missing-key        - Afficher le refus d'un paiement sans cle"

check:
	@set -eu; \
		for attempt in 1 2 3; do \
			result=$$(curl -sS -o "$(TMP_PREFIX)-replay-$$attempt.json" -w "%{http_code} %{content_type}" \
				-X POST "$(BASE_URL)/v1/orders/$(ORDER_ID)/payments" \
				-H "Content-Type: application/json" \
				-H "Idempotency-Key: $(REPLAY_KEY)" \
				-d '$(PAYLOAD)'); \
			test "$$result" = "201 application/json"; \
		done; \
		cmp -s "$(TMP_PREFIX)-replay-1.json" "$(TMP_PREFIX)-replay-2.json"; \
		cmp -s "$(TMP_PREFIX)-replay-1.json" "$(TMP_PREFIX)-replay-3.json"; \
		result=$$(curl -sS -o "$(TMP_PREFIX)-different.json" -w "%{http_code} %{content_type}" \
			-X POST "$(BASE_URL)/v1/orders/$(ORDER_ID)/payments" \
			-H "Content-Type: application/json" \
			-H "Idempotency-Key: $(DIFFERENT_KEY)" \
			-d '$(PAYLOAD)'); \
		test "$$result" = "201 application/json"; \
		test "$$(jq -r .id "$(TMP_PREFIX)-replay-1.json")" != "$$(jq -r .id "$(TMP_PREFIX)-different.json")"; \
		replay_count=$$(docker compose -f "$(COMPOSE_FILE)" exec -T postgres psql -U miamzy -d miamzy -Atc \
			"SELECT COUNT(*) FROM payments WHERE idempotency_key = '$(REPLAY_KEY)';"); \
		test "$$replay_count" = "1"; \
		total_count=$$(docker compose -f "$(COMPOSE_FILE)" exec -T postgres psql -U miamzy -d miamzy -Atc \
			"SELECT COUNT(*) FROM payments WHERE idempotency_key IN ('$(REPLAY_KEY)', '$(DIFFERENT_KEY)');"); \
		test "$$total_count" = "2"; \
		result=$$(curl -sS -o "$(TMP_PREFIX)-missing.json" -w "%{http_code} %{content_type}" \
			-X POST "$(BASE_URL)/v1/orders/$(ORDER_ID)/payments" \
			-H "Content-Type: application/json" \
			-d '$(PAYLOAD)'); \
		test "$$result" = "422 application/problem+json"; \
		jq -e '.status == 422 and (.detail | ascii_downcase | contains("idempotency-key"))' \
			"$(TMP_PREFIX)-missing.json" >/dev/null
	@echo "Etape 4 validee : un seul effet par cle, rejeux identiques et cle obligatoire."

replay-payment:
	@set -eu; \
		for attempt in 1 2 3; do \
			curl --fail-with-body -sS -o "$(TMP_PREFIX)-replay-$$attempt.json" \
				-X POST "$(BASE_URL)/v1/orders/$(ORDER_ID)/payments" \
				-H "Content-Type: application/json" \
				-H "Idempotency-Key: $(REPLAY_KEY)" \
				-d '$(PAYLOAD)'; \
		done; \
		echo "========== TROIS REPONSES =========="; \
		jq -s '{reponse1: .[0], reponse2: .[1], reponse3: .[2]}' \
			"$(TMP_PREFIX)-replay-1.json" "$(TMP_PREFIX)-replay-2.json" "$(TMP_PREFIX)-replay-3.json"; \
		echo "========== TABLE PAYMENTS =========="; \
		docker compose -f "$(COMPOSE_FILE)" exec -T postgres psql -U miamzy -d miamzy -P pager=off -c \
			"SELECT id, order_id, amount_cents, status, idempotency_key, paid_at FROM payments WHERE idempotency_key = '$(REPLAY_KEY)';"

different-key:
	@set -eu; \
		for key in "$(REPLAY_KEY)" "$(DIFFERENT_KEY)"; do \
			curl --fail-with-body -sS -X POST "$(BASE_URL)/v1/orders/$(ORDER_ID)/payments" \
				-H "Content-Type: application/json" \
				-H "Idempotency-Key: $$key" \
				-d '$(PAYLOAD)' | jq '{id, orderId, status, paidAt}'; \
		done
	@docker compose -f "$(COMPOSE_FILE)" exec -T postgres psql -U miamzy -d miamzy -P pager=off -c \
		"SELECT id, idempotency_key FROM payments WHERE idempotency_key IN ('$(REPLAY_KEY)', '$(DIFFERENT_KEY)') ORDER BY paid_at;"

missing-key:
	@curl -sS -D "$(TMP_PREFIX)-headers.txt" -o "$(TMP_PREFIX)-missing.json" \
		-X POST "$(BASE_URL)/v1/orders/$(ORDER_ID)/payments" \
		-H "Content-Type: application/json" \
		-d '$(PAYLOAD)'
	@echo "========== HEADERS HTTP =========="
	@cat "$(TMP_PREFIX)-headers.txt"
	@echo "========== RESPONSE JSON =========="
	@jq . "$(TMP_PREFIX)-missing.json"
