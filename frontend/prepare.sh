#/bin/sh

mkdir node_modules/pyright/dist/typeshed-fallback/stdlib/proxy

mv proxy_library/proxy_pyparser* node_modules/pyright/dist/typeshed-fallback/stdlib/proxy

echo $(cat proxy_library/to_append.py) >> node_modules/pyright/dist/typeshed-fallback/stdlib/builtins.pyi


