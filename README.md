# tictoc

`tictoc` aiuta a misurare il tempo di esecuzione di un programma Python, stimare
quanto manca alla fine di un ciclo, leggere velocita di elaborazione e scrivere
log di avanzamento gia formattati.

La classe principale e `TicToc`: appena viene creata inizia a contare.

```python
from tictoc import TicToc

timer = TicToc()

# codice da misurare

print(timer.toc())
```

Output leggibile, per esempio:

```text
00:01:12
```

## Installazione

Da PyPI, quando il pacchetto e pubblicato:

```bash
python -m pip install tictoc
```

Da una release GitHub:

```bash
python -m pip install "https://github.com/<owner>/<repo>/releases/download/v0.1.0/tictoc-0.1.0-py3-none-any.whl"
```

Da sorgente locale:

```bash
python -m pip install -e .
```

Per riconoscere formati data molto liberi, installa anche il parser opzionale:

```bash
python -m pip install "tictoc[dateutil]"
```

## Uso Rapido

### Misurare il tempo trascorso

```python
from tictoc import TicToc

tt = TicToc()

# lavoro...

elapsed = tt.toc()
print(elapsed)          # valore umanizzato
print(elapsed.seconds)  # secondi totali
```

`toc()` e un alias di `elapsed_time()`.

```python
tt.elapsed_time()
tt.elapsed_origin_time()
```

`elapsed_time()` misura dal tic piu recente.  
`elapsed_origin_time()` misura dalla creazione del timer.

### Resettare il timer

`tic()` resetta l'inizio del conteggio e restituisce lo stesso oggetto, quindi
puo essere usato in method chaining.

```python
tt = TicToc()

tt.tic().info("riparto da zero")
```

### Timer con nome

Un oggetto `TicToc` puo gestire piu misure indipendenti.

```python
tt = TicToc()

tt.tic("download")
# scaricamento...

tt.tic("parse")
# parsing...

print(tt.toc("download"))
print(tt.toc("parse"))
```

Puoi anche accedere al timer named:

```python
download_timer = tt["download"]
print(download_timer.elapsed_time())
```

## Avanzamento, ETA e Velocita

Quando conosci il numero totale di step, `TicToc` puo stimare tempo residuo,
tempo totale, ora di fine e velocita.

```python
from tictoc import TicToc

tt = TicToc(total=100)

for i in range(1, 101):
    # elabora uno step
    if i % 10 == 0:
        print(
            i,
            tt.elapsed_time(),
            tt.remaining_time(i=i),
            tt.total_time(i=i),
            tt.end_time(i=i),
            tt.speed(i=i),
        )
```

Metodi utili:

- `remaining_time(i=..., total=...)`: stima il tempo mancante.
- `total_time(i=..., total=...)`: stima il tempo totale.
- `end_time(i=..., total=...)`: stima l'istante di fine.
- `speed(i=...)`: restituisce una `TicTocSpeed`.
- `percent(i=..., total=...)`: percentuale di completamento.

### Metodi di stima

Puoi scegliere come stimare il tempo residuo con `method`.

```python
tt.remaining_time(i=i, total=100, method="origin")
tt.remaining_time(i=i, total=100, method="last")
tt.remaining_time(i=i, total=100, method="moving", n=5)
tt.remaining_time(i=i, total=100, method="ema", n=5)
```

- `origin`: usa la media dall'ultimo `tic`.
- `last`: usa l'ultimo intervallo tra due aggiornamenti.
- `moving`: usa la media degli ultimi `n` aggiornamenti.
- `ema`: usa una media mobile esponenziale.

## Logging Integrato

`TicToc` funziona anche come logger. Se non passi un logger, usa un logger
interno chiamato `tictoc`.

```python
import logging
from tictoc import TicToc

logging.basicConfig(level=logging.INFO)

tt = TicToc(total=50)

for i in range(1, 51):
    # lavoro...
    tt.info("{i}/{tot} elapsed={et} eta={rt} speed={v}", i=i, each=10)
```

`each=10` scrive il log solo ogni 10 step.

Sono disponibili i metodi:

```python
tt.debug("...")
tt.info("...")
tt.warning("...")
tt.error("...")
tt.exception("...")
```

### Placeholder per i log

Nei messaggi puoi usare placeholder rapidi.

| Placeholder | Significato |
| --- | --- |
| `{i}` o `{counter}` | step corrente |
| `{tot}` o `{total}` | totale step |
| `{percent_str}` | percentuale formattata |
| `{et}` | elapsed time |
| `{eot}` | elapsed origin time |
| `{rt}` | remaining time |
| `{tt}` | total time stimato |
| `{v}` | velocita |
| `{start}` | istante di start |
| `{origin}` | istante di creazione |
| `{end}` | istante stimato di fine |

Per ottenere valori numerici usa i suffissi:

```python
tt.info("elapsed={et_s:.2f}s eta={rt_m:.1f}min speed={v_h:.0f}/h", i=i)
```

Suffissi comuni:

- `_s`, `_sec`, `_seconds`
- `_m`, `_min`, `_minutes`
- `_h`, `_hours`
- `_d`, `_days`
- `_str`

## Intervalli: TicTocInterval

`TicTocInterval` rappresenta una durata.

```python
from datetime import timedelta
from tictoc import TicTocInterval

a = TicTocInterval("1 day 2 hours")
b = TicTocInterval(timedelta(minutes=30))
c = TicTocInterval(10)  # secondi

print(a + b)
print(c * 3)
print(float(a))         # secondi totali
print(a.total_hours)
print(a.component_days)
```

Formati accettati:

```python
TicTocInterval("1 day 2 seconds")
TicTocInterval("1d 2h 3m 4s")
TicTocInterval("01:02:03")
TicTocInterval("1.02:00:53")
TicTocInterval("PT1H30M")
```

## Istanti: TicTocTime

`TicTocTime` rappresenta un istante temporale.

```python
from datetime import datetime, timedelta
from tictoc import TicTocTime

now = TicTocTime.now()
start = TicTocTime.from_string("2026-06-16 12:00:00")
later = start + timedelta(minutes=10)

print(now)
print(later - start)  # TicTocInterval
print(start.year, start.month, start.day)
print(float(start))   # Unix timestamp
```

Puoi creare un `TicTocTime` da:

```python
TicTocTime.now()
TicTocTime.from_timestamp(1_781_600_000)
TicTocTime.from_datetime(datetime.now())
TicTocTime.from_string("2026-06-16 12:00:00")
```

## Velocita: TicTocSpeed

`TicTocSpeed` rappresenta step al secondo, con conversioni pronte.

```python
from tictoc import TicTocSpeed, TicTocInterval

speed = TicTocSpeed.from_steps(120, TicTocInterval.from_minutes(2))

print(speed)                  # 1 step/s
print(speed.steps_per_second)
print(speed.steps_per_minute)
print(speed.steps_per_hour)
```

## Esempio Completo

```python
import logging
import time

from tictoc import TicToc

logging.basicConfig(level=logging.INFO, format="%(message)s")

tt = TicToc(total=20)

for i in range(1, 21):
    time.sleep(0.1)
    tt.info(
        "{i}/{tot} ({percent_str}) elapsed={et} eta={rt} end={end} speed={v}",
        i=i,
        each=5,
    )

print("finito in", tt.elapsed_time())
```

Esempio di output:

```text
5/20 (25.0%) elapsed=0.501 s eta=1.5 s end=2026-06-16 12:00:03 speed=10 steps/s
10/20 (50.0%) elapsed=1 s eta=1 s end=2026-06-16 12:00:03 speed=10 steps/s
15/20 (75.0%) elapsed=1.5 s eta=0.5 s end=2026-06-16 12:00:03 speed=10 steps/s
20/20 (100.0%) elapsed=2 s eta=0 s end=2026-06-16 12:00:03 speed=10 steps/s
finito in 2 s
```
