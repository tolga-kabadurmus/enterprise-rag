Enterprise RAG
`enterprise-rag` is the top-level orchestration repository for the Enterprise RAG coding exercise. It brings the asynchronous document indexing pipeline, RAG query API, RustFS object storage, and Qdrant vector database together with Docker Compose.
The prototype indexes PDF documents from S3-compatible storage, chunks them, generates embeddings, stores them in Qdrant, and uses retrieved context to answer questions with source references. PDF indexing is the initial scope; additional document formats and advanced retrieval features can be added later.
For architecture, coding standards, project boundaries, and implementation guidance, see the root `AGENTS.md`.
Repositories
`enterprise-rag` — orchestrates the complete stack and tracks the other repositories as Git submodules.
`enterprise-rag-indexing` — provides a disposable, asynchronous indexing pipeline for documents in RustFS through its S3-compatible API.
`enterprise-rag-query` — provides the FastAPI RAG query service, served by Granian. Its detailed design is still to be defined.
```text
enterprise-rag (Docker Compose)
├── enterprise-rag-indexing/   # Git submodule; one-shot indexing job
├── enterprise-rag-query/      # Git submodule; RAG query API
├── RustFS                    # Compose service; S3-compatible documents
└── Qdrant                    # Compose service; vectors + source metadata
```
Git submodules
To add the component repositories to an existing `enterprise-rag` orchestration repository (run in its root directory):
```bash
git submodule add https://github.com/tolga-kabadurmus/enterprise-rag-indexing.git enterprise-rag-indexing
git submodule add https://github.com/tolga-kabadurmus/enterprise-rag-query.git enterprise-rag-query
git submodule add https://github.com/tolga-kabadurmus/enterprise-rag-deployment.git enterprise-rag-deployment
git submodule add https://github.com/tolga-kabadurmus/enterprise-rag-embedding-service.git enterprise-rag-embedding-service
git add .gitmodules enterprise-rag-indexing enterprise-rag-query enterprise-rag-deployment enterprise-rag-embedding-service
git commit -m "Add indexing and query submodules"
```
Listing the submodules
```bash
git config --file .gitmodules --name-only --get-regexp path
```
> The GitHub URLs above follow the naming convention of the earlier project. Verify that both repositories have been created under that account before executing these commands. Each repository should have at least one commit.
To clone the orchestration repository with submodules:
```bash
git clone --recurse-submodules https://github.com/tolga-kabadurmus/enterprise-rag.git
cd enterprise-rag
```
If the parent repository was already cloned without submodules:
```bash
git submodule update --init --recursive
```
To pull changes in the parent repository and check out the submodule commits it records:
```bash
git pull --ff-only
git submodule update --init --recursive
```
To intentionally advance a submodule to newer commits, update it inside its directory, then commit the changed submodule pointer from the parent repository. `git submodule update --remote` is another option when a tracking branch is configured; it should not be confused with checking out the parent repository's pinned versions.
Run the complete project
Prerequisites: Docker Engine with the Compose v2 plugin; Git; Python 3.12.3 and `virtualenv` for host-based Python development. The primary target is Ubuntu 24.04.4 LTS.
Clone with submodules using the command above, or update them if already cloned. Copy each file in `dev-envs/` by removing its `.example` suffix, then set RustFS credentials, S3 endpoints, Qdrant connection details, and embedding/LLM provider settings. Do not commit secrets.
The root S3 and Qdrant diagnostic scripts load validated settings from `dev-envs/diagnostics.env` through Pydantic `BaseSettings`. Create it from `dev-envs/diagnostics.env.example`; the real file is Git-ignored. The indexing service separately reads `dev-envs/enterprise-rag-indexing.env`, created from its safe example. Configure `EMBEDDINGS_BUCKET=models`, `EMBEDDINGS_KEY_PREFIX=embeddings`, and `EMBEDDINGS_LOCAL_DIRECTORY=/models/embeddings` to synchronize the uploaded model artifacts into its named volume before a real pipeline starts. `S3_PROCESSING_BUCKET=documents-processing` stores claimed in-progress documents, while `INDEXING_WORK_DIRECTORY=/work/indexing` points at the temporary `indexing-work` volume.
The current root `docker-compose.yaml` implements development services named `rustfs`, `qdrant`, `enterprise-rag-base`, and `enterprise-rag-indexing`. The indexing build consumes `enterprise-rag-base` as a service-backed build context, so Compose builds the base image before the indexing image. Its runtime dependency also starts the base service before the indexing service. The `indexing-work` volume is temporary scratch space; Kubernetes Jobs/CronJobs should use an `emptyDir` at the same mount path. Durable processing objects remain in RustFS.
Build the indexing image and its base dependency:
```bash
docker compose --profile dev build enterprise-rag-indexing
```
Start the persistent development infrastructure:
```bash
docker compose --profile dev up -d rustfs qdrant
```
Inspect the services and their logs:
```bash
docker compose ps
docker compose logs -f rustfs qdrant
```
Execute an on-demand indexing job (use the actual CLI flags implemented by the indexing application):
```bash
docker compose --profile dev run --rm enterprise-rag-indexing \
  python -m app.main \
  --pipeline v1 \
  --source-bucket documents \
  --key-prefix contracts/2026/ \
  --concurrency 4
```
The registered `v1` job discovers source and resumable processing objects, conditionally claims them, verifies movement into `documents-processing`, loads the configured ONNX model, and returns page-bounded PDF text chunks with citation metadata. Embedding inference and Qdrant persistence are not implemented yet, so processing objects remain durable for that later stage. The offline `mock-pdf` pipeline remains available for lifecycle diagnostics. Keep `dumb-init` as the image's PID 1 process.
When the query application provides an HTTP endpoint, use the API and documentation URLs defined by the published ports in `docker-compose.yaml`. No host port or endpoint path is fixed yet.
Stop the running services without deleting persistent data:
```bash
docker compose down
```
To remove the stack's named volumes and stored RustFS/Qdrant data (destructive):
```bash
docker compose down -v
```
Development profile
RustFS and Qdrant are assigned to the `dev` profile:
```bash
docker compose --profile dev up --build
```
A local source bind mount for the indexing service is required by `AGENTS.md`; production-style builds or a `prod` profile may be added later but are not currently implemented.
Documentation and scope
`AGENTS.md` defines coding conventions, Clean Architecture layers, factory patterns, asynchronous resource lifecycle, and planned implementation sequence.
MkDocs is the chosen documentation framework; project-specific READMEs remain useful for local development.
Hybrid search, reranking, response streaming, conversation memory, multi-agent workflows, evaluations, Helm, CI/CD, and dashboards are optional follow-on features, not claims about the initial prototype.
This README documents the intended repository and developer workflow. Keep it synchronized with the actual Docker Compose service names, environment templates, entrypoints, API paths, and host ports as implementation proceeds.
