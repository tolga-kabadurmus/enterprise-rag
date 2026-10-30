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
- Authentication (authn) and authorization (authz) are outside the scope of this project. Do not implement or present either topic as covered by this prototype.
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
- `enterprise-rag-deployment`: Kubernetes deployment repository developed with HelmChart.
- `enterprise-rag-embedding-service`: Dedicated FastAPI service that loads the shared embedding model once and produces compatible document and query vectors; indexing consumes it now and query integration remains planned.
- `enterprise-rag-indexing`: Implements the disposable, asynchronous document indexing pipeline.
- `enterprise-rag-query`: Implements the retrieval-and-answering application; detailed design is to be defined later. The minimum end-to-end prototype must nevertheless retrieve indexed chunks, call an LLM, and return the answer with sources.
- `enterprise-rag`: Orchestration repository containing the other repositories as Git submodules, shared deployment configuration, and `docker-compose.yaml`. Frankly the root repository.
- All environment variable files (*.env) must be placed on the ./dev-envs folder inside the root repository.
- For ech sub repository a seperate environment variable file is mandatory named as ./dev-envs{{of the root repository}}/{{sub-repo-name}}.env and must be used in its own docker-compose service
- All envvars (including S3 and qdrant) must be placed at a proper var name. For example S3_ACCESS_KEY, S3_EMBEDDINGS_ROOT_BUCKET , QDRANT_API_KEY
- Pydantic BaseSettings class implementing is a must for all envvar sets (for example for S3_ is a seperate BaseSettings class , for QDRANT_ )
- Inside for each repository implement ./common directory including BaseSetting class files and other utility funtions.
  - Setting files placed in ./common/settings directory
  - Utility files placed in ./common/utility directory

## enterprise-rag-deployment
- This is a Kubernetes/OpenShift deployment repository developed with Helm Charts.
- Use the Helm umbrella chart pattern.
- Helm structure must contain the following subcharts:
  - qdrant
  - rustfs
  - enterprise-rag-embedding-service
  - enterprise-rag-indexing
  - enterprise-rag-query

- Every subchart:
  - Must have its own `Chart.yaml`.
  - Must have its own dedicated `values.yaml`, containing default configurations that rarely change.
  - Environment-specific configurations must be overridden through the parent chart's values files.
  - Each Kubernetes resource must have its own dedicated template file, where applicable:
    - ConfigMap → `configmap.yaml`
    - Secret → `secret.yaml`
    - PersistentVolumeClaim → `pvc.yaml`
    - Deployment → `deployment.yaml`
    - StatefulSet → `statefulset.yaml`
    - Service → `service.yaml`
    - Ingress → `ingress.yaml`
    - Job → `job.yaml`
    - CronJob → `cronjob.yaml`
  - Do not generate unused Kubernetes resource templates.
  - Use `_helpers.tpl` for reusable Helm template definitions.

- Kubernetes workload considerations:
  - Qdrant and RustFS should use persistent storage.
  - Do not create ServiceAccount templates; workloads use the Kubernetes default ServiceAccount.
  - Do not set runtime user IDs or group IDs. Configure pod security settings to remain compatible with OpenShift-assigned UID/GID values.
  - `enterprise-rag-embedding-service` must run as a long-running FastAPI/Granian Deployment and expose an internal Kubernetes Service. Its readiness probe must not succeed until the embedding model is loaded.
  - `enterprise-rag-indexing` must run as a disposable CronJob or Job, with the default command `python -m app.main --pipeline v1 --concurrency 4`; environment-specific values may override the command.
  - `enterprise-rag-indexing` must run as a disposable Kubernetes Job or CronJob, not as a continuously running Deployment.
  - `enterprise-rag-query` must run as a Deployment.
  - `enterprise-rag-query` is a FastAPI/Granian Deployment with an internal Service and optional standard Kubernetes Ingress. Do not require an NGINX-specific controller or annotations.
  - Configure readiness/liveness probes where appropriate.
  - Configure CPU and memory requests/limits through Helm values.
  - Never hardcode credentials or sensitive information into Helm templates or committed values files.
  - Support existing Kubernetes Secrets for sensitive configuration.

- Helm validation:
  - Always validate the Helm chart structure using `helm lint`.
  - Always validate rendered Kubernetes manifests using `helm template`.
  - Validate rendered manifests using Kubernetes dry-run when a compatible cluster/API is available.
  - Fix all Helm rendering errors before considering the implementation complete.

umbrella Helm chart controlling the Kubernetes/OpenShift deployment of the complete stack.
RustFS — S3-compatible object storage for source and staging documents, with persistent storage.
Qdrant — vector storage for embeddings and source metadata, with persistent storage.
```text
enterprise-rag-deployment/              # Helm umbrella chart
├── Chart.yaml
├── values.yaml
├── values-dev.yaml                    # Development endpoint and runtime overrides
├── values-int.yaml                    # Integration endpoint and runtime overrides
├── values.uat.yaml                    # UAT endpoint and runtime overrides
├── values-prod.yaml                   # Production endpoint and runtime overrides; no secrets
└── charts/
    ├── qdrant/                        # Persistent vector database
    ├── rustfs/                        # Persistent S3-compatible storage
    ├── enterprise-rag-embedding-service/ # Shared embedding API Deployment
    ├── enterprise-rag-indexing/       # On-demand Job / optional CronJob
    └── enterprise-rag-query/          # Long-running API Deployment
```
Default application image names are `enterprise-rag-query`, `enterprise-rag-enterprise-rag-indexing`, and `enterprise-rag-embedding-service`; every image name and tag remains configurable through values files.
Each subchart contains its own `Chart.yaml`, default `values.yaml`, and `templates/` directory. Kubernetes resources should be defined in separate, purpose-named files when needed, such as `deployment.yaml`, `statefulset.yaml`, `job.yaml`, `cronjob.yaml`, `service.yaml`, `configmap.yaml`, `secret.yaml`, `pvc.yaml`, and `ingress.yaml`. Shared template helpers belong in `_helpers.tpl`. Unused resource templates should not be created. Do not create ServiceAccount templates; use the cluster default ServiceAccount.

The parent chart must provide `values-dev.yaml`, `values-int.yaml`, `values.uat.yaml`, and `values-prod.yaml`. Service endpoints, image references, commands, schedules, storage, and resource settings must be configurable through these files. Secret values must not be committed. Each `secret.yaml` must contain the comment `to be implemented by an enterprise vault` and support references to an existing Secret where appropriate. Match each secret-bearing `.env` file to its owning Helm subchart rather than sharing unrelated credentials across charts.

The indexing CronJob or Job must default to `python -m app.main --pipeline v1 --concurrency 4`, with command and arguments overridable through each environment values file. The embedding service remains a long-running FastAPI/Granian Deployment. Use ephemeral volumes for S3 staging and download paths; do not use PVCs for disposable staging data. PVCs for RustFS and Qdrant must omit a custom storage class (using the cluster default) and use `ReadWriteOnce`. The embedding service and query API Deployments must each have an HPA targeting both CPU and memory at `150` percent of requested resources. Rendered deployment manifests must be cross-checked against `docker-compose.yaml` after `helm template`, including images, ports, commands, dependencies, health checks, volumes, and environment names.

## enterprise-rag-embedding-service
- Status: FastAPI/Granian model-vectorization service implemented for local development; indexing now consumes its HTTP contract, while query migration and Kubernetes deployment remain planned.
- Implement it as a dedicated long-running FastAPI application served by Granian.
- Its only business responsibility is embedding vectorization. It accepts document chunks from `enterprise-rag-indexing` and user questions from `enterprise-rag-query`, then returns vectors produced by the same configured model and revision.
- Keep the request intent explicit so the service can apply model-specific document and query preparation consistently. For `intfloat/multilingual-e5-small`, document inputs use the `passage:` prefix and query inputs use the `query:` prefix.
- The service owns model artifact synchronization, tokenization, inference, pooling, normalization, batching, and reporting its model identity and vector dimension.
- The service must not own S3 document discovery, document extraction, chunking, Qdrant persistence/retrieval, prompt construction, or LLM calls.
- Use FastAPI lifespan/startup initialization to load the embedding model exactly once per application process and store the ready runtime on `app.state`. Request handlers must reuse that state so the API can serve multiple requests without reloading the model.
- Readiness must remain unsuccessful until startup model loading completes. Startup must fail rather than accept traffic when the configured model cannot be loaded.
- Implement `UnhandledExceptionMiddleware` to log unexpected failures while returning a safe response that does not expose internal exceptions, paths, model inputs, credentials, or stack traces to clients.
- Use Pydantic `BaseSettings` classes in `app/common/settings/` for model, S3-compatible model storage, API, and runtime configuration. Place reusable helpers in `app/common/utility/`.
- Use Pydantic `BaseModel` classes for API requests, responses, vector records, model metadata, and error payloads.
- Keep all container application code under `/app`; place repository adapters hierarchically under `/app/repository` and use constructor-based dependency injection and the dedicated capability-specific repository factory where provider selection is needed.
- Keep the service Dockerfile at `enterprise-rag-embedding-service/Dockerfiles/enterprise-rag-embedding-service`, use `dumb-init` as PID 1, and start Granian rather than a development server.
- Configure the Compose service with the root environment file `./dev-envs/enterprise-rag-embedding-service.env`. Commit only `./dev-envs/enterprise-rag-embedding-service.env.example`; never commit its real credentials.
- Provide health and readiness endpoints. Health may report that the process is alive; readiness must verify that the model runtime in `app.state` is usable.
- Bound request batch size, input length, concurrent inference, and timeouts. Do not log complete input text or returned vectors by default.
- Define a stable versioned REST contract, initially under `/v1`, used by both indexing and query HTTP repository adapters. Return model name/revision, vector dimension, and normalization information with embeddings.
- Test request validation, document/query preparation, deterministic inference fixtures, batching, concurrency bounds, startup failure, readiness, middleware sanitization, and cleanup. Keep live RustFS/model integration tests separate from unit tests.
- Maintain a dedicated MkDocs site after implementation code exists and validate it using `mkdocs build --strict`.

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
- Implement `DocumentIndexerFactory` to select the appropriate document indexer based on a validated content type (for example, `application/pdf`). Do not confuse this factory with capability-specific infrastructure factories such as `StorageRepositoryFactory` or `VectorRepositoryFactory`.
- Keep document extraction, chunking, embedding, and vector persistence as separate responsibilities.
- Obtain document embeddings through the versioned `enterprise-rag-embedding-service` API. Keep its asynchronous HTTP client behind an embedding repository contract; the indexing job must not load its own model in the normal composition. The previous local vectorizer remains only as an inactive compatibility path until separately removed.
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

## PLANNED: VERSIONED S3 DOCUMENT INDEXING PIPELINE
- Status: approved design for later implementation; do not describe it as implemented until its code and tests exist.
- Treat the CLI `--pipeline` value as a workflow version, initially `v1`, rather than as a document content type. Keep older pipeline behavior stable when a later version such as `v2` is introduced.
- Keep the three selection responsibilities distinct:
  - The pipeline registry selects the versioned top-level `AsyncIndexingJob` (`v1`, later `v2`).
  - `DocumentIndexerFactory` selects PDF, Word, HTML, or another document indexer from a normalized content type.
  - Capability-specific infrastructure repository factories select providers for their own contracts; for example, `StorageRepositoryFactory` selects S3/Ceph/NFS adapters and `VectorRepositoryFactory` selects Qdrant/Milvus adapters. They must not select document processors by content type.
- Implement the S3 repository before the document processors. Define shared repository contracts and object metadata models containing at least bucket, key, size, ETag, content type, and last-modified time.
- Implement a RustFS-compatible S3 repository with `boto3`. Read endpoint, credentials, region, addressing style, and TLS verification from validated environment configuration. Do not log credentials.
- Keep the indexing application asynchronous. Since `boto3` is blocking, execute its calls through a bounded `asyncio.to_thread()` boundary and close its client during asynchronous job cleanup.
- Support both an exact `--object-key` and all objects under the requested bucket/optional `--key-prefix`. Paginate `list_objects_v2`; do not assume the bucket contains at most 1,000 objects.
- `V1IndexingPipeline` must iterate the complete selection, isolate per-object failures, and process objects with bounded `asyncio.gather()` batches plus an `asyncio.Semaphore`. Do not create an unbounded task for every object in a large bucket.
- Resolve each object's content type before selecting its document indexer. Because S3 list responses do not normally contain content type, use object metadata/`head_object`; normalize MIME values and document any extension fallback for missing or generic content types.
- Initially map content types as follows:
  - `application/pdf` -> real `PDFDocumentIndexer`, using embedded PDF text first and RapidOCR fallback for pages without useful text.
  - Word MIME types -> `MockWordDocumentIndexer`.
  - `text/html` and `application/xhtml+xml` -> `MockHTMLDocumentIndexer`.
  - Unknown types -> an explicit unsupported-content-type result; log and skip them without corrupting the batch.
- Word and HTML mocks must report a distinct mocked/skipped status. They must not fabricate production document text, embeddings, Qdrant points, or successful indexing claims.
- Preserve deterministic document/chunk identities and source metadata. During this stage, do not delete or move source objects; document that overlapping jobs remain unsafe until the claim/locking workflow is implemented.
- Unit-test S3 pagination, exact-key access, configuration, cleanup, factory routing, MIME normalization, unsupported types, bounded concurrency, deterministic IDs, and per-object failure isolation with fakes/mocks. Keep live RustFS checks in separate integration tests.
- Update MkDocs and README documentation with the same implementation change, including the `v1` lifecycle, S3 environment variables, supported MIME mappings, mocked behavior, concurrency, retry limitations, and generated API references. Validate with unit tests, `mkdocs build --strict`, and `docker compose --profile dev config`.

## enterprise-rag-query
- Detailed internal design: to be defined later.
- Minimum required behavior for the coding exercise:
  - Accept a user question.
  - Generate a query embedding through `enterprise-rag-embedding-service`, compatible with the indexing pipeline's document vectors and dimensions.
  - Retrieve relevant chunks from Qdrant.
  - Send the question and retrieved context to a configurable LLM provider.
  - Return an answer and source references derived from retrieved chunk metadata.
  - Include logging, configuration management, and error handling.
- Use FastAPI for REST endpoints and Granian as the ASGI server.
  - Implement an UnhandledExceptionMiddleware in order to prevent undecessary events to end-user.
- Keep the embedding-service HTTP client behind a repository contract. Send questions as query inputs; do not send retrieved context back for query vectorization.
- Keep the LLM provider and model configurable; do not hard-code credentials or claim a provider selection has already been made.
- Streaming, reranking, hybrid search, memory, and multi-agent behavior remain future enhancements unless explicitly requested.

## enterprise-rag
- Orchestrate the complete stack, retaining `enterprise-rag-embedding-service`, `enterprise-rag-indexing`, `enterprise-rag-query`, and `enterprise-rag-deployment` as Git submodules.
- Keep `docker-compose.yaml` in this orchestration repository.
- Include:
  - Qdrant service with a named Docker volume for persistence.
  - RustFS service with a dedicated named Docker volume for persistence.
  - `enterprise-rag-embedding-service` as a long-running internal FastAPI/Granian service with model storage, health checks, and a development source bind mount.
  - `enterprise-rag-indexing` service with a bind mount of the local source directory for fast development.
  - `enterprise-rag-query` service for the working end-to-end RAG demonstration.
- Keep indexing as an on-demand, one-shot Compose job; do not force it to run indefinitely as a daemon.
- Make indexing and query depend on embedding-service readiness once their embedding HTTP clients are implemented; container startup alone is not readiness.
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
- At any python code;
  - if using environment variables is needed implementing Pydantic BaseSettings class is mandatory
  - if using is object class/data class is needed implement Pydantic Base class is mandatory
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
- For each python repository (for example enterprise-rag-indexing and enterprise-rag-query):
  - all codes must be placed on the /app directory at the containr
  - all repository classes must be placed at /app/repository directory with a hierarchical way
  - all repository classes must be placed at /app/repository directory with a hierarchical way
  - dockerfile must be placed at Dockerfiles repository and with the name of repository.
- Organize implementation into the following logical layers:
  - **Repositories:** Infrastructure and external-data access adapters (S3/RustFS, Qdrant, embedding APIs, LLM APIs). Keep business logic out of repositories.
  - **Usecases:** Application business logic. Preserve the original preference of one primary repository dependency per use case; when an operation requires several repositories, coordinate multiple use cases through a controller rather than bypassing this rule silently.
  - **Controllers:** Orchestrate multiple use cases when an operation is too complex for a single use case. Do not add controllers that only pass through a single call without value.
  - **REST API:** Follow REST principles. Each FastAPI endpoint invokes one use case or one controller.
- Every external connection capability must have its own dedicated base contract and registry-based factory. Do not create a catch-all `RepositoryFactory` with technology-specific methods such as `create_s3()`, `create_qdrant()`, or `create_embedding_service()`.
- Name factories and base contracts by capability, not by provider technology. Examples include `StorageRepositoryFactory` / `StorageRepositoryBase`, `VectorRepositoryFactory` / `VectorRepositoryBase`, `EmbeddingRepositoryFactory` / `EmbeddingRepositoryBase`, and `LLMRepositoryFactory` / `LLMRepositoryBase`.
- Each capability factory must expose explicit registration methods. Define provider keys as capability-specific `str, Enum` members; never scatter raw registration strings such as `"qdrant"` through composition code. Application composition selects the validated provider enum; callers must not branch directly on Qdrant, Milvus, S3, Ceph, NFS, or another implementation.
- Every provider implementation must inherit its capability base. For example, `S3Repository`, `RedhatCephFSS3Repository`, and `NFSRepository` inherit `StorageRepositoryBase`; Qdrant and Milvus implementations inherit `VectorRepositoryBase`.
- Keep a capability's base class, factory class, and all its provider implementations together in the same capability directory under `/app/repository` (for example, `/app/repository/storage/`). Do not scatter one capability's factory and implementations across unrelated locations.
- Register every supported implementation with its capability factory in the application composition/startup layer. Factories select implementations only; they must not contain provider business logic or instantiate unrelated repository capabilities.
- Keep infrastructure provider selection separate from document content-type selection in `DocumentIndexerFactory`.
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
2. Implement the shared embedding service and its compatible document/query vectorization contract.
3. Implement the PDF indexing path: RustFS -> extraction -> chunking -> embedding service -> Qdrant, including source metadata.
4. Implement the minimum query path: question -> embedding service -> retrieval -> LLM -> answer with citations.
5. Add meaningful unit/integration tests, documentation, logging, and error handling.
6. Verify the complete end-to-end prototype locally before adding optional enhancements.
7. Implement bonus features incrementally only when explicitly prioritized.

## Rules for coding agents
- Follow the repository boundaries and coding conventions above; keep changes small and readable.
- Preserve explicitly selected technology choices (RustFS, Qdrant, FastAPI, Granian, Docker Compose, `virtualenv`, Git submodules).
- Do not replace the one-shot async indexing job with an always-on service or external task queue without approval.
- Do not present unimplemented bonus features as implemented.
- If a requirement is ambiguous or technically unsafe, state the tradeoff and propose the smallest compatible change before making a significant architectural departure.
- Document assumptions and known limitations. Do not claim production readiness solely because Docker/Helm manifests exist.
