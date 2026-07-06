.PHONY: eval
eval:
	cd mwis-agent && MWIS_ENV=development uv run --env-file .env agents-cli eval generate --dataset tests/eval/datasets/mwis_eval.json
	cd mwis-agent && uv run --env-file .env agents-cli eval grade

.PHONY: playground
playground:
	cd mwis-agent && uv run --env-file .env agents-cli playground
