# Parameter Golf - Facundo

Repositorio para el challenge de OpenAI Parameter Golf.

## Objetivo
Entrenar un modelo de lenguaje que:
- tenga el menor `val_bpb`
- pese menos de 16MB comprimido

## Setup

```bash
git clone https://github.com/openai/parameter-golf.git
cd parameter-golf
```

## Flujo de trabajo

1. Correr baseline
2. Ajustar hiperparámetros
3. Medir val_bpb
4. Iterar

## Estructura

- experiments/: configuraciones y notas
- scripts/: helpers de ejecución
- src/: modificaciones al modelo

## Próximos pasos

- [ ] correr baseline
- [ ] loggear métricas
- [ ] probar tuning inicial
