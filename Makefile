.PHONY: eval
eval:
	MWIS_ENV=development uv run --env-file .env agents-cli eval generate --dataset tests/eval/datasets/mwis_eval.json
	uv run --env-file .env agents-cli eval grade

.PHONY: playground
playground:
	MWIS_ENV=development uv run --env-file .env agents-cli playground
