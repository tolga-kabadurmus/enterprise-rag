Enterprise RAG
`enterprise-rag` is the top-level orchestration repository for the Enterprise RAG coding exercise. It brings the asynchronous document indexing pipeline, RAG query API, MinIO object storage, and Qdrant vector database together with Docker Compose.
The prototype indexes PDF documents from S3-compatible storage, chunks them, generates embeddings, stores them in Qdrant, and uses retrieved context to answer questions with source references. PDF indexing is the initial scope; additional document formats and advanced retrieval features can be added later.
For architecture, coding standards, project boundaries, and implementation guidance, see the root `AGENTS.md`.
Repositories
`enterprise-rag` — orchestrates the complete stack and tracks the other repositories as Git submodules.
`enterprise-rag-indexing` — provides a disposable, asynchronous indexing pipeline for documents in MinIO.
`enterprise-rag-query` — provides the FastAPI RAG query service, served by Granian. Its detailed design is still to be defined.
```text
enterprise-rag (Docker Compose)
├── enterprise-rag-indexing/   # Git submodule; one-shot indexing job
├── enterprise-rag-query/      # Git submodule; RAG query API
├── MinIO                     # Compose service; S3-compatible documents
└── Qdrant                    # Compose service; vectors + source metadata
```
Git submodules
To add the component repositories to an existing `enterprise-rag` orchestration repository (run in its root directory):
```bash
git submodule add https://github.com/tolga-kabadurmus/enterprise-rag-indexing.git enterprise-rag-indexing
git submodule add https://github.com/tolga-kabadurmus/enterprise-rag-query.git enterprise-rag-query
git add .gitmodules enterprise-rag-indexing enterprise-rag-query
git commit -m "Add indexing and query submodules"
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
Clone with submodules using the command above, or update them if already cloned. Create the local configuration files from the supplied `.env.example` templates once those templates have been added. Set MinIO credentials, S3 endpoints, Qdrant connection details, and embedding/LLM provider settings. Do not commit secrets.
The following commands assume the root `docker-compose.yaml` implements services named `minio`, `qdrant`, `enterprise-rag-indexing`, and `enterprise-rag-query` as specified in `AGENTS.md`. They are intended commands, not a claim that the services have already been implemented.
Start the persistent infrastructure and query API:
```bash
docker compose up -d --build minio qdrant enterprise-rag-query
```
Inspect the services and their logs:
```bash
docker compose ps
docker compose logs -f enterprise-rag-query
```
Execute an on-demand indexing job (use the actual CLI flags implemented by the indexing application):
```bash
docker compose run --rm enterprise-rag-indexing --source-bucket documents --key-prefix ""
```
The command above is an illustrative CLI contract. It requires the indexing image to expose the application command as its entrypoint and accept `--source-bucket` and `--key-prefix`. Keep `dumb-init` as the image's PID 1 process. If the implementation chooses another CLI or entrypoint layout, update this example to match it. An explicit staging bucket may also be required by the final application configuration.
When the query application provides an HTTP endpoint, use the API and documentation URLs defined by the published ports in `docker-compose.yaml`. No host port or endpoint path is fixed yet.
Stop the running services without deleting persistent data:
```bash
docker compose down
```
To remove the stack's named volumes and stored MinIO/Qdrant data (destructive):
```bash
docker compose down -v
```
Optional development and production profiles
The previous eSIM Market project used `--profile dev` and `--profile prod`. That convention can be reused if profiles are explicitly configured in this project's Compose file, for example:
```bash
docker compose --profile dev up --build
# Or, if implemented:
docker compose --profile prod up --build
```
Profiles are not required for the initial Enterprise RAG prototype. A local source bind mount for the indexing service is required by `AGENTS.md`; production-style builds or alternate profiles may be added later.
Documentation and scope
`AGENTS.md` defines coding conventions, Clean Architecture layers, factory patterns, asynchronous resource lifecycle, and planned implementation sequence.
MkDocs is the chosen documentation framework; project-specific READMEs remain useful for local development.
Hybrid search, reranking, response streaming, conversation memory, multi-agent workflows, evaluations, Helm, CI/CD, and dashboards are optional follow-on features, not claims about the initial prototype.
This README documents the intended repository and developer workflow. Keep it synchronized with the actual Docker Compose service names, environment templates, entrypoints, API paths, and host ports as implementation proceeds.