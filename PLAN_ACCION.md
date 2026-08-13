# Plan de Acción — TFM: Análisis de Sentimiento y Tendencias en Campañas Electorales

> Objetivo: Matrícula de Honor — decisiones bien argumentadas, reproducibles y comparadas con SOTA.

---

## Estado actual

| Capítulo | Estado |
|----------|--------|
| 1 - Introducción | ✅ Completo |
| 2 - Estado del arte | ✅ Completo (incluye EDA TweetEval) |
| 3 - Fundamentos teóricos | ✅ Completo |
| 4 - Metodología | ❌ Vacío |
| 5 - Análisis de resultados | ❌ Vacío |
| 6 - Conclusiones | ❌ Vacío |

**Scraper:** corriendo en background. 110 queries × 4 campañas, output a GCS `tfm-twitter-raw/`.

---

## Datos disponibles

### TweetEval (benchmark oficial)
- **Sentiment:** 59.899 tweets (train 45.615 / val 2.000 / test 12.284). Clases: neg/neutral/pos.
- **Stance:** ~4.163 tweets en 5 tópicos (abortion, atheism, climate, feminist, hillary). Clases: favor/against/neither.
- **Baselines publicados:** F1-Macro sentiment = 72.8% (RoBERTa-retrained), F1-avg stance = 69.3%.

### Datos scrapeados (propios)
- 4 campañas: `españa_2023`, `trump_2024`, `trump_2016`, `brexit_2016`
- Tareas: sentiment queries + stance queries por candidato/target
- Almacenamiento: GCS bucket `tfm-twitter-raw/`

---

## Fase 0 — Preparación del entorno (inmediata, mientras corre scraper)

```bash
pip install datasets transformers torch scikit-learn evaluate
pip install pyLDAvis gensim  # para LDA (opcional)
```

Descargar TweetEval vía HuggingFace:
```python
from datasets import load_dataset
sentiment = load_dataset("tweet_eval", "sentiment")
stance_abortion = load_dataset("tweet_eval", "stance_abortion")
# etc.
```

---

## Fase 1 — Preprocesamiento (`notebooks/01_preprocessing.ipynb`)

### Decisión metodológica: dos variantes

| Variante | Descripción | Uso |
|----------|-------------|-----|
| **A — BERTweet-style** | `@usuario → @USER`, `URL → HTTPURL`, mantener hashtags y emojis | Fine-tuning transformers |
| **B — Limpia** | + lowercase, eliminar stopwords, quitar puntuación | Solo LDA |

### Acciones específicas
- Quitar `#semst` del dataset stance de TweetEval (artefacto de recolección SemEval-2016, contaminante)
- Para datos propios: mismo pipeline Variante A
- Justificación: Barbieri et al. (2020) establece este preprocesamiento como estándar TweetEval

---

## Fase 2 — Benchmark Sentimiento en TweetEval (`notebooks/02_sentiment_tweeteval.ipynb`)

### Modelos a comparar

| Modelo | HuggingFace ID | Referencia |
|--------|---------------|-----------|
| twitter-roberta-base-sentiment | `cardiffnlp/twitter-roberta-base-sentiment-latest` | Barbieri et al., 2020 |
| BERTweet-base | `vinai/bertweet-base` | Nguyen et al., 2020 |
| RoBERTa-base (genérico) | `roberta-base` | Liu et al., 2019 |
| BERT-base (baseline débil) | `bert-base-uncased` | Devlin et al., 2019 |

### Protocolo experimental
- Fine-tuning en TweetEval train, early stopping en val (F1-Macro)
- Evaluación en test set oficial con `evaluation_script.py` de TweetEval
- Hiperparámetros estándar: lr=2e-5, batch=32, epochs=3-5, seed fijo (42)
- Métrica principal: **F1-Macro** (estándar TweetEval)
- Target: igualar o superar 72.8%

---

## Fase 3 — ⚠️ DECISIÓN CRÍTICA: Idioma para campaña española

El TweetEval sentiment está en **inglés**. Los tweets de `españa_2023` son en **español**.

### Solución adoptada
Añadir modelo español/multilingüe al pipeline:

| Modelo | ID | Ventaja |
|--------|-----|---------|
| **RoBERTuito** (recomendado) | `pysentimiento/robertuito-sentiment-analysis` | Fine-tuneado específicamente en Twitter español, SOTA |
| Twitter-XLM-RoBERTa | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | Multilingüe, permite comparación directa entre campañas |

**Decisión para el TFM:** usar `cardiffnlp/twitter-xlm-roberta-base-sentiment` en todas las campañas para permitir **comparación directa cross-campaign** (mismo espacio de representación). RoBERTuito como validación adicional en campaña española.

Esto debe documentarse en Cap 4 como decisión metodológica argumentada.

---

## Fase 4 — Aplicar a datos scrapeados (`notebooks/03_sentiment_scraped.ipynb`)

1. Cargar JSONs desde GCS → DataFrame unificado con columna `campaign`
2. Inferencia con modelo ganador (sin fine-tuning adicional — zero-shot transfer)
3. **Análisis temporal:** evolución del sentimiento por semana dentro de cada campaña
4. **Comparativa cross-campaign:**
   - Distribución pos/neg/neutral por campaña
   - Pico de negatividad vs. eventos clave (debate, escándalo, resultado)
5. Visualizaciones para Cap 5: series temporales, violin plots, heatmaps

---

## Fase 5 — Benchmark Stance en TweetEval (`notebooks/04_stance_tweeteval.ipynb`)

### Protocolo
- Fine-tune por tópico (5 modelos independientes) y modelo multi-tópico
- **Problema val pequeño (40-70 muestras):** combinar train+val, validación cruzada 5-fold
- Quitar `#semst` antes de tokenizar
- Métrica: **F1-avg** = (F1_favor + F1_against) / 2 — excluye "neither" (Mohammad et al., 2016)

---

## Fase 6 — Stance en datos scrapeados (`notebooks/05_stance_scraped.ipynb`)

### Tres enfoques ordenados por robustez

| Enfoque | Descripción | Pros | Contras |
|---------|-------------|------|---------|
| **A — Zero-shot NLI** (principal) | Reformular stance como entailment: "Este tweet apoya a Trump" | Sin datos anotados propios | Menor F1 que fine-tuning |
| **B — Transfer TweetEval** (baseline) | Aplicar modelo entrenado en TweetEval stance | Rápido | Domain shift severo |
| **C — Anotación manual** (opcional) | 200-500 tweets anotados → fine-tuning | Más preciso | Costoso en tiempo |

**Modelos NLI candidatos:**
- `cross-encoder/nli-deberta-v3-small`
- `facebook/bart-large-mnli`

**Targets por campaña:**
- Brexit 2016: Leave vs. Remain
- Trump 2016: Trump vs. Clinton
- Trump 2024: Trump vs. Harris
- España 2023: PSOE-Sánchez / PP-Feijóo / Vox-Abascal

---

## Fase 7 — LDA (opcional, `notebooks/06_lda_topics.ipynb`)

Solo si queda tiempo. Tweet pooling por campaña para compensar brevedad de tweets. Coherence score (c_v) para seleccionar K. Visualización con pyLDAvis. Documentar en Cap 4 como análisis exploratorio complementario.

---

## Fase 8 — Escritura Cap 4, 5, 6

### Cap 4 — Metodología (estructura propuesta)
1. Estrategia de recolección de datos (scraper + TweetEval)
2. Preprocesamiento
3. Modelos seleccionados y justificación
4. Protocolo de evaluación y métricas
5. Experimentos diseñados

### Cap 5 — Análisis de resultados
- Tabla comparativa F1-Macro por modelo (sentiment benchmark)
- Tabla F1-avg por tópico (stance benchmark)
- Análisis temporal sentimiento por campaña
- Distribución de stance por target/campaña
- Comparativa cross-campaign

### Cap 6 — Conclusiones
- Qué modelo gana y por qué
- Qué campaña es más polarizada/negativa
- Limitaciones: sesgo demográfico Twitter, restricciones de scraping, domain gap TweetEval→campañas reales, ausencia de anotación ground truth propia
- Trabajo futuro: datos multimodales, detección bots, análisis de influencers

---

## Notebooks — orden de ejecución

```
notebooks/
  01_preprocessing.ipynb          # Preprocesamiento TweetEval + datos propios
  02_sentiment_tweeteval.ipynb    # Benchmark 4 modelos en TweetEval sentiment
  03_sentiment_scraped.ipynb      # Inferencia + análisis temporal en datos propios
  04_stance_tweeteval.ipynb       # Benchmark stance en TweetEval
  05_stance_scraped.ipynb         # Zero-shot NLI stance en datos propios
  06_lda_topics.ipynb             # (Opcional) LDA por campaña
  07_results_analysis.ipynb       # Figuras y tablas finales para el TFM
```

---

## Decisiones clave consolidadas (para argumentar en el TFM)

| Decisión | Elección | Justificación |
|----------|----------|---------------|
| Benchmark de evaluación | TweetEval | Estándar de facto en la comunidad (Barbieri et al., 2020) |
| Métrica sentimiento | F1-Macro | Trata clases desbalanceadas equitativamente |
| Métrica stance | F1-avg (favor+against) | Excluye "neither", foco en posicionamiento real (Mohammad et al., 2016) |
| Preprocesamiento | BERTweet-style (A) | Óptimo para modelos Twitter-específicos (Nguyen et al., 2020) |
| Modelo cross-campaign | twitter-xlm-roberta | Permite comparación directa entre idiomas/campañas |
| Stance scraped | Zero-shot NLI | No requiere anotación propia, reproducible, argumentable académicamente |
| Seed fijo | 42 | Reproducibilidad (estándar en NLP) |
| Val set stance | k-fold 5 | Val muy pequeño (40-70 muestras), evita alta varianza en métricas |
