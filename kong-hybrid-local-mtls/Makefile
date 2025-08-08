.PHONY: all build create-cluster generate-certs create-secrets deploy-cp deploy-dp cleanup

all: create-cluster build generate-certs create-secrets deploy-cp deploy-dp

build:
	./scripts/build-plugin.sh

create-cluster:
	./scripts/create-cluster.sh

generate-certs:
	./scripts/generate-mtls-certs.sh

create-secrets:
	./scripts/create-k8s-secrets.sh

deploy-cp:
	./scripts/deploy-cp.sh

deploy-dp:
	./scripts/deploy-dp.sh

cleanup:
	./scripts/cleanup.sh
