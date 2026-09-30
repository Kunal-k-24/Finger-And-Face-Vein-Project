# Privacy-Preserving Multibiometric Authentication System

A production-grade full-stack biometric authentication system combining **face recognition** and **finger vein recognition** with **homomorphic encryption**, **differential privacy**, and **federated learning**.

```
┌─────────────────────────────────────────────────────────┐
│  React 18 + Vite + TypeScript + TailwindCSS (Port 3000) │
└─────────────────────┬───────────────────────────────────┘
                      │ REST + WebSocket
┌─────────────────────▼───────────────────────────────────┐
│       FastAPI + Uvicorn (Port 8000)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  MTCNN   │ │FingerVein│ │ResNet-18 │ │  TenSEAL  │  │
│  │  Face    │ │Syn-5M    │ │Feature   │ │  CKKS HE  │  │
│  │  Prepro  │ │Prepro    │ │Extractor │ │  Encrypt  │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────────────────────────────────┐  │
│  │  Opacus  │ │   Flower FL Server (Port 8080)        │  │
│  │  DP-SGD  │ │   FedAvg + DP-SGD clients             │  │
│  └──────────┘ └──────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
PostgreSQL 15    Redis 7       MinIO
(Templates)    (Cache/JWT)   (Blob Store)
```

---

## Quick Start

### Prerequisites

- Docker 24+ and Docker Compose v2
- 8 GB RAM recommended (PyTorch + TenSEAL are memory-intensive)

### 1. Clone and configure

```bash
git clone <repo>
cd biometric-auth
cp .env.example .env
# Edit .env — change JWT_SECRET_KEY at minimum
```

### 2. Start all services

```bash
docker-compose up --build
```

On first startup Docker will:
1. Pull base images (postgres, redis, minio)
2. Build the Python backend (installs PyTorch, TenSEAL, Opacus, Flower)
3. Build the React frontend
4. Run Alembic migrations (`alembic upgrade head`)
5. Start all services

### 3. Open the application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API Docs** (Swagger) | http://localhost:8000/docs |
| **API Docs** (ReDoc) | http://localhost:8000/redoc |
| **MinIO Console** | http://localhost:9001 |
| **FL Server** | localhost:8080 (gRPC) |

### 4. First-time setup

1. Navigate to http://localhost:3000 — you'll be redirected to `/login`
2. Click **Register** and create an account
3. Go to **Enroll**: capture your face via webcam and upload a finger vein image
4. Go to **Verify**: repeat the biometric capture — the system accepts/rejects based on cosine similarity ≥ 0.75

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@postgres:5432/biometric_db` | Async PostgreSQL URL |
| `REDIS_URL` | `redis://:redispassword@redis:6379/0` | Redis connection URL |
| `MINIO_ENDPOINT` | `minio:9000` | MinIO S3-compatible endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `MINIO_BUCKET` | `biometric-templates` | Bucket for blob storage |
| `JWT_SECRET_KEY` | `change-me-in-production` | **Change this in production** |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_EXPIRE_MINUTES` | `30` | Access token TTL |
| `JWT_REFRESH_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `HE_POLY_MODULUS_DEGREE` | `8192` | CKKS polynomial modulus degree |
| `DP_TARGET_EPSILON` | `3.0` | Differential privacy budget ε |
| `DP_TARGET_DELTA` | `1e-5` | DP failure probability δ |
| `DP_MAX_GRAD_NORM` | `1.0` | Per-sample gradient clip norm |
| `FL_SERVER_ADDRESS` | `fl-server:8080` | Flower gRPC server address |
| `FL_NUM_ROUNDS` | `10` | Default federated learning rounds |
| `SIMILARITY_THRESHOLD` | `0.75` | Cosine similarity acceptance threshold |
| `REDIS_PASSWORD` | `redispassword` | Redis AUTH password |
| `POSTGRES_DB` | `biometric_db` | PostgreSQL database name |
| `POSTGRES_USER` | `user` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `pass` | PostgreSQL password |

---

## API Endpoint Reference

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/register` | — | Create new user |
| `POST` | `/auth/login` | — | Login → JWT access + refresh tokens |
| `POST` | `/auth/refresh` | — | Refresh access token |
| `GET` | `/auth/me` | Bearer | Current user info |

**Login request:**
```json
{ "username": "alice", "password": "secret123" }
```
**Login response:**
```json
{ "access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer" }
```

### Biometric

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/enroll` | Bearer | Enroll face + vein (multipart) |
| `POST` | `/verify` | Bearer | Verify identity (multipart) |

**Enroll multipart fields:**
- `face_image` (file) — JPEG/PNG webcam face capture
- `vein_image` (file) — JPEG/PNG near-infrared finger vein
- `vein_xml` (file, optional) — FingerVeinSyn-5M XML annotation

**Verify response:**
```json
{
  "decision": "accept",
  "similarity_score": 0.9341,
  "threshold": 0.75,
  "latency_ms": 142
}
```

### Admin (admin role required)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/admin/users?page=1&page_size=20` | Paginated user list |
| `GET` | `/admin/logs?result=accept&page=1` | Filterable auth logs |
| `GET` | `/admin/metrics` | Aggregate stats (FAR, FRR, acceptance rate) |

### Federated Learning

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/federated/status` | — | All completed FL rounds |
| `POST` | `/federated/start?num_rounds=10` | Admin | Start FL training (async) |
| `WS` | `/federated/ws/federated` | — | Live round progress stream |

**WebSocket message format:**
```json
{ "round": 3, "accuracy": 0.847, "epsilon": 2.91 }
```

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Component health check |

```json
{ "status": "ok", "db": "ok", "redis": "ok", "minio": "ok" }
```

---

## How It Works

### Face Preprocessing Pipeline (7 Stages)

Implemented in `backend/services/preprocessing/face_preprocessor.py`.

```
Input BGR image
       │
  Stage 1: MTCNN detection
       │  → highest-confidence bounding box + 5 landmarks
       │    (left eye, right eye, nose, left mouth, right mouth)
       │
  Stage 2: Affine alignment
       │  → cv2.estimateAffinePartial2D maps landmarks to canonical
       │    reference positions (ArcFace 112×112 coordinate system)
       │
  Stage 3: BGR → YCbCr, extract luminance Y, resize to 128×128
       │  → discards colour variation from lighting conditions
       │
  Stage 4: CLAHE (clipLimit=3.0, tileGridSize=8×8)
       │  → local contrast enhancement of facial structure
       │
  Stage 5: Gaussian noise σ=5.0 (training only)
       │  → simulates sensor noise for robustness
       │
  Stage 6: Augmentation (training only)
       │  → horizontal flip p=0.5, rotation ±15°,
       │    brightness/contrast ±20%, random erasing p=0.2
       │
  Stage 7: Normalise → (3, 128, 128) tensor
           → replicate single channel × 3, apply ImageNet stats
             mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]
```

### Finger Vein Preprocessing Pipeline — FingerVeinSyn-5M (6 Stages)

Implemented in `backend/services/preprocessing/vein_preprocessor.py`.

The FingerVeinSyn-5M dataset defines 8 intra-class variation types captured in XML annotations. This pipeline faithfully implements the paper's preprocessing protocol.

```
Input grayscale vein image + optional XML annotation
       │
  Stage 1: XML annotation parsing (if available)
       │  → extract bbox (cx,cy,w,h), 4 anatomical landmarks
       │    [root, proximal_joint, distal_joint, tip]
       │  → parse 8 intra-variation flags:
       │    IsRotate, IsShift, IsRoll, IsScale, IsExposure,
       │    IsMotionBlur, IsOpticalBlur, IsSkinScatter
       │
  Stage 2: ROI extraction
       │  → crop to bbox + 10px margin on all sides
       │  → resize to 128×128 (cv2.INTER_CUBIC)
       │
  Stage 3: Geometric normalisation (if landmarks available)
       │  → cv2.getAffineTransform aligns 4 anatomical landmarks
       │    to canonical reference positions on 128×128 template
       │  → cv2.warpAffine with BORDER_REFLECT_101 padding
       │
  Stage 4: Photometric normalisation (always applied)
       │  → percentile rescaling: clip to [p1, p99], rescale to [0,255]
       │  → CLAHE (clipLimit=2.0, tileGridSize=8×8)
       │
  Stage 5: Intra-variation augmentation (training only, if XML present)
       │  → IsShift:       random translation ±20px
       │  → IsRotate:      rotation ±20° around centre
       │  → IsScale:       uniform scale ±15%, centre-crop to 128×128
       │  → IsRoll:        in-plane roll correction
       │  → IsExposure:    gamma adjustment γ ∈ [0.5, 2.0]
       │  → IsMotionBlur:  linear motion kernel 5–15px at random angle
       │  → IsOpticalBlur: Gaussian blur σ ∈ [0.5, 2.0]
       │  → IsSkinScatter: multiplicative low-frequency noise
       │
  Stage 6: Normalise → (1, 128, 128) tensor
           → (pixel / 255.0 − 0.5) / 0.5  maps [0,255] → [−1,+1]
```

### Feature Extraction + Fusion

```
face_tensor (3,128,128)  →  ResNet-18 (3ch)  →  128-d L2-normalised embedding
vein_tensor (1,128,128)  →  ResNet-18 (1ch)  →  128-d L2-normalised embedding
                                                          │
                                                   concatenate
                                                          │
                                                   256-d fused vector
                                                          │
                                                   L2 normalise
                                                          │
                                                   256-d fused embedding
```

The two ResNet-18 instances share the same architecture but have independent weights. The first conv layer is adapted: face encoder uses 3-channel input; vein encoder uses 1-channel input with weights initialised by averaging the pretrained RGB channels.

### Homomorphic Encryption (TenSEAL CKKS)

All three biometric vectors (face 128-d, vein 128-d, fused 256-d) are independently encrypted with CKKS before database storage:

```
Parameters:
  scheme:                CKKS
  poly_modulus_degree:   8192  (128-bit security)
  coeff_mod_bit_sizes:   [60, 40, 40, 60]  (200-bit total)
  global_scale:          2^40

Key material:
  Public context  → shared / stored in HEService
  Secret key      → serialised separately (never leaves the server)
  Relinearisation keys → for ciphertext multiplication
  Galois keys     → for rotation operations
```

> **Note:** Full ciphertext-domain cosine similarity requires OpenFHE or Microsoft SEAL (dot product over encrypted vectors without decryption). This prototype decrypts both vectors server-side for the similarity computation and includes a `TODO` comment marking the upgrade point.

### Differential Privacy (Opacus)

During federated learning, each client's local training is wrapped with Opacus DP-SGD:

```
Target ε = 3.0  (strong privacy guarantee)
Target δ = 1e-5  (≈ 1/dataset_size)
max_grad_norm = 1.0  (per-sample gradient clipping)

Opacus automatically computes the noise multiplier σ such that
after `epochs` of training the privacy budget is not exceeded.
```

### Federated Learning (Flower)

```
Server (Port 8080):
  Strategy: FedAvg
    fraction_fit = 0.5        (50% of clients per round)
    min_fit_clients = 2       (minimum clients to start round)
    evaluate_metrics: weighted accuracy average

Client:
  BiometricFLClient(NumPyClient)
    fit():      local DP-SGD training for local_epochs
    evaluate(): validation loss + accuracy
    Communicates weight deltas only (raw data never leaves client)

Round logging:
  Each completed round → federated_rounds DB table
  WebSocket /ws/federated streams live: {round, accuracy, epsilon}
```

---

## Database Schema

```sql
users                    -- User accounts + roles
biometric_templates      -- CKKS-encrypted face/vein/fused vectors
auth_logs                -- Every enroll/verify attempt with latency
federated_rounds         -- FL training history (accuracy, ε per round)
```

---

## Running Tests

```bash
# From the backend directory (or inside the container)
cd backend
pip install -r requirements.txt
pytest ../tests/ -v

# Run a specific test file
pytest ../tests/test_encryption.py -v
pytest ../tests/test_preprocessing.py -v
pytest ../tests/test_auth_flow.py -v
pytest ../tests/test_federated.py -v
```

Tests use mocked DB sessions and feature extractors — no GPU or live services required.

---

## Project Structure

```
biometric-auth/
├── docker-compose.yml              # All 6 services
├── .env.example                    # Environment variable template
│
├── backend/
│   ├── main.py                     # FastAPI app + router registration
│   ├── config.py                   # pydantic-settings configuration
│   ├── database.py                 # Async SQLAlchemy engine + session
│   ├── alembic.ini                 # Alembic migration config
│   ├── models/                     # SQLAlchemy ORM models
│   ├── schemas/                    # Pydantic request/response schemas
│   ├── routers/                    # FastAPI route handlers
│   │   ├── auth.py                 # /auth/*
│   │   ├── enroll.py               # /enroll
│   │   ├── verify.py               # /verify
│   │   ├── federated.py            # /federated/* + /ws/federated
│   │   ├── admin.py                # /admin/*
│   │   └── health.py               # /health
│   ├── services/
│   │   ├── preprocessing/
│   │   │   ├── face_preprocessor.py   # 7-stage MTCNN pipeline
│   │   │   └── vein_preprocessor.py   # 6-stage FingerVeinSyn-5M pipeline
│   │   ├── feature_extractor.py    # Dual ResNet-18 encoders
│   │   ├── fusion.py               # Concatenation + L2 normalisation
│   │   ├── encryption.py           # TenSEAL CKKS encrypt/decrypt
│   │   ├── differential_privacy.py # Opacus DP-SGD engine
│   │   ├── federated_server.py     # Flower FedAvg server
│   │   ├── federated_client.py     # Flower NumPyClient
│   │   └── authentication.py      # End-to-end enroll/verify orchestrator
│   ├── ml/
│   │   └── models/
│   │       └── resnet18_biometric.py  # Custom ResNet-18 (1ch/3ch, 128-d output)
│   └── utils/
│       ├── minio_client.py
│       ├── redis_client.py
│       └── logger.py
│
├── frontend/
│   └── src/
│       ├── App.tsx                 # Router + auth guard + nav shell
│       ├── pages/                  # LoginPage, RegisterPage, EnrollPage,
│       │                           # VerifyPage, AdminPage
│       ├── components/             # CameraCapture, FingerVeinUpload,
│       │                           # AuthResult, FederatedStatus, BiometricChart
│       ├── hooks/                  # useCamera, useWebSocket
│       ├── api/client.ts           # Axios instance + all API calls
│       └── types/index.ts          # TypeScript interfaces
│
├── migrations/
│   ├── env.py                      # Alembic async env
│   └── versions/0001_initial.py    # All four tables
│
└── tests/
    ├── test_preprocessing.py       # Face + vein pipeline shape/contrast tests
    ├── test_encryption.py          # CKKS roundtrip + cosine similarity tests
    ├── test_auth_flow.py           # Enroll/verify accept/reject tests
    └── test_federated.py           # FL client fit/evaluate + FedAvg tests
```

---

## Security Considerations

- **JWT tokens** are stored in memory only — never in `localStorage` or cookies accessible to JavaScript
- **Biometric vectors** are CKKS-encrypted before any database write — plaintext vectors never persist
- **Differential privacy** (ε=3.0, δ=1e-5) protects training data in federated rounds
- **Federated learning** ensures raw biometric images never leave the client node
- **Passwords** are hashed with bcrypt (cost factor 12)
- **Production checklist**: rotate `JWT_SECRET_KEY`, use TLS termination (nginx/Caddy), restrict MinIO to internal network, run behind a WAF

---

## Extending the System

**Add a new biometric modality** (e.g., iris):
1. Create `services/preprocessing/iris_preprocessor.py`
2. Add `iris_encoder` to `FeatureExtractor`
3. Extend `FeatureFusion.fuse()` to accept a third vector
4. Add `iris_template_blob` column via a new Alembic migration
5. Update `AuthenticationService.enroll()` and `verify()`

**Use real pretrained weights**:
Place `face_encoder.pth` and `vein_encoder.pth` in `backend/ml/weights/`. The `FeatureExtractor` automatically loads them on startup.

**Production HE upgrade**:
Replace the `cosine_similarity_encrypted` method in `encryption.py` with a full ciphertext-domain dot product using Microsoft SEAL or OpenFHE (see `TODO` comment in that method).
