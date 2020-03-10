## Developer Resources

### Static checking
`log-visualizer.py` is newer code that was written with mypy static type annotations, and if you have mypy installed (can be done via `pip`) you can typecheck the code using: 
```
dmypy run -- --follow-imports=error --disallow-untyped-defs --disallow-incomplete-defs --check-untyped-defs -p log-visualizer
```
