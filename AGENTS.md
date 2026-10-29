# ABOUT
- Project: Enterprise RAG
- Task: Build a Simple Enterprise RAG Application in Python.
- Purpose: Deliver a working, understandable prototype that demonstrates enterprise-oriented design without unnecessary abstractions or overengineering.
- This file guides AI coding agents. Preserve the architecture and decisions below; do not silently substitute technologies or introduce architectural changes.

# REQUIREMENTS
The working prototype must:
- Read PDF and/or text documents (implement PDF first; keep the design extensible to text).
- Perform document chunking.
- Generate embeddings.
- Store embeddings and relevant metadata in a vector database.
- Retrieve relevant document chunks.
- Query an LLM using retrieved context.
- Return the answer together with source references (document identifier, object key, and page/chunk information where available).
- Include basic logging and error handling.
- Demonstrate clean architecture, modular design, readable code, configuration management, documentation, and production-readiness considerations.

# BUSINESS BOUNDARIES
- Produce readable, straightforward code; avoid fancy, heavily abstracted, or unnecessarily polished AI-generated code.
- Manage configuration through environment variables. Never commit credentials or secrets.
- Include explicit error handling and structured or consistently formatted logging.
- Account for production readiness without turning this prototype into a full production platform.
- The following exercise bonus features are planned enhancements, NOT prerequisites for the first working end-to-end RAG flow:
  - Hybrid search
  - Reranking
  - Streaming responses
  - Conversation memory
  - Multi-agent workflow
  - Prompt templates
  - Evaluation pipeline
  - Docker deployment (also required for this project's local infrastructure)
  - Kubernetes/OpenShift deployment manifests through a Helm chart
  - CI/CD pipeline
  - Observability dashboard
- Implement optional features incrementally. Do not add unrelated frameworks or services solely to anticipate them.

# PRE-REQUISITES
- Use Docker and Docker Compose.
- Primary host target: Ubuntu 24.04.4 LTS with Python 3.12.3.
- Use RustFS as S3-compatible object storage, deployed as a Docker Compose service using the pinned `rustfs/rustfs:1.0.4-glibc` image.
- Use Qdrant as the vector database, deployed as a Docker Compose service using a suitable container image.
- Pin compatible container image versions rather than relying on floating `latest` tags.
- Treat RustFS as an S3-compatible infrastructure adapter: keep application configuration and repository interfaces provider-neutral where practical.
- The initial RustFS deployment is single-node, single-disk development storage without redundancy. Do not present it as a production storage topology.
- Do not reuse a MinIO data volume as a RustFS data volume. Migrate existing objects through the S3 API because MinIO on-disk compatibility is not assumed.

## Repository structure
- `enterprise-rag-indexing`: Implements the disposable, asynchronous document indexing pipeline.
- `enterprise-rag-query`: Implements the retrieval-and-answering application; detailed design is to be defined later. The minimum end-to-end prototype must nevertheless retrieve indexed chunks, call an LLM, and return the answer with sources.
- `enterprise-rag`: Orchestration repository containing the other repositories as Git submodules, shared deployment configuration, and `docker-compose.yaml`.

## enterprise-rag-indexing
- Implement the indexing pipeline with `asyncio` and asynchronous resource cleanup.
- Use an asynchronous context manager: `__aenter__()` initializes clients/resources and `__aexit__()` closes/releases them, including when errors occur.
- Trigger an indexing job with `async with`, not synchronous `with`.
- Preferred usage:

  ```python
  async with PDFDocumentIndexing(...) as indexer:
      await indexer.run()
  ```

- The indexing process is a one-shot job: execute the requested indexing work, report success/failure, release resources, and exit. It is not a permanently running worker.
- Start with PDF indexing, while allowing more document content types to be supported later.
- Implement `DocumentIndexerFactory` to select the appropriate document indexer based on a validated content type (for example, `application/pdf`). Do not confuse this factory with infrastructure `RepositoryFactory`.
- Keep document extraction, chunking, embedding, and vector persistence as separate responsibilities.
- Preserve document identity and source metadata so retrieved chunks can cite their origin. Store at least source bucket, object key, document identifier, chunk identifier, and page number where available.
- Dockerfile entrypoint must use `dumb-init` for signal forwarding and process cleanup.
- Read S3 endpoint, access key, secret key, and other credentials/configuration from environment variables; keep local values in a separate, Git-ignored `.env` file, and provide a safe `.env.example`.
- Get the source bucket and optional key prefix from command-line arguments when the indexing pipeline is invoked. Document any additional staging bucket arguments or configuration.
- A single pipeline job should process eligible documents from the specified source bucket/prefix concurrently, using `asyncio.gather()` with a concurrency limit (for example, an `asyncio.Semaphore`). Use threads/processes only for operations demonstrated to be blocking or CPU-intensive.
- Preserve the original source-to-staging workflow to avoid duplicate work, with the following safeguards:
  - Object movement in S3-compatible storage is not inherently atomic; it is normally a copy followed by delete.
  - Define an explicit claim/processing state so overlapping jobs cannot assume a move alone prevents duplicates.
  - Use deterministic document/chunk IDs and idempotent vector upserts to make retrying safe.
  - Do not silently delete the only durable copy of a source document after a partial failure.
  - Record per-document success/failure and make failures retriable.
  - If a complete claim/locking mechanism is not implemented in the prototype, document that limitation and avoid running overlapping jobs against the same input objects.
- Handle empty documents, unsupported content types, extraction failures, embedding/provider failures, and vector database failures without corrupting the batch state.
- Log object identifiers, document counts, chunk counts, elapsed time, and failures. Do not log secret values or full document contents by default.

## enterprise-rag-query
- Detailed internal design: to be defined later.
- Minimum required behavior for the coding exercise:
  - Accept a user question.
  - Generate a query embedding compatible with the indexing pipeline's embedding model and dimensions.
  - Retrieve relevant chunks from Qdrant.
  - Send the question and retrieved context to a configurable LLM provider.
  - Return an answer and source references derived from retrieved chunk metadata.
  - Include logging, configuration management, and error handling.
- Use FastAPI for REST endpoints and Granian as the ASGI server.
  - Implement an UnhandledExceptionMiddleware in order to prevent undecessary events to end-user.
- Keep the LLM provider and model configurable; do not hard-code credentials or claim a provider selection has already been made.
- Streaming, reranking, hybrid search, memory, and multi-agent behavior remain future enhancements unless explicitly requested.

## enterprise-rag
- Orchestrate the complete stack, retaining `enterprise-rag-indexing` and `enterprise-rag-query` as Git submodules.
- Keep `docker-compose.yaml` in this orchestration repository.
- Include:
  - Qdrant service with a named Docker volume for persistence.
  - RustFS service with a dedicated named Docker volume for persistence.
  - `enterprise-rag-indexing` service with a bind mount of the local source directory for fast development.
  - `enterprise-rag-query` service for the working end-to-end RAG demonstration.
- Keep indexing as an on-demand, one-shot Compose job; do not force it to run indefinitely as a daemon.
- Use health checks and appropriate startup dependencies where useful; readiness must be verified by the client and must not be assumed from container startup alone.
- Document local setup, indexing invocation, querying, and teardown in the README.
- Keep the root `README.md` concise and aligned with the orchestration repository: purpose, repository links, topology, setup, Git submodule commands, Docker Compose commands, and links to `AGENTS.md`.
- Follow the established submodule workflow: `git clone --recurse-submodules` when cloning, `git submodule add` when registering a new component, and `git submodule update --init --recursive` when restoring submodules. Record new submodule pointers in the orchestration repository.
- Use `docker compose` (Compose v2) command syntax. The local development workflow should document `docker compose up -d --build`, one-shot `docker compose run --rm ...`, service logs, and `docker compose down`. Make command examples match actual service names and configured flags.
- Development source bind mounts are required for the indexing service; a separate production-style profile/image is optional. Do not advertise `--profile dev` or `--profile prod` as working until these profiles exist in `docker-compose.yaml`.
- Commit only safe `.env.example` templates. Keep actual `.env` files and credentials ignored by Git; avoid assuming the earlier eSIM Market project's environment-file naming has been adopted here.

# TECHNICAL BOUNDARIES
- Use Python as the primary programming language.
- Documentation framework: MkDocs, selected for its lightweight Markdown-first workflow and suitability for a small multi-repository Python prototype. Keep useful README files in each repository.
- MkDocs documentation is mandatory for each Python project once implementation code exists. Each such project must include a working `mkdocs.yml`, a `docs/` directory, and pinned documentation dependencies separate from runtime dependencies where practical.
- At minimum, each Python project's MkDocs site must document its current implementation status, architecture and layer boundaries, configuration/environment variables, CLI or API usage, local development and test commands, error/lifecycle behavior, and known limitations. Clearly label planned behavior; never present it as implemented.
- Public Python modules, classes, functions, and non-trivial methods must have useful docstrings covering purpose, important arguments, return values, raised exceptions, lifecycle/cleanup requirements, and side effects where applicable. Generate an API reference from these docstrings with `mkdocstrings` or an equivalently lightweight MkDocs integration.
- Documentation must be updated in the same change as the behavior or public contract it describes. A README should link developers to the full MkDocs site but must not replace it.
- Treat `mkdocs build --strict` as a required documentation validation step. Do not commit generated `site/` output.
- Use modular design and Docker/Docker Compose.
- Use Python virtual environments created with the `virtualenv` module.
- Each Python project must have its own `requirements.txt`; pin or constrain dependencies to reproducible compatible versions.
- Keep each project's Dockerfile in its own `Dockerfiles/` directory, and maintain its own Docker build pipeline. In the orchestration repository, reference each project's Dockerfile explicitly in Compose build configuration.
- Prefer Python standard library features where sufficient. Avoid introducing a framework when a small, readable module does the job.

## Clean Architecture conventions
- Organize implementation into the following logical layers:
  - **Repositories:** Infrastructure and external-data access adapters (S3/RustFS, Qdrant, embedding APIs, LLM APIs). Keep business logic out of repositories.
  - **Usecases:** Application business logic. Preserve the original preference of one primary repository dependency per use case; when an operation requires several repositories, coordinate multiple use cases through a controller rather than bypassing this rule silently.
  - **Controllers:** Orchestrate multiple use cases when an operation is too complex for a single use case. Do not add controllers that only pass through a single call without value.
  - **REST API:** Follow REST principles. Each FastAPI endpoint invokes one use case or one controller.
- Instantiate infrastructure repository implementations through `RepositoryFactory` to support different providers. Keep provider selection separate from document content-type selection in `DocumentIndexerFactory`.
- Repository classes must inherit from a shared repository base or implement a shared repository interface/abstract base class.
- Use case classes must inherit from a shared use case base or implement an agreed abstract base contract. Keep base classes small and purposeful.
- Use constructor-based dependency injection:

  ```python
  usecase: XUsecase = XUsecase(repo=XRepository(...))
  controller: XController = XController(
      usecase_x=XUsecase(repo=XRepository(...)),
      usecase_y=YUsecase(repo=YRepository(...)),
  )
  ```

- Build dependencies in the application composition/startup layer; do not create infrastructure clients inside business use case methods.
- Do not test external repository integrations as unit tests. **Do** unit-test use cases, controllers, factories, and pure transformations with mocks/fakes for repositories. Test RustFS/Qdrant integrations separately with integration tests.
- Centralize configuration validation and exception handling. Preserve error causes in logs; avoid exposing internal exceptions or secrets through REST responses.
- For REST APIs, always use FastAPI and run with Granian.

## Delivery and implementation sequence
1. Establish repository layout, dependency installation, environment configuration, and Docker Compose infrastructure.
2. Implement the PDF indexing path: RustFS -> extraction -> chunking -> embedding -> Qdrant, including source metadata.
3. Implement the minimum query path: question -> query embedding -> retrieval -> LLM -> answer with citations.
4. Add meaningful unit/integration tests, documentation, logging, and error handling.
5. Verify the complete end-to-end prototype locally before adding optional enhancements.
6. Implement bonus features incrementally only when explicitly prioritized.

## Rules for coding agents
- Follow the repository boundaries and coding conventions above; keep changes small and readable.
- Preserve explicitly selected technology choices (RustFS, Qdrant, FastAPI, Granian, Docker Compose, `virtualenv`, Git submodules).
- Do not replace the one-shot async indexing job with an always-on service or external task queue without approval.
- Do not present unimplemented bonus features as implemented.
- If a requirement is ambiguous or technically unsafe, state the tradeoff and propose the smallest compatible change before making a significant architectural departure.
- Document assumptions and known limitations. Do not claim production readiness solely because Docker/Helm manifests exist.
