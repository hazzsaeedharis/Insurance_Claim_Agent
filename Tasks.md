Nice — below is a **machine-executable, bite-sized MVP backlog** you can hand to an engineering LLM.
Each item is **atomic**, has a **clear start + end**, **one concern**, and **concrete acceptance tests**. Execute tasks in order where dependencies are listed; otherwise they can be run in parallel.

> How to use: pick a task ID, hand it to the engineering LLM, run the acceptance tests, then mark it done and move to the next task. If a task lists dependencies, complete those first.

# MVP Tasks (grouped by subsystem)

---

## Project & data bootstrap (PROJ)

**PROJ-01 — Create monorepo skeleton**

* **Start:** empty repo created
* **End:** monorepo with folders: `/services`, `/web`, `/infra`, `/data`, `/tests`, `/docs`
* **Acceptance tests:** `git clone` shows those folders; README.md exists with 1-line purpose.
* **Deps:** none

**PROJ-02 — Add CONTRIBUTING + issue template**

* **Start:** monorepo present
* **End:** `.github/ISSUE_TEMPLATE/bug.md`, `task_template.md` with fields: ID, Description, Start, End, Tests.
* **Acceptance tests:** open `task_template.md` and see required fields.

**PROJ-03 — Create synthetic claims generator (script stub)**

* **Start:** monorepo present
* **End:** `data/gen_synthetic_claims.py` that, when run, outputs 10 JSON claim objects to `data/synthetic/` (no PDFs yet).
* **Acceptance tests:** running script creates `data/synthetic/claim_001.json` … `claim_010.json`.

**PROJ-04 — Generate 5 synthetic PDF receipts (placeholder)**

* **Start:** PROJ-03 done
* **End:** `data/synthetic_pdfs/` contains 5 simple PDFs (text receipt, claim form) created from the JSONs.
* **Acceptance tests:** `file` or `ls` shows 5 PDFs; each PDF is readable text (no OCR needed yet).

---

## Dev infra & local run (INFRA)

**INFRA-01 — Add Dockerfile template for microservices**

* **Start:** monorepo exists
* **End:** `infra/dockerfiles/Dockerfile.micro` (base image, copy, entrypoint)
* **Acceptance tests:** `docker build -f infra/dockerfiles/Dockerfile.micro .` completes (can be minimal).

**INFRA-02 — Add docker-compose for local dev**

* **Start:** Dockerfile.micro present
* **End:** `infra/docker-compose.yml` with services: `postgres`, `minio`, `keycloak` (or placeholder), and `one example service` (healthcheck)
* **Acceptance tests:** `docker-compose -f infra/docker-compose.yml up --build` starts containers and healthcheck passes.

**INFRA-03 — Create basic K8s manifests (namespace + secrets k8s template)**

* **Start:** monorepo exists
* **End:** `infra/k8s/namespace.yml` and `infra/k8s/secret-template.yml`
* **Acceptance tests:** `kubectl apply -f infra/k8s/namespace.yml --dry-run=client` returns success.

**INFRA-04 — Set up CI skeleton (GitHub Actions)**

* **Start:** repo present
* **End:** `.github/workflows/ci.yml` that runs tests: lint + `python -m pytest` placeholder
* **Acceptance tests:** push triggers workflow (or `act` run) and shows the job steps.

**INFRA-05 — Add basic logging & metrics library glue**

* **Start:** service template present
* **End:** `/services/common/logging.py` with standardized logger factory and `/services/common/metrics.py` stub exporting `increment(metric)` function
* **Acceptance tests:** import logger and call in a small script; output logs to console.

---

## Authentication & RBAC (AUTH)

**AUTH-01 — Add Keycloak dev container in docker-compose**

* **Start:** infra docker-compose running
* **End:** Keycloak service added and starts with admin user env vars in compose
* **Acceptance tests:** GET to Keycloak admin endpoint returns 200 (or reachable).

**AUTH-02 — Define RBAC roles & scopes**

* **Start:** AUTH-01 done
* **End:** JSON `auth/roles.json` containing roles: `customer`, `adjuster`, `admin`, `system`
* **Acceptance tests:** role JSON loads into Keycloak using admin API curl (or saved for manual import).

**AUTH-03 — Implement auth middleware stub for services**

* **Start:** services/common present
* **End:** `services/common/auth_middleware.py` that validates JWT signature and role claim (mockable)
* **Acceptance tests:** calling a sample endpoint with a valid JWT returns 200; invalid JWT returns 401.

---

## Data model & API contracts (DATA)

**DATA-01 — Define minimal Claim JSON contract**

* **Start:** monorepo
* **End:** `specs/claim.json` (OpenAPI component or JSON Schema) with fields: `claim_id`, `customer_id`, `items[]` (date, provider, code, net\_amount, currency), `documents[]`, `status`, `created_at`
* **Acceptance tests:** JSON Schema validator accepts a sample claim JSON.

**DATA-02 — DB schema: claims table migration**

* **Start:** Postgres running (docker-compose)
* **End:** `infra/migrations/0001_create_claims.sql` creating `claims` table with columns matching claim JSON
* **Acceptance tests:** apply migration to local Postgres; `SELECT * FROM information_schema.tables WHERE table_name='claims'` returns row.

**DATA-03 — DB schema: documents table migration**

* **Start:** DATA-02 done
* **End:** migration file creating `documents` table (claim\_id FK, filename, storage\_key, checksum)
* **Acceptance tests:** apply migration and verify table exists.

**DATA-04 — Create API skeleton for Claims service**

* **Start:** service template present
* **End:** REST API with `POST /claims` (create), `GET /claims/{id}` (read)
* **Acceptance tests:** `curl -X POST /claims` with a sample JSON returns 201 and location header; `GET` returns stored JSON.

---

## Document intake & storage (DOC)

**DOC-01 — Implement `POST /claims/{id}/documents` endpoint**

* **Start:** DATA-04 done
* **End:** Endpoint accepts multipart/form-data file, saves metadata to `documents` table, returns `document_id`
* **Acceptance tests:** POST with a synthetic PDF stores DB row and returns ID.

**DOC-02 — Integrate MinIO (S3 compatible) for document storage**

* **Start:** MinIO running in docker-compose
* **End:** upload code that stores uploaded PDF under `claims/{claim_id}/{doc_uuid}.pdf` and returns `storage_key`
* **Acceptance tests:** object exists in MinIO via `mc` or SDK list.

**DOC-03 — Add checksum & basic virus-scan stub**

* **Start:** DOC-02 done
* **End:** After upload compute SHA256 checksum and store in DB; call a `virus_scan()` stub that returns `clean`
* **Acceptance tests:** checksum present in DB; `virus_scan()` returns `clean` in response.

**DOC-04 — Metadata extractor: store filename, size, mimetype**

* **Start:** DOC-02 done
* **End:** DB stores `filename`, `size_bytes`, `mimetype` for uploaded documents
* **Acceptance tests:** DB columns populated after upload.

**DOC-05 — Add webhook/event: emit `document.uploaded` event to an internal queue**

* **Start:** message broker (e.g., RabbitMQ or Redis) running
* **End:** event message posted with `{claim_id, document_id, storage_key}` when upload succeeds
* **Acceptance tests:** consuming the queue returns the event payload.

---

## OCR & preprocessing (OCR)

**OCR-01 — Add OCR microservice skeleton**

* **Start:** services folder
* **End:** `services/ocr` with `POST /ocr/extract` accepting `storage_key`
* **Acceptance tests:** hitting endpoint with a dummy storage\_key returns 200 and `{"text": ""}` (placeholder).

**OCR-02 — Implement image preprocessing: deskew + denoise function**

* **Start:** OCR-01 done
* **End:** `ocr/preprocess.py` exposing `preprocess_bytes(bytes)->bytes`
* **Acceptance tests:** run preprocess on sample PDF bytes and confirm output bytes are non-empty & smaller or same size.

**OCR-03 — Integrate Tesseract (local) or Dockerized OCR engine**

* **Start:** OCR-01 & preprocess ready
* **End:** OCR service calls tesseract on preprocessed page images and returns extracted text
* **Acceptance tests:** provide one synthetic PDF; `POST /ocr/extract` returns non-empty text including known words from PDF.

**OCR-04 — Persist OCR output to DB**

* **Start:** OCR-03 done
* **End:** store `ocr_text` and `ocr_confidence` in `documents` table
* **Acceptance tests:** after OCR call, DB row updated with `ocr_text`.

**OCR-05 — Add language detection (DE/EN) on OCR text**

* **Start:** OCR-03 done
* **End:** function `detect_language(text)->'de'|'en'|other` and store in DB
* **Acceptance tests:** German test PDF returns 'de'.

**OCR-06 — Add page-level extraction metadata**

* **Start:** OCR-03 done
* **End:** store page count and per-page text snippets in a `document_pages` table
* **Acceptance tests:** synthetic multi-page PDF results in 2+ `document_pages` rows.

---

## Document parsing & field extraction (EXTRACT)

**EX-01 — Implement doc-type classifier**

* **Start:** OCR text stored
* **End:** function `classify_document(ocr_text)->'claim_form'|'receipt'|'invoice'|unknown` using keywords
* **Acceptance tests:** known claim form text returns `claim_form`.

**EX-02 — Build field extractor for standard claim form (regex rules)**

* **Start:** EX-01 done
* **End:** `extract_claim_form_fields(ocr_text)->{name,dob,policy_id,claim_date,total_amount}` implemented with unit tests
* **Acceptance tests:** run on synthetic claim form PDF; extracted fields match expected.

**EX-03 — Build line-item extractor for receipts (tabular parser)**

* **Start:** EX-01 done
* **End:** `extract_receipt_items(ocr_text)->items[]` where each item has date, code/desc, amount
* **Acceptance tests:** synthetic receipt yields correct `items[]` and amounts sum to total.

**EX-04 — Map extracted fields to Claim JSON**

* **Start:** EX-02 & EX-03 done
* **End:** create a function that merges extracted data into `claim` object and updates DB
* **Acceptance tests:** submitted PDF results in a DB claim row with `items[]` populated.

**EX-05 — Add confidence score per extracted field**

* **Start:** EX-02 done
* **End:** extraction returns `{value, confidence}` for each field and stores confidence
* **Acceptance tests:** confidence fields present and between 0-1.

**EX-06 — Implement manual correction endpoint for adjusters**

* **Start:** EX-04 done
* **End:** `POST /claims/{id}/extraction-correction` that updates claim fields and logs user & timestamp
* **Acceptance tests:** sending corrections updates DB and creates an audit entry.

---

## Policy ingestion & rule schema (POL)

**POL-01 — Task: Upload Hallesche NK.select S PDF to system**

* **Start:** account/user with upload rights exists
* **End:** `policies/` contains `hallesche_nk_select_s.pdf` and DB entry `policies` created
* **Acceptance tests:** file accessible and DB row exists.

**POL-02 — Task: Upload TK statutory terms PDF to system**

* **Start:** POL-01 done
* **End:** `policies/tk_statutory_terms.pdf` saved with DB record
* **Acceptance tests:** file accessible and DB row exists.

**POL-03 — Define policy rule JSON schema**

* **Start:** POL-01 & POL-02 done
* **End:** `specs/policy_rule.json` that can express: covered\_item\_codes\[], coverage\_pct, deductible\_eur, exceptions, annual\_caps
* **Acceptance tests:** schema validates a sample rule JSON.

**POL-04 — Create one example rule: "general outpatient consultation"**

* **Start:** POL-03 done
* **End:** `policies/hallesche/rule_outpatient_consult.json` mapping a simple coverage % and deductible
* **Acceptance tests:** rule JSON parsed by rule engine (later) without errors.

**POL-05 — Create one example rule for TK statutory "sickness benefit"**

* **Start:** POL-03 done
* **End:** `policies/tk/rule_example.json` created
* **Acceptance tests:** file exists and conforms to schema.

**POL-06 — Implement policy upload endpoint + list**

* **Start:** policies DB table present
* **End:** `POST /policies` and `GET /policies`
* **Acceptance tests:** upload a policy PDF via endpoint; GET returns it.

**POL-07 — Small task: manual mapping task template**

* **Start:** POL-03 done
* **End:** `docs/policy_mapping_template.md` describing how to map a clause to rule JSON (one clause per file)
* **Acceptance tests:** template exists with example mapping.

---

## Rule evaluation engine (RULE)

**RULE-01 — Add rule engine skeleton (service)**

* **Start:** monorepo
* **End:** `services/rule_engine` with `POST /evaluate` accepting `{claim, policy_rules[]}`
* **Acceptance tests:** POST with empty rule array returns `{"result":"no-rule"}`.

**RULE-02 — Implement rule matching: item code -> rule lookup**

* **Start:** RULE-01 done
* **End:** function `match_rules(claim_item, rules)->matched_rules[]`
* **Acceptance tests:** sample claim item returns the expected rule id when rule exists.

**RULE-03 — Implement single rule evaluation returning coverage percent & reason**

* **Start:** RULE-02 done
* **End:** `evaluate_rule(claim_item, rule)->{payable_amount, reason}`
* **Acceptance tests:** with rule coverage\_pct=80 and item 100 EUR, payable\_amount is 80 EUR.

**RULE-04 — Add support for deductibles (annual, per-claim)**

* **Start:** RULE-03 done
* **End:** evaluator can apply deductible thresholds (stateful: reads account `deductible_used` field)
* **Acceptance tests:** when deductible remaining 50 EUR and claim 100, payable becomes 50 (minus ded).

**RULE-05 — Build unit tests for rules with 5 deterministic cases**

* **Start:** RULE-04 done
* **End:** tests covering coverage %, deductible, exceptions, caps, multiple-items
* **Acceptance tests:** `pytest` passes.

---

## Settlement calculation engine (SETTLE)

**SET-01 — Create settlement service skeleton**

* **Start:** monorepo
* **End:** `services/settlement` with `POST /settle` accepting `{claim, matched_rules, policy_state}` and returning `settlement_proposal`
* **Acceptance tests:** calling `POST /settle` with simple data returns a `settlement_proposal` JSON.

**SET-02 — Implement item-level calculation (apply coverage % + deductible)**

* **Start:** SET-01 + RULE-03 done
* **End:** `calculate_item(item, rule, deductible_state)->{payable, breakdown}`
* **Acceptance tests:** known inputs produce expected numeric outputs.

**SET-03 — Implement claim-level aggregation & rounding rules**

* **Start:** SET-02 done
* **End:** aggregator sums items, applies caps, returns `total_payable` and `breakdown_per_item`
* **Acceptance tests:** aggregated total equals sum of per-item payables; rounding to cents.

**SET-04 — Persist settlement proposal to DB with versioning**

* **Start:** SET-03 done
* **End:** `settlements` table with `proposal_json`, `version`, `created_by`
* **Acceptance tests:** after `POST /settle`, DB row created with version=1.

**SET-05 — Add test case for partial payment + co-insurance**

* **Start:** SET-02 done
* **End:** unit test demonstrating co-insurance calculation
* **Acceptance tests:** test passes.

---

## Fraud detection (FRAUD)

**FRAUD-01 — Create simple rule-based fraud service skeleton**

* **Start:** monorepo
* **End:** `services/fraud` with `POST /score` accepting `claim` and returning `risk_score` and `flags[]`
* **Acceptance tests:** POST returns `risk_score` between 0-1.

**FRAUD-02 — Implement rule: duplicate invoice detection by `invoice_number` + `provider`**

* **Start:** FRAUD-01 done
* **End:** check DB for same invoice\_number/provider in last 365 days; flag if found
* **Acceptance tests:** inserting a duplicate invoice leads to `flags` containing `"duplicate_invoice"` and `risk_score` increases.

**FRAUD-03 — Implement rule: amount anomaly (Z-score vs historical avg for provider)**

* **Start:** FRAUD-01 done
* **End:** compute provider mean and std from past claims; flag if >3σ
* **Acceptance tests:** synthetic claim with amount >> historical triggers flag.

**FRAUD-04 — Implement rule: date mismatch (service date > submission date)**

* **Start:** FRAUD-01 done
* **End:** flag if service\_date > submission\_date
* **Acceptance tests:** claim with future service date flagged.

**FRAUD-05 — Provide risk scoring aggregator**

* **Start:** FRAUD-02..FRAUD-04 done
* **End:** weighted sum aggregator returns `risk_score` and top-3 flags
* **Acceptance tests:** known flagged case yields score > threshold.

**FRAUD-06 — Emit `claim.flagged.fraud` event when `risk_score` > 0.7**

* **Start:** FRAUD-05 done
* **End:** event posted to internal queue with claim id, score, flags
* **Acceptance tests:** submit high-risk claim and verify event in queue.

---

## Orchestration & workflow (WF)

**WF-01 — Add lightweight workflow orchestrator (state machine)**

* **Start:** services skeleton
* **End:** `services/workflow` implementing states: `received` → `extracted` → `evaluated` → either `auto_approved` or `flagged_for_review` or `rejected`
* **Acceptance tests:** POST a claim to orchestrator and follow state transitions in sequence via API.

**WF-02 — Wire document.uploaded → OCR → extraction → rule evaluation → settlement**

* **Start:** DOC-05 event system and OCR and EX and RULE services available
* **End:** a claim with uploaded document flows end-to-end and reaches `evaluated` state with `settlement_proposal`
* **Acceptance tests:** upload synthetic claim PDF; after workflow completes, claim status `evaluated` and `settlement_proposal` exists.

**WF-03 — Implement manual review queue (adjuster assignment)**

* **Start:** WF-02 done
* **End:** flagged claims appear in `adjuster_queue` with assignment API `POST /adjuster/assign`
* **Acceptance tests:** high-risk claim appears in queue; assignment call sets `assigned_to` and updates claim status.

**WF-04 — Implement "override decision" action by adjuster**

* **Start:** WF-03 done
* **End:** `POST /claims/{id}/override` that accepts `decision` and `note` and updates settlement and logs auditor ID
* **Acceptance tests:** override request updates settlement status and creates audit log.

---

## Letters & communications (COMM)

**COMM-01 — Create template engine skeleton (Jinja2 or similar)**

* **Start:** monorepo
* **End:** `services/communication/templates/` with `approval_de_en.html` and `denial_de_en.html` placeholders
* **Acceptance tests:** rendering template with sample data returns HTML for both languages.

**COMM-02 — Implement `POST /claims/{id}/generate-letter?lang=de|en&type=approval|denial`**

* **Start:** COMM-01 done
* **End:** endpoint generates HTML and stores PDF in MinIO and returns `letter_doc_id`
* **Acceptance tests:** calling endpoint returns `letter_doc_id` and PDF exists in storage.

**COMM-03 — Add notification sender stub (email + SMS)**

* **Start:** COMM-02 done
* **End:** function `notify(customer_id, channel, template_id)` that logs a `notification` row and emits an event
* **Acceptance tests:** calling notify inserts DB row and event is emitted.

**COMM-04 — Save all correspondence to audit trail**

* **Start:** COMM-02 done
* **End:** DB `correspondence` table saving `claim_id`, `template`, `lang`, `sent_at`, `storage_key`
* **Acceptance tests:** after generating letter and notify, correspondence row exists.

---

## Payments & reconciliation (PAY)

**PAY-01 — Add payment service skeleton**

* **Start:** monorepo
* **End:** `services/payments` with `POST /payments/create` and `POST /payments/callback`
* **Acceptance tests:** `POST /payments/create` returns `payment_id` and `status: created`.

**PAY-02 — Implement SEPA payment request payload generator (mock)**

* **Start:** PAY-01 done
* **End:** function `make_sepa_payload(claim_id, amount, beneficiary)` returning valid XML or JSON mock
* **Acceptance tests:** payload contains IBAN, BIC, amount, reference with `CLAIM-{claim_id}`.

**PAY-03 — Implement payment callback handler that marks claim paid**

* **Start:** PAY-02 done
* **End:** `POST /payments/callback` accepts `{payment_id, status, settled_at}` and updates settlement and claim status
* **Acceptance tests:** hitting callback sets `claim.status = paid` and stores `settlement.paid_at`.

**PAY-04 — Add reconciliation report generator**

* **Start:** PAY-03 done
* **End:** `GET /payments/reconciliation?date=YYYY-MM-DD` returns list of payments and status
* **Acceptance tests:** create one mock payment and `GET` returns it.

---

## UI: Customer, Adjuster, Admin (UI)

**UI-01 — Create React skeleton with Tailwind**

* **Start:** monorepo
* **End:** `/web/app` with `npm start` scaffold, empty routes for `/customer`, `/adjuster`, `/admin`
* **Acceptance tests:** `npm start` serves the app and routes load.

**UI-02 — Customer: upload claim form page**

* **Start:** UI-01 done
* **End:** page with file input and `POST /claims` + `POST /claims/{id}/documents` integration
* **Acceptance tests:** upload creates claim and document; show returned claim id.

**UI-03 — Customer: claim status page**

* **Start:** UI-02 done
* **End:** page that calls `GET /claims/{id}` and displays `status`, `settlement_proposal`
* **Acceptance tests:** status updates when CLI triggers state change.

**UI-04 — Adjuster: flagged claims queue**

* **Start:** UI-01 done
* **End:** page listing `flagged` claims with `view details`, `approve`, `reject`, `request more info`
* **Acceptance tests:** clicking approve calls `POST /claims/{id}/override` and updates status.

**UI-05 — Admin: policy rule editor (simple JSON editor)**

* **Start:** UI-01 done
* **End:** editor page that loads a rule JSON, allows edit, and `POST /policies/rules/{id}`
* **Acceptance tests:** edit and save persists the rule and affects rule evaluation (smoke test).

**UI-06 — Add login flow (JWT) and role-based route protection**

* **Start:** AUTH-03 and Keycloak running
* **End:** frontend authenticates via Keycloak/OIDC and shows pages per role
* **Acceptance tests:** user with adjuster role sees adjuster routes; customer role blocked.

---

## Audit, logging, compliance (AUDIT)

**AUD-01 — Event audit trail: append-only event table**

* **Start:** DB available
* **End:** `events` table with `id, event_type, payload, created_at, actor_id` and insert mechanism
* **Acceptance tests:** important actions (upload, settle, override) insert events.

**AUD-02 — Export compliance report endpoint**

* **Start:** events exist
* **End:** `GET /compliance/report?from=..&to=..` returns CSV of events filtered for regulators
* **Acceptance tests:** call endpoint with date range and CSV contains events.

**AUD-03 — Implement pseudonymization function**

* **Start:** services/common present
* **End:** `pseudonymize(customer_data)->pseudonym_id` and reversible via secure key; store mapping in `pd_map` table
* **Acceptance tests:** calling function returns `pseudonym_id`; mapping stored.

**AUD-04 — Data retention delete job**

* **Start:** AUD-03 done
* **End:** job `DELETE /data/retention?older_than=YYYY-MM-DD` that deletes PII beyond retention and logs event
* **Acceptance tests:** create an older synthetic claim, run job, PII removed but pseudonym id remains with deletion event.

---

## Monitoring, testing & performance (QA)

**QA-01 — Add unit test template & CI integration**

* **Start:** CI skeleton done
* **End:** `tests/test_sample.py` with one passing test; CI run executes it
* **Acceptance tests:** CI shows green for unit tests.

**QA-02 — Add end-to-end test: upload PDF → OCR → extraction → settle**

* **Start:** services running locally
* **End:** `tests/e2e/test_end_to_end.py` triggers the workflow using synthetic PDF and asserts final `claim.status == evaluated`
* **Acceptance tests:** test passes locally.

**QA-03 — Add load test script to simulate 1000 claims/day (burst test)**

* **Start:** e2e test passes
* **End:** `load/run_load_test.py` that can replay 200 requests/minute for 1 hour on local env (adjustable)
* **Acceptance tests:** script completes and produces latency metrics.

**QA-04 — Add basic Prometheus metrics in services (request latency, error rate)**

* **Start:** services skeleton present
* **End:** `/metrics` endpoint exposing `http_requests_total`, `http_request_duration_seconds`
* **Acceptance tests:** scraping `/metrics` returns metrics lines.

**QA-05 — Add basic alert rule (automation% drop)**

* **Start:** metrics being emitted
* **End:** rule in `infra/alerts/automation_drop.yml` that triggers when automation% < 50% for 10m
* **Acceptance tests:** simulated metric breach would match rule (dry-run).

---

## Docs & handoff (DOCS)

**DOCS-01 — Generate OpenAPI for Claims service**

* **Start:** API endpoints implemented
* **End:** `docs/openapi/claims.yaml` with `POST /claims` and `GET /claims/{id}`
* **Acceptance tests:** swagger UI can render the file.

**DOCS-02 — Write runbook for `flagged_for_review` incidents**

* **Start:** workflow implemented
* **End:** `docs/runbooks/flagged_review.md` listing steps to triage and escalate
* **Acceptance tests:** runbook contains checklist and contact placeholders.

**DOCS-03 — Create handoff checklist for production rollout**

* **Start:** MVP systems implemented
* **End:** `docs/handoff_checklist.md` with items: backups, secrets rotated, monitoring enabled, legal sign-offs
* **Acceptance tests:** checklist file present.

---

## Sample policy-mapping micro tasks (repeatable) — do this per clause (POL-MAP)

> These are intentionally tiny. Repeat for each policy clause you must support.

**POL-MAP-01 — Identify clause in PDF and create mapping file (one clause)**

* **Start:** policy PDF uploaded (POL-01/POL-02)
* **End:** `policies/hallesche/clause_01.md` with exact clause text copy + page number
* **Acceptance tests:** file exists and contains a verbatim short excerpt (<100 words) and page number.

**POL-MAP-02 — Encode the clause into rule JSON (one clause)**

* **Start:** POL-MAP-01 done
* **End:** `policies/hallesche/rule_clause_01.json` that follows `specs/policy_rule.json`
* **Acceptance tests:** JSON validates against `policy_rule.json` schema.

**POL-MAP-03 — Add unit test demonstrating clause behavior**

* **Start:** POL-MAP-02 done
* **End:** `tests/policies/test_clause_01.py` exercising evaluation of that rule against an example claim
* **Acceptance tests:** test passes.

*(Repeat POL-MAP-01..03 for each meaningful clause for Hallesche and TK — aim for core 8–12 clauses first in MVP: covered treatments, deductibles, co-insurance, annual caps, pre-authorization requirements, provider restrictions, excluded services, claim submission deadlines.)*

---

## Final MVP validation tasks

**VAL-01 — Run end-to-end scenario: normal claim (auto-approve)**

* **Start:** services all running, rules loaded
* **End:** process a synthetic normal claim end-to-end and assert `claim.status == auto_approved` and `payment` created with `paid` status (mock)
* **Acceptance tests:** success log + generated approval letter stored.

**VAL-02 — Run end-to-end scenario: suspicious claim (flag + adjuster override)**

* **Start:** FRAUD rules present
* **End:** process a high-risk synthetic claim and assert it lands in adjuster queue; simulate adjuster override; final status reflects override
* **Acceptance tests:** queue shows claim; override action updates settlement and audit trail.

**VAL-03 — Automation % & latency measurement**

* **Start:** run a batch of 100 synthetic claims
* **End:** compute `automation% = auto_approved / total` and average processing time; store result in analytics table
* **Acceptance tests:** a report CSV exists with those numbers.

---

## Notes & final pointers

* **Keep tasks tiny.** If a task still feels complex, split it into smaller tasks (e.g., “implement DB model” → “create migration” + “create ORM model” + “write CRUD tests”).
* **Policy mapping is manual.** The POL-MAP tasks are intentionally human-assisted — each clause must be read and encoded. If you want the engineering LLM to extract text from PDFs and propose mappings automatically, add a task like `POL-AUTO-EXTRACT-1`.
* **Security & legal sign-offs required before production.** We included pseudonymization + retention tasks, but you’ll need legal review for health data (GDPR).
* **Priorities for MVP:** get the intake→OCR→extraction→rule evaluation→settlement→letter loop working for a small subset of policy rules; implement fraud rules as rule-based first, ML second.

---
